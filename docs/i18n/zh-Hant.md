# Clean Your TV — 使用者指南

No-root 和 Root 是適用於不同電視組態的同等選項。使用 LG 開發者模式請選擇 No-root；已有 root SSH 訪問請選擇 Root。兩種版本的兼容性與測試範圍分別記錄。

## 安裝之前

本指南涵蓋 **[v1.2.0 穩定版](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.2.0)**。最新下載鏈接指向已發佈的穩定版。另請參閱[安裝指南](../INSTALL.md)和[發行說明](../RELEASE-1.2.0.md)。

v1.2.0 包含 cytv **0.3.1**、Home **1.4.1**、Home Helper **0.6.19**、Root Edition **0.3.0**、Home Updater 和 Root Updater **0.2.1**、Android **0.2.1-preview**（版本代碼 **10**），以及 System Updater supervisor **1.0.0**（協議 **1**）。

安裝期間保持電視開機，將電腦與電視連線到同一個可信本地網路。完成後無需電腦持續開機。兼容性取決於型號、固件和遙控器；Root 仍有待完成的實機檢查。

- **No-root：**啟用 LG Developer Mode 和 Key Server，輸入電視顯示的口令，並單獨接受電視配對請求。開發者模式必須保持有效；過期可能移除側載應用。即使啟用 Beta 自動續期，也要留意官方計時器。Helper 監控需要本地網路。
- **Root：**必須已有 root SSH 訪問權限。安裝程式不會為電視獲取 root。已取得 root 的電視不要啟用開發者模式。請保留 root 訪問和恢復服務。

新版 No-root Helper 要求電視 Node.js **0.12.2+**；安裝程式會預先檢查。舊的已發佈安裝套件不會自動獲得此兼容性。每種型號仍需檢查輸入設備訪問、待機和冷啟動。

## v1.1.0 起的可選 Root Python

Root 要求電視上有可用的 Python **3.9+**。安裝程式會檢查必需模塊（包括 `json`、`fcntl`）、鎖、檔案系統及子進程操作；僅版本號滿足要求並不足夠。如果已有合適解釋器，則無需額外下載。否則會在電腦或 Android 上下載經過驗證的 **ARMv7 soft-float CPython 3.13.17**，再透過可信 SSH 傳到電視；電視無需聯網。

普通安裝程式不包含此可選壓縮包。下載約 **26.3 MB**，規範化 SSH 傳輸約 **51.5 MB**，安裝後約 **119.3 MB**；初始暫存要求 **320 MiB** 可用空間。專用執行環境不會替換系統 Python、libc 或全局 PATH。

仍需兼容的載入器和庫、root SSH、Node.js **8+**、`luna-send` 以及 webOS 應用/服務目錄。No-root Helper 要求 Node.js **0.12.2+**。LG UK6540PTD / 固件 05.50.70 / ARM32（#37，只有 Python 2.7.12）**尚未**透過此執行環境的實機驗收。QEMU 測試不能證明電視、冷啟動、遙控輸入或回復兼容性；歷史實機結果僅適用於記錄的型號、固件和建置產物。

在聯網電腦上準備驗證過的快取，**無需連線電視**：

```sh
./cytv --language zh-Hant --prepare-python-runtime
```

安裝時使用同一私有資料目錄。移動快取時，請準備專用新目錄，並在兩個指令中都使用 `--data-dir /path/to/private-data`。不要將普通 SSH 密鑰或組態複製到共享快取。狀態、診斷、恢復和移除不會自動下載 Python。保留已安裝更新程式或恢復功能引用的執行環境槽位。參閱 [Python 詳情](../OPTIONAL-PYTHON.md)。

## 安裝與選擇語言

- **Windows x64：**下載 `cytv-windows-x64-desktop.zip`，在資源管理器中選擇“全部解壓縮”，然後打開 `cytv-desktop/cytv-desktop.exe`。保留旁邊的 `_internal` 資料夾。尚未組態 Windows 發佈者簽名。獨立主控台為 `cytv-windows-x64.exe`；將其重命名為 `cytv.exe`，在 PowerShell 中用 `.\cytv.exe` 替換下方指令的 `./cytv`。
- **macOS 13+：**解壓 `cytv-macos-arm64.zip`（Apple Silicon）或 `cytv-macos-x64.zip`（Intel），將 `cytv.app` 移到“應用程式”後打開。允許本地網路訪問。若被阻止，僅對可信項目下載使用“隱私與安全性 → 仍要打開”；不要禁用 Gatekeeper。舊系統尚未驗收。
- **Linux x64：**在 Ubuntu 22.04+、Debian 12+ 或 Mint 21+ 中，用圖形軟體包安裝程式打開 `cytv-linux-x64.deb`，安裝後從應用菜單啟動 Clean Your TV。桌面庫可能需要聯網下載。不含 Linux ARM。獨立 `cytv-linux-x64` 為 CLI；圖形界面請使用 `.deb`。

