# Clean Your TV — 用户指南

No-root 和 Root 是适用于不同电视配置的同等选项。使用 LG 开发者模式请选择 No-root；已有 root SSH 访问请选择 Root。两种版本的兼容性与测试范围分别记录。

## 安装之前

本指南涵盖 **[v1.2.0 稳定版](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.2.0)**。最新下载链接指向已发布的稳定版。另请参阅[安装指南](../INSTALL.md)和[发行说明](../RELEASE-1.2.0.md)。

v1.2.0 包含 cytv **0.3.1**、Home **1.4.1**、Home Helper **0.6.19**、Root Edition **0.3.0**、Home Updater 和 Root Updater **0.2.1**、Android **0.2.1-preview**（版本代码 **10**），以及 System Updater supervisor **1.0.0**（协议 **1**）。

安装期间保持电视开机，将电脑与电视连接到同一个可信本地网络。完成后无需电脑持续开机。兼容性取决于型号、固件和遥控器；Root 仍有待完成的实机检查。

- **No-root：**启用 LG Developer Mode 和 Key Server，输入电视显示的口令，并单独接受电视配对请求。开发者模式必须保持有效；过期可能移除侧载应用。即使启用 Beta 自动续期，也要留意官方计时器。Helper 监控需要本地网络。
- **Root：**必须已有 root SSH 访问权限。安装程序不会为电视获取 root。已取得 root 的电视不要启用开发者模式。请保留 root 访问和恢复服务。

新版 No-root Helper 要求电视 Node.js **0.12.2+**；安装程序会预先检查。旧的已发布安装包不会自动获得此兼容性。每种型号仍需检查输入设备访问、待机和冷启动。

## v1.1.0 起的可选 Root Python

Root 要求电视上有可用的 Python **3.9+**。安装程序会检查必需模块（包括 `json`、`fcntl`）、锁、文件系统及子进程操作；仅版本号满足要求并不足够。如果已有合适解释器，则无需额外下载。否则会在电脑或 Android 上下载经过验证的 **ARMv7 soft-float CPython 3.13.17**，再通过可信 SSH 传到电视；电视无需联网。

普通安装程序不包含此可选压缩包。下载约 **26.3 MB**，规范化 SSH 传输约 **51.5 MB**，安装后约 **119.3 MB**；初始暂存要求 **320 MiB** 可用空间。专用运行环境不会替换系统 Python、libc 或全局 PATH。

仍需兼容的加载器和库、root SSH、Node.js **8+**、`luna-send` 以及 webOS 应用/服务目录。No-root Helper 要求 Node.js **0.12.2+**。LG UK6540PTD / 固件 05.50.70 / ARM32（#37，只有 Python 2.7.12）**尚未**通过此运行环境的实机验收。QEMU 测试不能证明电视、冷启动、遥控输入或回滚兼容性；历史实机结果仅适用于记录的型号、固件和构建产物。

在联网电脑上准备验证过的缓存，**无需连接电视**：

```sh
./cytv --language zh-Hans --prepare-python-runtime
```

安装时使用同一私有数据目录。移动缓存时，请准备专用新目录，并在两个命令中都使用 `--data-dir /path/to/private-data`。不要将普通 SSH 密钥或配置复制到共享缓存。状态、诊断、恢复和移除不会自动下载 Python。保留已安装更新程序或恢复功能引用的运行环境槽位。参阅 [Python 详情](../OPTIONAL-PYTHON.md)。

## 安装与选择语言

- **Windows x64：**下载 `cytv-windows-x64-desktop.zip`，在资源管理器中选择“全部解压缩”，然后打开 `cytv-desktop/cytv-desktop.exe`。保留旁边的 `_internal` 文件夹。尚未配置 Windows 发布者签名。独立控制台为 `cytv-windows-x64.exe`；将其重命名为 `cytv.exe`，在 PowerShell 中用 `.\cytv.exe` 替换下方命令的 `./cytv`。
- **macOS 13+：**解压 `cytv-macos-arm64.zip`（Apple Silicon）或 `cytv-macos-x64.zip`（Intel），将 `cytv.app` 移到“应用程序”后打开。允许本地网络访问。若被阻止，仅对可信项目下载使用“隐私与安全性 → 仍要打开”；不要禁用 Gatekeeper。旧系统尚未验收。
- **Linux x64：**在 Ubuntu 22.04+、Debian 12+ 或 Mint 21+ 中，用图形软件包安装程序打开 `cytv-linux-x64.deb`，安装后从应用菜单启动 Clean Your TV。桌面库可能需要联网下载。不含 Linux ARM。独立 `cytv-linux-x64` 为 CLI；图形界面请使用 `.deb`。

