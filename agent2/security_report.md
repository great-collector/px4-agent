# PX4 Modules 安全缺陷静态检测报告

> **检测日期**: 2025年  
> **检测对象**: PX4-Autopilot/src/modules  
> **检测工具**: 人工代码审计 + Flawfinder扫描尝试  
> **严重程度分级**: 🔴 **高危** | 🟠 **中危** | 🟡 **低危**

---

## 1. mavlink 模块

### 1.1 【🟠 中危】MAVLink FTP — 目录遍历漏洞 (Path Traversal)

**文件路径**: `src/modules/mavlink/mavlink_ftp.cpp`

**漏洞描述**:

在 `_workList`, `_workOpen`, `_workRead`, `_workWrite`, `_workRemoveFile`, `_workRename`, `_workCreateDirectory`, `_workRemoveDirectory`, `_workCalcFileCRC32` 等函数中，接收到的文件路径直接拼接至 `_root_dir` 后，虽然使用了 `strncpy` 限制长度，但**未对路径中的 `../` 目录穿越字符进行过滤**。

例如 `_workOpen` 函数中：

```cpp
strncpy(_work_buffer1, _root_dir, _work_buffer1_len);
strncpy(_work_buffer1 + _root_dir_len, _data_as_cstring(payload), _work_buffer1_len - _root_dir_len);
```

攻击者可以通过 MAVLink FTP 协议，在路径中注入 `../` 序列来读取或写入飞控文件系统上任意位置的文件（包括系统配置文件、固件等），导致严重的安全风险。

**受影响函数**:
- `_workList`
- `_workOpen` (支持 O_RDONLY / O_CREAT / O_WRONLY)
- `_workRead`
- `_workWrite`
- `_workRemoveFile`
- `_workRename`
- `_workCreateDirectory`
- `_workRemoveDirectory`
- `_workCalcFileCRC32`
- `_workTruncateFile`

**建议修复**:
- 在拼接路径前，检查路径中是否包含 `../` 或 `..\\` 等目录穿越序列
- 使用 `realpath()` 规范化路径并与允许的根目录比较
- 限制文件操作仅能在白名单目录中进行

---

### 1.2 【🟠 中危】MAVLink FTP — 缓冲区溢出风险 (Buffer Overflow)

**文件路径**: `src/modules/mavlink/mavlink_ftp.cpp`

**漏洞描述**:

在 `_workList` 中，目录列表输出使用了固定大小的 `_work_buffer2` 缓冲区，但文件名长度和目录类型标识的写入未进行完全的长度边界校验：

```cpp
// 检查是否有足够空间容纳名称、目录类型标识和空终止符
if ((offset + nameLen + 2) > kMaxDataLength) {
    break;
}
// ... 之后直接使用 strcpy
strcpy((char *)&payload->data[offset], _work_buffer2);
```

虽然 offset 检查存在，但 `_work_buffer2` 的内容构建使用了 `snprintf` 和 `strncpy`，如果文件系统中有超长文件名，可能导致数据截断与预期行为不符的安全问题。

另外，`_data_as_cstring` 函数中：

```cpp
if (payload->size < kMaxDataLength) {
    payload->data[payload->size] = '\0';
} else {
    payload->data[kMaxDataLength - 1] = '\0';
}
```

这里当 `payload->size == kMaxDataLength` 时，存在**差一错误（off-by-one）**，会导致写入越界。

---

### 1.3 【🔴 高危】MAVLink Shell — 任意命令执行 (Arbitrary Command Execution)

**文件路径**: `src/modules/mavlink/mavlink_shell.cpp`

**漏洞描述**:

该模块创建了一个通过 MAVLink 访问的交互式 NuttX Shell（仅 NuttX 上启用）：

```cpp
int MavlinkShell::start()
{
    // ...
    _task = px4_task_spawn_cmd("mavlink_shell",
                                SCHED_DEFAULT,
                                SCHED_PRIORITY_DEFAULT,
                                2048,
                                &MavlinkShell::shell_start_thread,
                                nullptr);
    // ...
}

int MavlinkShell::shell_start_thread(int argc, char *argv[])
{
    dup2(1, 2); //redirect stderror to stdout
#ifdef __PX4_NUTTX
    nsh_consolemain(0, NULL);
#endif
    return 0;
}
```