[Android 安裝程式](../../android/README.md)右上角顯示當前語言，點擊即可切換，選擇儲存在手機上。Android 的狀態和恢復操作在連線時保留所選動作並顯示專屬進度，採用手機系統字體和較大的標籤、幫助文字。

此候選原始碼新增简体中文（`zh-Hans`）和繁體中文（`zh-Hant`）；不代表已發佈的 v1.2.0 安裝套件包含中文。桌面嚮導自動選擇系統語言，也可手動選擇並儲存。電視端在**設定 → 語言**中選擇，或使用系統/自動選項。安裝程式與電視偏好獨立。完整代碼見[語言索引](../LANGUAGES.md)。

單獨下載的 macOS/Linux CLI，請在解壓目錄打開終端：

```sh
chmod +x cytv
./cytv --language zh-Hant install
```

選擇電視（或輸入 IP）、版本，然後檢查摘要。僅在可信網路上為自己的電視接受首次 SSH 信任；儲存的密鑰發生改變時將阻止訪問。Root 憑據與開發者模式口令不同。Root 會安裝恢復功能並立即啟用 Home，無試用或 Keep 步驟。請在自己的電視上檢查方向鍵、OK、Home、返回/取消、音量、待機/喚醒和冷啟動。

Root 移除中斷時，在應用中再次選擇“移除”。它會先檢查電視保留的日誌與安裝套件狀態；已完成的移除不會再次提交。如前次操作仍在進行，請等待一分鐘。如無法驗證結果，重啟電視後再檢查，並保留診斷報告。

## 日常使用與恢復

方向鍵選擇圖塊，OK 打開，按住 OK 調整順序。短按返回保留應用本身的導航和退出確認。啟用 Home 控制時，短按 Home 打開 Clean Your TV。新建置中，按住返回 1.2 秒會臨時打開 LG Home 一次，不改變 Home 控制開關和設定。

**新建置：兩秒內按 Home 三次，每次都鬆開**，即可返回 LG Home 並停止 Home 控制，偏好設定保留。No-root Helper 0.6.13 及更早版本改為按住 Home 約兩秒；按住 Home 不是 Root 的緊急退出方式。

No-root：從 LG Apps 打開 **Home Helper** 恢復；只打開 Home 不會解除停止狀態。Root：在 Home 設定中啟用 **Change Home** 恢復。**Open LG Home** 只打開 LG Home 一次，不更改路由。要持續使用 LG Home，請關閉 **Change Home** 或執行 `cytv restore`。不要同時執行兩種控制器。若故障重復出現，請保持 LG Home 啟用。

```sh
./cytv --language zh-Hant status
./cytv --language zh-Hant doctor --report
./cytv --language zh-Hant restore
./cytv --language zh-Hant uninstall
```

中斷後重試前先執行 `status`，保留日誌和恢復檔案。`restore` 返回 LG Home 而不移除應用；`uninstall` 先恢復再移除。Root 恢復狀態會特意保留，切勿刪除它來強行重新安裝。分享報告前請檢查內容，不要公開密鑰或組態資料夾。

## 更新與移除

保留已知可用的安裝套件和私有設定備份。電腦輔助替換 No-root 安裝套件時，先停止 Helper，然後直接更新；解除安裝可能清除設定。移除桌面應用不會移除電視應用。不要用獨立 IPK 替換正在執行的 Root 環境；請使用 cytv 的明確恢復/重新安裝流程。

v1.1.0 起，Home 設定 → 軟體更新中的 **Update all** 使用已簽名的完整發行集：已取得 root 的 No-root 電視更新 Home、Helper 和 Home Updater；Root 更新 Root Home、Root Updater 及路由/恢復執行環境。此功能要求 root、Homebrew Channel、可用的 webOS 安裝服務、Python **3.9+** 和 Node.js **8+**。無 root 電視仍需電腦安裝程式。