[Android 安装程序](../../android/README.md)右上角显示当前语言，点击即可切换，选择保存在手机上。Android 的状态和恢复操作在连接时保留所选动作并显示专属进度，采用手机系统字体和较大的标签、帮助文字。

此候选源码新增简体中文（`zh-Hans`）和繁體中文（`zh-Hant`）；不代表已发布的 v1.2.0 安装包包含中文。桌面向导自动选择系统语言，也可手动选择并保存。电视端在**设置 → 语言**中选择，或使用系统/自动选项。安装程序与电视偏好独立。完整代码见[语言索引](../LANGUAGES.md)。

单独下载的 macOS/Linux CLI，请在解压目录打开终端：

```sh
chmod +x cytv
./cytv --language zh-Hans install
```

选择电视（或输入 IP）、版本，然后检查摘要。仅在可信网络上为自己的电视接受首次 SSH 信任；保存的密钥发生改变时将阻止访问。Root 凭据与开发者模式口令不同。Root 会安装恢复功能并立即激活 Home，无试用或 Keep 步骤。请在自己的电视上检查方向键、OK、Home、返回/取消、音量、待机/唤醒和冷启动。

Root 移除中断时，在应用中再次选择“移除”。它会先检查电视保留的日志与安装包状态；已完成的移除不会再次提交。如前次操作仍在进行，请等待一分钟。如无法验证结果，重启电视后再检查，并保留诊断报告。

## 日常使用与恢复

方向键选择磁贴，OK 打开，按住 OK 调整顺序。短按返回保留应用本身的导航和退出确认。启用 Home 控制时，短按 Home 打开 Clean Your TV。新构建中，按住返回 1.2 秒会临时打开 LG Home 一次，不改变 Home 控制开关和设置。

**新构建：两秒内按 Home 三次，每次都松开**，即可返回 LG Home 并停止 Home 控制，偏好设置保留。No-root Helper 0.6.13 及更早版本改为按住 Home 约两秒；按住 Home 不是 Root 的紧急退出方式。

No-root：从 LG Apps 打开 **Home Helper** 恢复；只打开 Home 不会解除停止状态。Root：在 Home 设置中启用 **Change Home** 恢复。**Open LG Home** 只打开 LG Home 一次，不更改路由。要持续使用 LG Home，请关闭 **Change Home** 或运行 `cytv restore`。不要同时运行两种控制器。若故障重复出现，请保持 LG Home 启用。

```sh
./cytv --language zh-Hans status
./cytv --language zh-Hans doctor --report
./cytv --language zh-Hans restore
./cytv --language zh-Hans uninstall
```

中断后重试前先运行 `status`，保留日志和恢复文件。`restore` 返回 LG Home 而不移除应用；`uninstall` 先恢复再移除。Root 恢复状态会特意保留，切勿删除它来强行重新安装。分享报告前请检查内容，不要公开密钥或配置文件夹。

## 更新与移除

保留已知可用的安装包和私有设置备份。电脑辅助替换 No-root 安装包时，先停止 Helper，然后直接更新；卸载可能清除设置。移除桌面应用不会移除电视应用。不要用独立 IPK 替换正在运行的 Root 环境；请使用 cytv 的明确恢复/重新安装流程。

v1.1.0 起，Home 设置 → 软件更新中的 **Update all** 使用已签名的完整发行集：已取得 root 的 No-root 电视更新 Home、Helper 和 Home Updater；Root 更新 Root Home、Root Updater 及路由/恢复运行环境。此功能要求 root、Homebrew Channel、可用的 webOS 安装服务、Python **3.9+** 和 Node.js **8+**。无 root 电视仍需电脑安装程序。