**风险分析**:
- MAVLink Shell 提供了**完全的命令行访问权限**，允许攻击者执行任意系统命令
- 虽然该功能需要 MAVLink 连接，但如果系统暴露在网络中（比如通过 WiFi 模块），远程攻击者可以获取飞控的完全控制权
- 可以进行读取/修改/删除任意文件、停止/启动服务、修改系统配置等操作
- **无身份认证机制**保护此 Shell 的访问

**建议修复**:
- 增加身份认证机制（如密码验证、签名验证）
- 添加 IP 白名单限制
- 默认禁用此功能，仅通过特定编译选项启用
- 在飞行中（armed）禁用 Shell 功能

---

### 1.4 【🟠 中危】MAVLink Parameters — 缺乏参数设置验证

**文件路径**: `src/modules/mavlink/mavlink_parameters.cpp`

**漏洞描述**:

在 `handle_message` 中处理 `MAVLINK_MSG_ID_PARAM_SET` 时，直接接收地面站的参数设置请求并执行：

```cpp
case MAVLINK_MSG_ID_PARAM_SET: {
    mavlink_param_set_t set;
    mavlink_msg_param_set_decode(msg, &set);
    
    if (set.target_system == mavlink_system.sysid &&
        (set.target_component == mavlink_system.compid || set.target_component == MAV_COMP_ID_ALL)) {
        // ...
        param_set(param, &(set.param_value));
        send_param(param);
    }
}
```

**风险分析**:
- 参数设置仅通过 `target_system` 和 `target_component` 进行简单匹配，无身份验证
- 攻击者可以修改关键飞行参数（如 PID 增益、传感器校准值、安全限制等）
- 参数 `_HASH_CHECK` 可以用来停止参数发送，导致地面站无法获取参数更新
- `MAV_CMD_DO_SET_MODE` 可被滥用来切换飞行模式

**建议修复**:
- 增加写操作的身份验证机制
- 对关键安全参数（如飞行限制、安全开关等）进行二次确认
- 在飞行中限制部分危险参数的修改

---

### 1.5 【🟠 中危】MAVLink Receiver — 未经充分验证的 offboard 控制输入

**文件路径**: `src/modules/mavlink/mavlink_receiver.cpp`

**漏洞描述**:

在 `handle_message_set_position_target_local_ned` 和 `handle_message_set_position_target_global_int` 中，系统接受外部位姿/速度/加速度设定值，直接发布到 uORB 主题供控制器使用。

```cpp
if ((mavlink_system.sysid == set_position_target_local_ned.target_system ||
     set_position_target_local_ned.target_system == 0) &&
    (mavlink_system.compid == set_position_target_local_ned.target_component ||
     set_position_target_local_ned.target_component == 0) &&
    values_finite) {
    // ...
    _pos_sp_triplet_pub.publish(pos_sp_triplet);
}
```

**风险分析**:
- `target_system == 0` 被当作广播处理，任何发送者都可以控制飞行器
- 无身份认证，无加密，任何能发送 MAVLink 的设备（包括同一网络中的第三方设备）都可以接管控制
- `target_component == 0` 也接受任何组件 ID

**建议修复**:
- 移除 `target_system == 0` 的宽松匹配
- 增加飞行模式切换的安全确认
- 建议启用 MAVLink 2 的签名机制

---

### 1.6 【🟡 低危】MAVLink — RC Channels Override 无鉴权

**文件路径**: `src/modules/mavlink/mavlink_receiver.cpp`

**漏洞描述**:

`handle_message_rc_channels_override` 允许任意 MAVLink 消息源覆盖 RC 通道值，被覆盖的 RC 通道值将作为手动控制输入直接注入飞行控制系统，可用于绕过遥控器安全开关或强制进入危险飞行模式。

---

## 2. commander 模块

### 2.1 【🔴 高危】ARM_AUTH — 同步阻塞风险 (Busy-Wait/DoS)

**文件路径**: `src/modules/commander/arm_auth.cpp`

**漏洞描述**:

`_auth_method_arm_req_check` 中使用**轮询（busy-wait）**方式等待授权响应：

```cpp
while (now < auth_timeout) {
    arm_auth_update(now);
    if (state != ARM_AUTH_WAITING_AUTH && state != ARM_AUTH_WAITING_AUTH_WITH_ACK) {
        break;
    }
    /* 0.5ms */
    px4_usleep(500);
    now = hrt_absolute_time();
}
```