首次設定請使用完整穩定版安裝程式，安裝匹配的過渡 Home 和對應版本的恢復 Updater。**現有 Root 安裝若保留 Root Updater，可能會主動阻止通用重新安裝。**請先透過匹配的舊版恢復流程檢查 `status`、Recovery 和現有事務；參閱[現有電視檢查點](../UPDATES.md#one-time-computer-preparation)。不要刪除日誌或繞過檢查。舊的僅 Home OTA 不會安裝新基礎設施。

組件和恢復狀態就緒後，才在桌面安裝程式中啟用**所有電視組件的更新**。已儲存 root SSH 連線的 Root 版本可執行：

```sh
./cytv --language zh-Hant enable-system-updates --edition root --host TV_ADDRESS
```

此獨立操作會安裝固定 supervisor，並將已安裝組件集記錄為回復基線。它要求 Home 元資料有 `systemUpdateProtocol = 1`，不會重裝 Home 或改變路由。在已取得 root 的電視上使用普通 No-root，也需要 root SSH 和匹配的電腦安裝組件，參閱[引導步驟](../UPDATES.md#one-time-computer-preparation)。舊的僅 Home OTA **不會**安裝 supervisor、Python 或更新基礎設施。安裝 supervisor 後，衝突的舊安裝器會被禁用；不要繞過它替換安裝套件。

Root 0.2.0、Root Updater 0.2.0 和 supervisor 1.0.0 在 OLED55C3RLA / 固件 43.21.71 / webOS 11.2.0 上透過了控制、三次 Home 緊急退出/恢復、Emby 打開時待機/喚醒 70 秒、已安裝版本菜單和更新源不可用時的友好提示檢查（`d344d92`，產品內容與 `4b66951` 相同）。真正冷啟動、電視上的 Helper 0.6.19、UK6540PTD、完整簽名系統升級/回復仍未測試。穩定版發佈接受這一有限證據；其他型號未經驗證。

英文技術資料：[桌面安裝](../DESKTOP_INSTALL.md)、[CLI](../CLI.md)、[兩種版本安裝](../INSTALL.md)、[手動安裝](../MANUAL_INSTALL.md)、[恢復](../RECOVERY.md)、[版本比較](../EDITIONS.md)。

連線後，cytv 顯示電視當前版本 → 內建版本：No-root 的 Home 和 Home Helper，或 Root 和 Root Updater。安裝前需檢查確認。首次安裝、重新安裝與降級會分別標明；`--yes` 跳過確認但仍列印版本。

軟體更新只顯示當前已安裝版本或更新版本的發行詳情。Recovery 顯示已儲存的回復版本或不可回復原因；返回鍵回到更新。No-root 檢查電視 shell ABI，因此可接受已驗證 ARM32 使用者空間的 64 位內核。如檢查失敗，請提供診斷 JSON，不要分享密鑰或口令。

Home 更新安裝前要求確認，之後自動檢查啟動健康狀態，無需手動確認。後台刷新不會改變已選遙控按鈕。舊的僅 Home 回復恢復之前的 Home 包和組態；System Updater 回復恢復完整的前一發行集。確認後恢復功能仍可使用，無時間限制，直到下次更新。較新的設定可能丟失；回復前會確認。電視上的 No-root 更新與回復仍要求 root 和 Homebrew Channel。

中斷後先執行 `status` 並檢查 Recovery。安裝結果不確定時會阻止重新安裝與回復；保留日誌、恢復記錄和執行環境槽位，切勿刪除狀態來強行重試。中斷的 cytv 操作只能透過經過檢查的恢復流程繼續。

更新頁面分開展示版本、狀態和可讀發行說明。上下鍵閱讀說明，左右鍵選擇下方固定操作。自動啟動檢查後，Root 會恢復先前啟用的 Home 控制；No-root 保留獨立 Helper 狀態。已禁用、明確關閉或緊急停止狀態保持關閉。

打開 Home 設定會在後台檢查更新。軟體更新上的橙色圓點表示有新版本，包括需要電腦安裝的版本；檢查期間仍可使用設定。No-root 的 Home 設定 → 開發者模式提供自動續期、會話檢查和診斷，主屏保留簡短狀態和續期錯誤，返回鍵回到 Home 設定。兩種版本都將語言、軟體更新、電視設定放在同一行，箭頭打開各項。

打開 Home Helper 可查看用途和狀態。啟動已停止的 Helper 需要確認。Home Updater 和 Root Updater 解釋恢復功能，日常更新位於 Home 設定。僅存在已儲存版本時顯示恢復，替換 Home 及其設定前需要確認。

Root 若在 supervisor 引導後立即顯示 `Denied methods call status`，請關閉並重新打開 Home Root 一次，再檢查更新。如持續出現，保留診斷和恢復狀態。

1.2.0（#51）：電視拒絕安裝套件後，診斷 JSON 只保留操作類別、有界數字錯誤/狀態碼、允許列表內的安裝套件狀態和布爾結果，排除電視原始錯誤文本、路徑和應用 ID。分享前請檢查報告；不會自動重試安裝，UN70006LA 安裝失敗尚未確認修復。

1.2.0（#59）：無法檢查 Helper 狀態時，仍可在確認後使用 **Start Helper**。打開圖塊不會重啟 Helper 或清除緊急停止。Home 按鈕設定要求控制器正常響應。

1.2.0（#55）：Root 安裝前驗證遷移資料。組態前中斷的清理可在不存在 LS2 快照時移除包，保留驗證過的收據供正常 cytv 歸檔/重新安裝流程使用。後續階段缺少快照或證據衝突仍會停止清理。這要求新驅動；OLED Flex 恢復服務啟動失敗仍未解決。

## 1.2.0 的 LG 固件更新阻止功能

僅 Root：Home 設定 → LG 固件更新可更改 Homebrew Channel 現有偏好，包括固件安全更新；Clean Your TV 更新獨立。兩個方向都必須真正重啟電視，待機無效。開關顯示儲存的偏好，不代表已驗證阻止生效。有些電視會在阻止啟動前檢查更新，因此提示可能保留，可能還需路由器阻止。移除 CYTV 或回復後 Homebrew 仍保留偏好。如功能不可用或狀態未確認，請檢查 Homebrew 並刷新狀態。實機檢查範圍見驗收記錄。

[LG 固件更新阻止](../LG-FIRMWARE-UPDATES.md) · [1.2.0 驗收](../RELEASE-1.2.0-ACCEPTANCE.md)

## 候選版：桌面引導恢復

以下為下一候選版行為，**不屬於已發佈的 v1.2.0 安裝程式**。檢查電視狀態、連線診斷或返回 LG Home 後，如有未完成的 No-root 移除，可對同一電視和連線選擇**恢復並重新安裝**。先檢查並明確確認完成移除（預設：否），再檢查內建版本並安裝。“設定我的電視”也可直接提供此恢復。單獨返回 LG Home 不會完成移除。

失敗時使用**儲存診斷報告…**儲存本次失敗的報告，並附到問題中，無需終端。如未能生成報告，請提供畫面錯誤。保留恢復檔案；失敗或結果不明的操作不會自動重試。這尚不能證明 G5 / 固件 43.21.71 的報告問題（#65）已修復。

## 下一候選版：連線與 Home 狀態（#12）

未發佈準備：Android Tools 返回開始頁後保留所選電視、版本和 SSH 端口；No-root 通常為 9922。如 Home 設定無法驗證 Home 控制，將顯示未知狀態並隱藏 Change Home，直到收到有效響應。這不表示 Helper 停止，也不會重啟它。這些更改不在已發佈的 v1.2.0 包中。

下一候選版 Root 診斷（#55）：設定失敗後儲存該次嘗試的報告，其中可能包含分類後的恢復服務啟動故障。保留恢復狀態和舊驅動。尚未確認 OLED Flex 問題修復。

## 未發佈候選版：透過 Homebrew 設定 Root

此原始碼候選版新增獨立的 **CYTV Installer** 電視應用，**僅用於 Root**。它尚未發佈到 Homebrew 目錄。Windows、macOS、Linux、Android 上的 cytv 仍支援兩種版本；現有下載鏈接仍指向已發佈 cytv。

Installer 要求已有 root、可執行 root exec 的 Homebrew Channel、Node.js **8+** 和可用 Python **3.9+**。對於受支援的 ARMv7/`armv8l` 32 位使用者空間，離線內建固定 Python。打開應用/查看狀態只讀取資訊：需明確準備缺失的 Python，再檢查，然後檢查安裝摘要。執行環境設定要求 **Installer 安裝後仍有 320 MiB 可用空間**，另需尚未測量的電視安裝套件暫存空間。不代表新增型號/固件兼容性。

設定會安裝 Root Home 和 Root Updater；準備 System Updater 是明確的可選步驟。驗證後單獨啟用 Change Home；設定絕不清除緊急停止或關閉狀態。經驗證的現有安裝可在 cytv/電視之間共享組態和恢復狀態，無需重裝或重置。未知舊基礎設施需先診斷；安裝套件偏好導入僅供首次設定，不用於瀏覽器儲存或基礎設施遷移。

中斷後先檢查狀態。只有原始快照/租約仍存在且最終回讀已確認時才顯示“繼續”。其他階段需要檢查狀態、恢復或診斷；原始碼 CLI 可明確恢復更多已識別階段。cytv 的“完成 Root 設定”不會重啟未完成的工作進程。不要刪除日誌或盲目重試。Homebrew 只更新 Installer；現有更新程式負責產品更新/已簽名完整發行集。刪除 Installer 不會刪除產品。

明確的完整移除會恢復 LG Home 並清理本項目的啟動鈎子，同時保留獨立恢復/歸檔證據及引用中的 Python 槽位。此路徑所有實機檢查仍待完成；上文 Root 0.2.0 的 C3 歷史結果不能驗證 Homebrew 設定。

[候選版設定與恢復（英文）](../INSTALL.md#candidate-on-tv-root-installation) · [待完成實機驗收（英文）](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)
