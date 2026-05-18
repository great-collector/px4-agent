## 1. 无人机软件安全

| 资讯/主题                                          | 时间      | 重点                                                         | 链接                                                         |
| -------------------------------------------------- | --------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| PX4 Autopilot MAVLink FTP 未认证路径遍历漏洞       | 2026      | PX4 官方 GitHub 安全公告，涉及 MAVLink FTP 实现，任意 MAVLink peer 可能读写文件，适合你研究 PX4 软件安全。 | ([GitHub](https://github.com/PX4/PX4-Autopilot/security/advisories/GHSA-fh32-qxj9-x32f?utm_source=chatgpt.com)) |
| PX4 Autopilot 高危漏洞 CVE-2026-1579               | 2026      | CYVIATION 披露 PX4 相关严重漏洞，CVSS 9.8，可能导致无人机被恶意控制。 | ([商业电报](https://www.businesswire.com/news/home/20260407114884/en/CYVIATION-Discovers-Critical-Security-Flaw-in-Popular-UAV-and-Drone-Software-Preventing-Potential-Hacker-Takeovers?utm_source=chatgpt.com)) |
| PX4 Autopilot CVE 列表                             | 2024–2026 | OpenCVE 汇总了 PX4 Autopilot 相关 CVE，包括缓冲区溢出、地理围栏绕过、拒绝服务等。 | ([app.opencve.io](https://app.opencve.io/cve/?product=px4_drone_autopilot&vendor=dronecode&utm_source=chatgpt.com)) |
| PX4-Autopilot CVE-2023-46256                       | 2023      | NVD 记录的 PX4 heap buffer overflow，可能导致无人机异常行为。 | ([国家漏洞数据库](https://nvd.nist.gov/vuln/detail/cve-2023-46256?utm_source=chatgpt.com)) |
| DJI DroneID 可被解码，暴露操作者位置               | 2023      | 研究人员发现 DJI DroneID 广播中可解析操作者 GPS 位置，涉及无人机通信与隐私安全。 | ([WIRED](https://www.wired.com/story/dji-droneid-operator-location-hacker-tool?utm_source=chatgpt.com)) |
| FCC 允许外国制造无人机继续接收安全/固件更新到 2029 | 2026      | 说明“禁止更新”本身会带来安全风险，适合写无人机供应链与固件维护安全。 | ([Tom's Hardware](https://www.tomshardware.com/networking/routers/fcc-reverses-course-allows-software-updates-for-foreign-made-drones-and-routers-until-2029-agency-says-blocking-security-patches-could-create-cybersecurity-risks?utm_source=chatgpt.com)) |

## 2. 自动驾驶/智能汽车软件安全

| 资讯/主题                                                    | 时间     | 重点                                                         | 链接                                                         |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Waymo 召回约 3,791 辆 Robotaxi，原因是自动驾驶软件未能正确处理积水道路 | 2026     | 典型自动驾驶软件安全/功能安全案例，涉及感知、决策、极端天气约束和 OTA 修复。 | ([The Verge](https://www.theverge.com/transportation/928480/waymo-recall-flooded-roads-robotaxi?utm_source=chatgpt.com)) |
| Kia 车辆远程控制 API 漏洞                                    | 2024     | 研究人员发现攻击者仅凭车牌号就可能远程解锁、启动、定位车辆，Kia 已修补。 | ([VicOne](https://vicone.com/blog/now-patched-kia-vulnerabilities-could-have-allowed-remote-control-using-only-a-license-plate-number?utm_source=chatgpt.com)) |
| The Hacker News 对 Kia 漏洞的报道                            | 2024     | 更偏新闻解读，适合引用“车联网 API 漏洞如何影响真实车辆控制”。 | ([The Hacker News](https://thehackernews.com/2024/09/hackers-could-have-remotely-controlled.html?utm_source=chatgpt.com)) |
| Upstream 2025 全球汽车网络安全报告                           | 2025     | 行业报告，覆盖 2024 年智能汽车、车联网、EV 基础设施、数字出行服务的攻击趋势。 | ([Upstream Security](https://upstream.auto/reports/global-automotive-cybersecurity-report-2025/?utm_source=chatgpt.com)) |
| VicOne 2025 汽车网络安全报告                                 | 2025     | 关注软件定义汽车、车载系统、供应链和汽车威胁情报。           | ([VicOne](https://vicone.com/blog/shifting-gears-for-2025-the-next-generation-of-automotive-cybersecurity-challenges?utm_source=chatgpt.com)) |
| NHTSA 自动驾驶系统安全页面                                   | 长期更新 | 美国监管机构关于 Automated Driving Systems 的官方说明，可作为政策/监管背景资料。 | ([NHTSA](https://www.nhtsa.gov/vehicle-safety/automated-vehicles-safety?utm_source=chatgpt.com)) |

## 3. 机器人/机器狗软件安全

| 资讯/主题                                                  | 时间     | 重点                                                         | 链接                                                         |
| ---------------------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Unitree Go1 机器狗后门漏洞 CVE-2025-2894                   | 2025     | NVD 记录：Go1 存在未公开后门，持有 API key 者可能通过 CloudSail 远程控制设备。 | ([国家漏洞数据库](https://nvd.nist.gov/vuln/detail/CVE-2025-2894?utm_source=chatgpt.com)) |
| SecurityWeek：Unitree Go1 机器狗被发现远程访问后门         | 2025     | 新闻报道角度，强调攻击者可能控制远程隧道并访问摄像头。       | ([SecurityWeek](https://www.securityweek.com/undocumented-remote-access-backdoor-found-in-unitree-go1-robot-dog/?utm_source=chatgpt.com)) |
| Unitree 多型号机器人 BLE/Wi-Fi 配置接口漏洞 CVE-2025-35027 | 2025     | 影响 Go2、G1、H1、B2 等，BLE 配网流程中的命令注入可能导致 root 权限执行。 | ([国家漏洞数据库](https://nvd.nist.gov/vuln/detail/CVE-2025-35027?utm_source=chatgpt.com)) |
| UniPwn：Unitree 机器人接管漏洞                             | 2025     | GitHub 技术披露，涉及 BLE、硬编码密钥、认证缺陷、命令注入，适合技术分析。 | ([GitHub](https://github.com/Bin4ry/UniPwn?utm_source=chatgpt.com)) |
| IEEE Spectrum：Unitree 机器人群体接管风险                  | 2025     | 报道 UniPwn 对商用四足/人形机器人的影响，适合作为高可信行业报道。 | ([IEEE Spectrum](https://spectrum.ieee.org/unitree-robot-exploit?utm_source=chatgpt.com)) |
| ROS 2 Navigation2 漏洞 CVE-2024-30962                      | 2024     | NVD 记录：ROS2 navigation2 中 nav2_amcl 存在缓冲区溢出，可本地执行任意代码。 | ([国家漏洞数据库](https://nvd.nist.gov/vuln/detail/CVE-2024-30962?utm_source=chatgpt.com)) |
| ROS 2 Navigation2 漏洞 CVE-2024-30961                      | 2024     | NVD 记录：ROS2 navigation2 存在不安全权限问题，可能通过 nav2_bt_navigator 执行任意代码。 | ([国家漏洞数据库](https://nvd.nist.gov/vuln/detail/CVE-2024-30961?utm_source=chatgpt.com)) |
| Robot Vulnerability Database, RVD                          | 长期项目 | Alias Robotics 维护的机器人漏洞数据库，适合查机器人、ROS、中间件、工业机器人相关漏洞。 | ([GitHub](https://github.com/aliasrobotics/RVD?utm_source=chatgpt.com)) |