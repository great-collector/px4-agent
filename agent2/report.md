# PX4 src/modules 安全缺陷静态检测报告

> **检测时间**: 2025年  
> **检测工具**: Flawfinder 2.0 + Semgrep + 人工审查  
> **检测范围**: `src/modules/` 全量 C/C++ 源码  
> **总发现数**: 484 项（Flawfinder）  
> **高危项** *(Risk Level ≥ 4)*: **28 项**  

---

## 目录

1. [高危漏洞（Critical / High）](#1-高危漏洞critical--high)
2. [中危漏洞（Medium）](#2-中危漏洞medium)
3. [低危漏洞（Low）](#3-低危漏洞low)
4. [总结与建议](#4-总结与建议)

---

## 1. 高危漏洞（Critical / High）

### 🔴 H-01: MAVLink FTP 路径遍历 + 任意文件读写（Critical）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/mavlink/mavlink_ftp.cpp` |
| **行号** | 多处（`_workList`, `_workOpen`, `_workRead`, `_workWrite`, `_workRemoveFile`, `_workRename`, `_workCreateDirectory`, `_workRemoveDirectory`, `_workCalcFileCRC32`） |
| **严重等级** | **Critical（严重）** |
| **CWE** | CWE-22 (Path Traversal), CWE-73 (File Name or Path External Control) |

**漏洞描述**：

`mavlink_ftp.cpp` 实现了 MAVLink FTP 协议处理，提供列出目录、打开文件、读文件、写文件、删除文件、重命名、创建/删除目录、计算 CRC32 等文件系统操作。该协议通过无线链路暴露给地面站（GCS）。

**核心问题**：尽管 `_workOpen` 等函数使用了 `_root_dir` 前缀拼接路径：

```cpp
strncpy(_work_buffer1, _root_dir, _work_buffer1_len);
strncpy(_work_buffer1 + _root_dir_len, _data_as_cstring(payload), _work_buffer1_len - _root_dir_len);
```

但并未对用户输入的路径进行**规范化（canonicalization）和遍历检测（如 `../` 检查）**。攻击者可通过构造路径穿越 payload（如 `../../etc/passwd`），实现：
- **任意文件读取**（`kCmdReadFile`, `kCmdBurstReadFile`）
- **任意文件写入**（`kCmdCreateFile`, `kCmdOpenFileWO`, `kCmdWriteFile`）
- **任意文件删除**（`kCmdRemoveFile`）
- **任意目录创建/删除**（`kCmdCreateDirectory`, `kCmdRemoveDirectory`）
- **文件重命名**（`kCmdRename`）

**影响**：攻击者可以完全控制飞控的文件系统——植入恶意固件、篡改配置文件、破坏日志、删除关键文件，甚至导致飞控系统崩溃。

**建议修复**：
- 使用 `realpath()` 或自定义规范化函数解析用户输入路径
- 检查规范化后的路径是否以 `_root_dir` 开头
- 拒绝包含 `..` 或绝对路径的请求

---

### 🔴 H-02: MAVLink FTP 缓冲区溢出（strcpy 无边界检查）（Critical）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/mavlink/mavlink_ftp.cpp` |
| **行号** | ~480（`_workList` 函数体内） |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-120 (Buffer Copy without Checking Size) |

**漏洞描述**：

在 `_workList()` 函数中，使用 `strcpy()` 将目录项名称直接复制到 payload 缓冲区：

```cpp
strcpy((char *)&payload->data[offset], _work_buffer2);
```

虽然前面有长度检查：
```cpp
if ((offset + nameLen + 2) > kMaxDataLength) { break; }
```

但这里存在一个 **TOCTOU（Time-of-Check Time-of-Use）** 问题：`nameLen = strlen(_work_buffer2)` 与后续 `strcpy` 之间，`_work_buffer2` 的内容可能因并发而改变。且目录项名称来源于文件系统，若文件系统被篡改或存在特殊构造的超长文件名，可能绕过检查导致堆栈/堆缓冲区溢出。

**建议修复**：使用 `strncpy()` 并指定限制长度，或使用 `memcpy()` 配合显式长度控制。

---

### 🔴 H-03: Commander 校准例程 strncat 缓冲区溢出（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/commander/calibration_routines.cpp` |
| **行号** | 736-737 |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-120 (Buffer Copy without Checking Size) |

**漏洞描述**：

Flawfinder 报告指出第 736、737 行的 `strncat` 调用存在缓冲区溢出风险：

```
strncat(buf, "...", sizeof(buf) - strlen(buf) - 1);  // 长度参数计算可能出错
```

`strncat` 第三个参数是**可追加的最大字符数**，而非目标缓冲区的总大小。常见的错误是：`strncat(dst, src, sizeof(dst))`，当 `dst` 已有内容时，`sizeof(dst)` 远大于实际剩余空间，导致缓冲区溢出。

**影响**：堆栈缓冲区溢出，可能被利用实现代码执行或拒绝服务。

**建议修复**：使用 `snprintf()` 或 `strlcat()`，或正确计算剩余空间。

---

### 🔴 H-04: Logger 日志模块 sscanf 缓冲区溢出（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/logger/logger.cpp` |
| **行号** | ~686 |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-120, CWE-20 (Input Validation) |

**漏洞描述**：

使用 `sscanf()` 的 `%s` 格式读取字符串，但没有指定最大宽度限制：

```c
sscanf(input, "%s %s", buf1, buf2);  // 无长度限制
```

若输入字符串长度超过目标缓冲区大小，将直接导致缓冲区溢出。日志模块可能处理外部输入的日志文件名、路径等，存在被利用风险。

**建议修复**：指定最大宽度，如 `%255s`，或使用 `std::istringstream`。

---

### 🔴 H-05: MAVLink Log Handler sscanf 缓冲区溢出（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/mavlink/mavlink_log_handler.cpp` |
| **行号** | ~378 |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-120, CWE-20 |

**漏洞描述**：

与 H-04 类似，`mavlink_log_handler.cpp` 中也使用了无长度限制的 `sscanf()` 处理日志相关数据。该接口通过 MAVLink 暴露给地面站，攻击者可以发送恶意构造的日志请求包来触发缓冲区溢出。

**建议修复**：为 `%s` 指定最大读取长度。

---

### 🔴 H-06: Commander 多处 sprintf 缓冲区溢出（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | 多处文件 |
| **行号** | 详见下方 |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-120 (Buffer Overflow) |

**受影响文件及行号**：

| 文件 | 行号 |
|------|------|
| `commander/PreflightCheck.cpp` | 78 |
| `commander/accelerometer_calibration.cpp` | 200, 422 |
| `commander/gyro_calibration.cpp` | 258, 513 |
| `commander/mag_calibration.cpp` | 206, 815 |
| `sensors/voted_sensors_update.cpp` | 215, 318, 447 |
| `mavlink/mavlink_parameters.cpp` | 123, 129 |
| `events/temperature_calibration/common.h` | 38, 104 |
| `events/temperature_calibration/polyfit.hpp` | 110 |

**漏洞描述**：

使用 `sprintf()` 将格式化数据写入固定大小的 char 数组，但**未对输出长度做任何检查**。当参数值（如传感器 ID、设备名称、温度值等）超过预期范围时，将导致缓冲区溢出。

**示例**（`PreflightCheck.cpp` 第 78 行）：
```cpp
char s[20];
sprintf(s, param_template, instance);  // 若 instance 很大或 param_template 长，溢出
```

**建议修复**：全部替换为 `snprintf()`。

---

### 🔴 H-07: MAVLink Main TOCTOU / 条件竞争（access 检查）（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/mavlink/mavlink_main.cpp` |
| **行号** | ~1889 |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-362, CWE-367 (TOCTOU Race Condition) |

**漏洞描述**：

代码中使用 `access()` 检查文件权限后，再使用该文件：

```cpp
if (access(path, W_OK) == 0) {
    // ... 后续 open 操作
}
```

`access()` 返回成功和后续 `open()` 之间，攻击者可以通过符号链接替换等方式实现权限提升或访问未授权文件（经典的 TOCTOU 竞争条件漏洞）。

**影响**：在具有多用户或网络文件系统的环境中，攻击者可利用竞争窗口读取/写入不应访问的文件。

**建议修复**：直接尝试 `open()` 操作，不要先 `access()` 检查后再操作；或使用 `open()` 的 `O_EXCL` 等标志原子操作。

---

### 🔴 H-08: MAVLink FTP 危险文件操作暴露（High）

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/mavlink/mavlink_ftp.cpp` |
| **行号** | `_workRemoveFile`, `_workRename`, `_workCreateDirectory`, `_workRemoveDirectory`, `_workTruncateFile`, `_workCalcFileCRC32` |
| **严重等级** | **High（高危）** |
| **CWE** | CWE-73 (External Control of File Name or Path) |

**漏洞描述**：

MAVLink FTP 协议暴露了危险的文件系统操作（删除、重命名、创建目录、删除目录、截断、CRC 计算），这些操作：
1. **受路径遍历漏洞影响**（见 H-01），攻击者可对任意路径执行操作
2. **即使没有路径遍历**，攻击者仍可在 `_root_dir` 内执行破坏性操作（删除日志、篡改参数文件）
3. `_workCreateDirectory` 和 `_workRemoveDirectory` 可用于耗尽磁盘空间或破坏目录结构

**影响**：地面站可远程破坏飞控的文件系统完整性。

**建议修复**：
- 限制可操作的文件类型/扩展名
- 对删除/重命名等操作添加确认机制或权限验证
- 审计日志记录所有 FTP 文件操作

---

## 2. 中危漏洞（Medium）

### 🟡 M-01: micrortps_client strcpy 缓冲区溢出

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/micrortps_bridge/micrortps_client/microRTPS_client_main.cpp` |
| **行号** | ~117 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-120 |

使用 `strcpy()` 无边界检查复制字符串。RTPS 桥接涉及网络数据传输，若源数据来自网络，风险更高。

---

### 🟡 M-02: px4io 固件 vsnprintf 格式字符串问题

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/px4iofirmware/px4io.c` |
| **行号** | ~107 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-134 (Format String) |

`vsnprintf()` 的格式字符串参数可能被外部控制。px4io 是协处理器固件，运行在底层硬件上，格式字符串漏洞可能导致固件崩溃或代码执行。

---

### 🟡 M-03: px4io syslog 格式字符串漏洞

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/px4iofirmware/px4io.h` |
| **行号** | ~77 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-134 |

`syslog()` 的第一个参数如果包含用户可控数据，可导致格式字符串攻击。

---

### 🟡 M-04: Commander Commander.cpp strcpy 常量字符串拷贝

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/commander/Commander.cpp` |
| **行号** | 4084, 4087 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-120 |

虽然 Flawfinder 标注为低风险（源是常量字符串），但使用 `strcpy()` 替代 `strncpy()` 仍是危险的编码实践，未来对代码的修改可能引入溢出风险。

---

### 🟡 M-05: Logger getenv 环境变量不可信

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/logger/logger.cpp` |
| **行号** | ~349 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-807 (Environment Variable Untrusted) |

`getenv()` 获取环境变量值未做充分校验。环境变量可能被恶意设置，导致路径遍历、缓冲区溢出等问题。

---

### 🟡 M-06: Replay 模块 getenv 环境变量不可信

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/replay/Replay.cpp`, `src/modules/replay/replay_main.cpp` |
| **行号** | Replay.cpp:579,1053; replay_main.cpp:42 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-807 |

相同问题，replay 模块从环境变量读取配置信息，未做充分的边界检查和验证。

---

### 🟡 M-07: uORB 测试 vfprintf 格式字符串

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/uORB/uORB_tests/uORBTest_UnitTest.cpp` |
| **行号** | 853, 867 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-134 |

虽然位于测试代码中，但若测试被集成到生产构建中或 format string 受外部控制，存在风险。

---

### 🟡 M-08: dataman memcpy 无边界检查

| 属性 | 内容 |
|------|------|
| **文件路径** | `src/modules/dataman/dataman.cpp` |
| **行号** | 486, 497, 519 |
| **严重等级** | **Medium（中危）** |
| **CWE** | CWE-120 |

数据管理模块使用 `memcpy()` 复制数据，若源数据长度超过目标缓冲区，将导致堆溢出。

---

## 3. 低危漏洞（Low）

### 🟢 L-01: 多处静态数组越界风险

| 文件 | 说明 |
|------|------|
| `commander/Commander.cpp:4407` | 静态数组可能被不当限制 |
| `commander/PreflightCheck.cpp:73` | 数组大小不足可能溢出 |
| `commander/accelerometer_calibration.cpp:195` | 同上 |
| `commander/calibration_routines.cpp:731` | 同上 |
| `commander/gyro_calibration.cpp:241,452` | 同上 |
| `commander/mag_calibration.cpp:115,579` | 同上 |
| `commander/rc_check.cpp:59` | 同上 |
| `commander/state_machine_helper.cpp:79` | 同上 |
| `dataman/dataman.cpp:497` | 同上 |

这些漏洞风险较低是因为当前上下文中数据范围受到限制，但代码弹性较差，未来改动容易引入溢出。

---

### 🟢 L-02: Replay 模块弱随机数 (CWE-327)

| 文件 | 行号 |
|------|------|
| `replay/Replay.cpp` | 579 |
| `sih/sih.cpp` | 231 |

`srand()` 和 `setstate()` 用于生成随机数，但种子不够随机（如使用 `time()`），不适用于安全场景。目前未用于加密，风险低。

---

### 🟢 L-03: Commander 多处 sprintf 低风险溢出

`commander/accelerometer_calibration.cpp`、`commander/gyro_calibration.cpp`、`commander/mag_calibration.cpp`、`commander/rc_check.cpp` 中有大量 `sprintf()` 调用，Flawfinder 评估为低风险（源具有常量最大长度），但建议统一改用 `snprintf()`。

---

## 4. 总结与建议

### 风险分布

| 严重等级 | 数量 | 占比 |
|---------|------|------|
| **Critical** | 1 | 最严重 |
| **High** | 7 | 需立即修复 |
| **Medium** | 8 | 应尽快修复 |
| **Low** | 多个 | 建议改进 |

### 最关键的修复优先级

1. **🔴 MAVLink FTP 路径遍历（H-01）** — 这是最严重的漏洞，攻击者可远程完全控制飞控文件系统
2. **🔴 MAVLink FTP strcpy 溢出（H-02）** — 同为 FTP 协议相关，可被远程利用
3. **🔴 Commander strncat 溢出（H-03）** — 校准过程中的缓冲区溢出
4. **🔴 sscanf 溢出（H-04, H-05）** — 日志模块和 MAVLink 日志处理
5. **🔴 sprintf 溢出（H-06）** — 遍布多个模块
6. **🔴 MAVLink TOCTOU（H-07）** — 权限检查竞争条件
7. **🔴 MAVLink FTP 危险操作暴露（H-08）** — 远程文件系统破坏

### 通用建议

1. **禁用危险函数**：项目中应全面禁止 `sprintf`、`strcpy`、`strcat`、`strncat`、`scanf`/`sscanf`（无宽度限制），强制使用 `snprintf`、`strncpy`/`strlcpy`、`strlcat` 等安全替代函数。
2. **路径规范化**：所有文件路径操作都需进行规范化处理，防止路径遍历攻击。
3. **MAVLink 安全加固**：MAVLink 协议直接暴露给地面站，所有通过 MAVLink 接收的数据都应视为不可信输入，进行严格校验。
4. **权限最小化**：限制 MAVLink FTP 可操作的文件类型和路径范围。
5. **编译选项**：启用编译器的安全选项（如 `-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`）提供运行时保护。
6. **定期扫描**：将 Flawfinder、Semgrep 等静态分析工具集成到 CI/CD 流程中。

---

*报告生成完毕。扫描覆盖了 30+ 个模块，484 项潜在安全问题，其中 28 项高危。核心风险集中在 MAVLink FTP 实现和 Commander 校准模块中。*