首次设置请使用完整稳定版安装程序，安装匹配的过渡 Home 和对应版本的恢复 Updater。**现有 Root 安装若保留 Root Updater，可能会主动阻止通用重新安装。**请先通过匹配的旧版恢复流程检查 `status`、Recovery 和现有事务；参阅[现有电视检查点](../UPDATES.md#one-time-computer-preparation)。不要删除日志或绕过检查。旧的仅 Home OTA 不会安装新基础设施。

组件和恢复状态就绪后，才在桌面安装程序中启用**所有电视组件的更新**。已保存 root SSH 连接的 Root 版本可运行：

```sh
./cytv --language zh-Hans enable-system-updates --edition root --host TV_ADDRESS
```

此独立操作会安装固定 supervisor，并将已安装组件集记录为回滚基线。它要求 Home 元数据有 `systemUpdateProtocol = 1`，不会重装 Home 或改变路由。在已取得 root 的电视上使用普通 No-root，也需要 root SSH 和匹配的电脑安装组件，参阅[引导步骤](../UPDATES.md#one-time-computer-preparation)。旧的仅 Home OTA **不会**安装 supervisor、Python 或更新基础设施。安装 supervisor 后，冲突的旧安装器会被禁用；不要绕过它替换安装包。

Root 0.2.0、Root Updater 0.2.0 和 supervisor 1.0.0 在 OLED55C3RLA / 固件 43.21.71 / webOS 11.2.0 上通过了控制、三次 Home 紧急退出/恢复、Emby 打开时待机/唤醒 70 秒、已安装版本菜单和更新源不可用时的友好提示检查（`d344d92`，产品内容与 `4b66951` 相同）。真正冷启动、电视上的 Helper 0.6.19、UK6540PTD、完整签名系统升级/回滚仍未测试。稳定版发布接受这一有限证据；其他型号未经验证。

英文技术资料：[桌面安装](../DESKTOP_INSTALL.md)、[CLI](../CLI.md)、[两种版本安装](../INSTALL.md)、[手动安装](../MANUAL_INSTALL.md)、[恢复](../RECOVERY.md)、[版本比较](../EDITIONS.md)。

连接后，cytv 显示电视当前版本 → 内置版本：No-root 的 Home 和 Home Helper，或 Root 和 Root Updater。安装前需检查确认。首次安装、重新安装与降级会分别标明；`--yes` 跳过确认但仍打印版本。

软件更新只显示当前已安装版本或更新版本的发行详情。Recovery 显示已保存的回滚版本或不可回滚原因；返回键回到更新。No-root 检查电视 shell ABI，因此可接受已验证 ARM32 用户空间的 64 位内核。如检查失败，请提供诊断 JSON，不要分享密钥或口令。

Home 更新安装前要求确认，之后自动检查启动健康状态，无需手动确认。后台刷新不会改变已选遥控按钮。旧的仅 Home 回滚恢复之前的 Home 包和配置；System Updater 回滚恢复完整的前一发行集。确认后恢复功能仍可使用，无时间限制，直到下次更新。较新的设置可能丢失；回滚前会确认。电视上的 No-root 更新与回滚仍要求 root 和 Homebrew Channel。

中断后先运行 `status` 并检查 Recovery。安装结果不确定时会阻止重新安装与回滚；保留日志、恢复记录和运行环境槽位，切勿删除状态来强行重试。中断的 cytv 操作只能通过经过检查的恢复流程继续。

更新页面分开展示版本、状态和可读发行说明。上下键阅读说明，左右键选择下方固定操作。自动启动检查后，Root 会恢复先前启用的 Home 控制；No-root 保留独立 Helper 状态。已禁用、明确关闭或紧急停止状态保持关闭。

打开 Home 设置会在后台检查更新。软件更新上的橙色圆点表示有新版本，包括需要电脑安装的版本；检查期间仍可使用设置。No-root 的 Home 设置 → 开发者模式提供自动续期、会话检查和诊断，主屏保留简短状态和续期错误，返回键回到 Home 设置。两种版本都将语言、软件更新、电视设置放在同一行，箭头打开各项。

打开 Home Helper 可查看用途和状态。启动已停止的 Helper 需要确认。Home Updater 和 Root Updater 解释恢复功能，日常更新位于 Home 设置。仅存在已保存版本时显示恢复，替换 Home 及其设置前需要确认。

Root 若在 supervisor 引导后立即显示 `Denied methods call status`，请关闭并重新打开 Home Root 一次，再检查更新。如持续出现，保留诊断和恢复状态。

1.2.0（#51）：电视拒绝安装包后，诊断 JSON 只保留操作类别、有界数字错误/状态码、允许列表内的安装包状态和布尔结果，排除电视原始错误文本、路径和应用 ID。分享前请检查报告；不会自动重试安装，UN70006LA 安装失败尚未确认修复。

1.2.0（#59）：无法检查 Helper 状态时，仍可在确认后使用 **Start Helper**。打开磁贴不会重启 Helper 或清除紧急停止。Home 按钮设置要求控制器正常响应。

1.2.0（#55）：Root 安装前验证迁移数据。配置前中断的清理可在不存在 LS2 快照时移除包，保留验证过的回执供正常 cytv 归档/重新安装流程使用。后续阶段缺少快照或证据冲突仍会停止清理。这要求新驱动；OLED Flex 恢复服务启动失败仍未解决。

## 1.2.0 的 LG 固件更新阻止功能

仅 Root：Home 设置 → LG 固件更新可更改 Homebrew Channel 现有偏好，包括固件安全更新；Clean Your TV 更新独立。两个方向都必须真正重启电视，待机无效。开关显示保存的偏好，不代表已验证阻止生效。有些电视会在阻止启动前检查更新，因此提示可能保留，可能还需路由器阻止。移除 CYTV 或回滚后 Homebrew 仍保留偏好。如功能不可用或状态未确认，请检查 Homebrew 并刷新状态。实机检查范围见验收记录。

[LG 固件更新阻止](../LG-FIRMWARE-UPDATES.md) · [1.2.0 验收](../RELEASE-1.2.0-ACCEPTANCE.md)

## 候选版：桌面引导恢复

以下为下一候选版行为，**不属于已发布的 v1.2.0 安装程序**。检查电视状态、连接诊断或返回 LG Home 后，如有未完成的 No-root 移除，可对同一电视和连接选择**恢复并重新安装**。先检查并明确确认完成移除（默认：否），再检查内置版本并安装。“设置我的电视”也可直接提供此恢复。单独返回 LG Home 不会完成移除。

失败时使用**保存诊断报告…**保存本次失败的报告，并附到问题中，无需终端。如未能生成报告，请提供屏幕错误。保留恢复文件；失败或结果不明的操作不会自动重试。这尚不能证明 G5 / 固件 43.21.71 的报告问题（#65）已修复。

## 下一候选版：连接与 Home 状态（#12）

未发布准备：Android Tools 返回开始页后保留所选电视、版本和 SSH 端口；No-root 通常为 9922。如 Home 设置无法验证 Home 控制，将显示未知状态并隐藏 Change Home，直到收到有效响应。这不表示 Helper 停止，也不会重启它。这些更改不在已发布的 v1.2.0 包中。

下一候选版 Root 诊断（#55）：设置失败后保存该次尝试的报告，其中可能包含分类后的恢复服务启动故障。保留恢复状态和旧驱动。尚未确认 OLED Flex 问题修复。

## 未发布候选版：通过 Homebrew 设置 Root

此源码候选版新增独立的 **CYTV Installer** 电视应用，**仅用于 Root**。它尚未发布到 Homebrew 目录。Windows、macOS、Linux、Android 上的 cytv 仍支持两种版本；现有下载链接仍指向已发布 cytv。

Installer 要求已有 root、可执行 root exec 的 Homebrew Channel、Node.js **8+** 和可用 Python **3.9+**。对于受支持的 ARMv7/`armv8l`/`aarch64` 32 位用户空间，离线内置固定 Python。打开应用/查看状态只读取信息：需明确准备缺失的 Python，再检查，然后检查安装摘要。运行环境设置要求 **Installer 安装后仍有 320 MiB 可用空间**，另需尚未测量的电视安装包暂存空间。不代表新增型号/固件兼容性。

设置会安装 Root Home 和 Root Updater；准备 System Updater 是明确的可选步骤。验证后单独启用 Change Home；设置绝不清除紧急停止或关闭状态。经验证的现有安装可在 cytv/电视之间共享配置和恢复状态，无需重装或重置。未知旧基础设施需先诊断；安装包偏好导入仅供首次设置，不用于浏览器存储或基础设施迁移。

中断后先检查状态。只有原始快照/租约仍存在且最终回读已确认时才显示“继续”。其他阶段需要检查状态、恢复或诊断；源码 CLI 可明确恢复更多已识别阶段。cytv 的“完成 Root 设置”不会重启未完成的工作进程。不要删除日志或盲目重试。Homebrew 只更新 Installer；现有更新程序负责产品更新/已签名完整发行集。删除 Installer 不会删除产品。

明确的完整移除会恢复 LG Home 并清理本项目的启动钩子，同时保留独立恢复/归档证据及引用中的 Python 槽位。此路径所有实机检查仍待完成；上文 Root 0.2.0 的 C3 历史结果不能验证 Homebrew 设置。

启动使用由收据标识归属的私有包装脚本，仅将已安装包的身份信息作为数据进行检查，不执行包内的启动脚本。包缺失或不安全时停止自动重新启用；独立恢复仍可恢复 LG Home。检查可能短暂地在私有目录暂存已验证文件，不会更改 Home 或产品。

[候选版设置与恢复（英文）](../INSTALL.md#candidate-on-tv-root-installation) · [待完成实机验收（英文）](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


此源码候选版中，现有 Root 安装需要经过验证的恢复和重新设置，才能获得修正后的私有运行环境。仅更新 Installer 不会替换它。请保留恢复记录，并且只通过正常设置流程或设置页面启用 Home。