**风险分析**:
- 该循环在 commander 主线程中运行，会阻塞整个飞行控制状态机
- 如果在授权等待期间发生紧急情况（如电池低电量、GPS 丢失等），系统无法响应
- 可能导致在紧急情况下无法 disarm（解锁）或切换飞行模式
- 攻击者可以通过简单地不回复授权请求来造成 DoS 攻击效果

**建议修复**:
- 使用状态机 + 定时器机制代替阻塞轮询
- 增加授权超时的紧急处理逻辑
- 紧急情况（如电池临界、RC 信号丢失）应中断授权等待

---

### 2.2 【🟠 中危】Commander — 全局变量污染

**文件路径**: `src/modules/commander/Commander.cpp`

**漏洞描述**:

大量关键状态使用了**全局/静态变量**：

```cpp
static struct vehicle_status_s status = {};
static struct actuator_armed_s armed = {};
static struct safety_s safety = {};
static struct commander_state_s internal_state = {};
static manual_control_setpoint_s sp_man = {};
```

在多线程环境下（MAVLink 接收线程、命令处理线程），这些全局变量可能被并发访问，存在**竞态条件（Race Condition）**。

**风险分析**:
- 状态变量未加锁保护，多线程同时读写可能导致状态不一致
- 可能造成错误的 arm/disarm 判断、错误的模式切换
- 在极端条件下可能导致空中意外解锁或飞行中锁定

---

## 3. navigator 模块

### 3.1 【🟡 低危】Navigator — 外部命令未充分校验

**文件路径**: `src/modules/navigator/navigator_main.cpp`

**漏洞描述**:

在处理 `VEHICLE_CMD_DO_REPOSITION` 等命令时，对经纬度值的处理较为宽松：

```cpp
if (PX4_ISFINITE(cmd.param5) && PX4_ISFINITE(cmd.param6)) {
    rep->current.lat = (cmd.param5 < 1000) ? cmd.param5 : cmd.param5 / (double)1e7;
    rep->current.lon = (cmd.param6 < 1000) ? cmd.param6 : cmd.param6 / (double)1e7;
}
```

**风险分析**:
- 参数校验仅检查是否为有限值，未检查是否在合理的地理坐标范围内
- 攻击者可以设置非法坐标值，可能导致导航计算出错

---

## 4. dataman 模块

### 4.1 【🟠 中危】Dataman — 未充分验证的存储操作

**文件路径**: `src/modules/dataman/dataman.cpp`

**相关风险**:
dataman 被多个模块（mission, geofence, safepoint）用于持久化存储数据。各模块在调用 `dm_write` / `dm_read` 时，数据大小和内容的校验依赖调用方的正确性。如果某个调用方传入了越界数据，可能导致存储损坏。

---

## 5. uORB 模块

### 5.1 【🟡 低危】uORB — 发布者/订阅者无访问控制

**文件路径**: `src/modules/uORB/`

**漏洞描述**:

整个 PX4 的进程间通信机制 uORB 没有任何访问控制。任何模块都可以订阅或发布任何主题。这意味着：
- 传感器数据可以被恶意模块篡改
- 命令主题可以被第三方注入伪造命令
- 状态信息可以被读取泄露

---

## 6. 总结与建议

### 严重性汇总

| 严重程度 | 数量 | 关键影响 |
|---------|:---:|---------|
| 🔴 高危 | 2 | 任意命令执行（MAVLink Shell）、DoS/状态机阻塞（arm_auth） |
| 🟠 中危 | 5 | 目录遍历、缓冲区溢出、参数未验证、offboard无鉴权、全局变量竞态 |
| 🟡 低危 | 3 | RC Override、命令校验不足、uORB无访问控制 |

### 总体安全建议

1. **启用 MAVLink 2 签名**：所有 MAVLink 通信应启用端到端签名验证
2. **最小权限原则**：
   - 默认禁用 MAVLink Shell 和 MAVLink FTP
   - 关键操作（arm、参数修改、模式切换）增加二次确认
3. **输入验证加固**：
   - 所有外部输入路径检查目录穿越
   - 所有数值范围进行边界检查
   - 网络消息增加来源验证
4. **消除竞态条件**：对全局/静态状态变量增加互斥保护
5. **避免阻塞调用**：关键路径上的同步等待改为异步状态机

---

*本报告由 PX4 安全缺陷静态检测 Agent 生成，基于代码人工审计及静态分析工具辅助。*
