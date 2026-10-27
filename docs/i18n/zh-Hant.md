# Clean Your TV — 使用者指南

1.4.0：維護者已接受修正後的 C3 電源、Home、焦點、關閉狀態保持和手動回退至 1.3.0 測試，並要求關閉 #90。其他電視、eARC 聲音和實體 Android 仍未驗證。未重複測試上一候選版本的所有基本按鍵。 [1.4.0 acceptance (English)](../RELEASE-1.4.0-ACCEPTANCE.md). Earlier pending statements below are historical.


No-root 和 Root 是適用於不同電視組態的同等選項。使用 LG 開發者模式請選擇 No-root；已有 root SSH 訪問請選擇 Root。兩種版本的兼容性與測試範圍分別記錄。

## 安裝之前

本指南涵蓋 **[v1.3.0 穩定版](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)**。最新下載鏈接指向已發佈的穩定版。另請參閱[安裝指南](../INSTALL.md)和[發行說明](../RELEASE-1.3.0.md)。

v1.3.0 包含 cytv **0.4.0**、Home **1.4.2**、Home Helper **0.6.19**、Root Edition **0.4.0**、Home Updater 和 Root Updater **0.3.0**、Android **0.3.0-preview**（版本代碼 **11**），以及 System Updater supervisor **1.1.0**（協議 **1**）。

尚未發布的 1.4.0 候選版選用 Android 0.4.0（版本代碼 13），維護者接受模擬器測試後移除 preview。已測環境：Android 15 ARM64 / WebView 124。實體手機及實際電視安裝過程中的復原尚未驗證；Android 7 / WebView 108 是最低要求，並非已測手機設定。更新時不要解除安裝應用程式或清除資料。公開下載仍為 0.3.0-preview。回報問題時請提供手機、Android/WebView、電視/韌體、版本類型及失敗步驟，請勿公開憑證。

1.3.0 已知問題：待機喚醒後，Root 的 Home 控制可能關閉，按 Home 會開啟 LG。請在 Clean Your TV 設定中明確重新開啟 Home 控制；如果開啟失敗，請保留 LG Home 並儲存診斷資訊。參見 [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90) 和[目前測試紀錄](../RELEASE-1.3.0-ACCEPTANCE.md)。

安裝期間保持電視開機，將電腦與電視連線到同一個可信本地網路。完成後無需電腦持續開機。兼容性取決於型號、固件和遙控器；Root 仍有待完成的實機檢查。

- **No-root：**啟用 LG Developer Mode 和 Key Server，輸入電視顯示的口令，並單獨接受電視配對請求。開發者模式必須保持有效；過期可能移除側載應用。即使啟用 Beta 自動續期，也要留意官方計時器。Helper 監控需要本地網路。
- **Root：**必須已有 root SSH 訪問權限。安裝程式不會為電視獲取 root。已取得 root 的電視不要啟用開發者模式。請保留 root 訪問和恢復服務。

新版 No-root Helper 要求電視 Node.js **0.12.2+**；安裝程式會預先檢查。舊的已發佈安裝套件不會自動獲得此兼容性。每種型號仍需檢查輸入設備訪問、待機和冷啟動。


## 設定 Developer Mode（No-root）

Developer Mode 讓 CYTV 可以在沒有 root 的電視上安裝應用程式。

1. 在電視上開啟 LG Apps，搜尋並安裝 Developer Mode。
2. 開啟 Developer Mode 並登入 LG Developer 帳號。如需註冊，請前往 webostv.developer.lge.com。
3. 開啟 Dev Mode Status。電視將重新啟動，之後請再次開啟 Developer Mode。
4. 開啟 Key Server 並保持 Developer Mode 開啟。將其中的 IP Address 填入 CYTV 的電視位址欄。
5. 輸入電視上 Developer Mode 顯示的六位 Passphrase，注意區分大小寫。

請使用電視上的代碼，而非 LG 帳號密碼。如未顯示代碼，請開啟 Key Server。

配對是獨立步驟：電視提示時，請用遙控器允許 CYTV 連線。

請保持 Developer Mode 有效：計時結束前開啟它，並在電視連網時按 EXTEND。過期後 LG 可能會刪除這些應用程式。

Home 是您的應用程式主畫面。Home Helper 讓遙控器的 Home 鍵開啟此畫面。

安裝後按 Home 鍵試用。如果開啟的是 LG Home，請從電視應用程式列表開啟 Home Helper。 在兩秒內短按 Home 三次可返回 LG Home。要重新啟動 Home 控制，請開啟 Home Helper，選擇啟動 Helper 並確認。已儲存的主畫面選擇會保留。

電腦版 CYTV 會逐步顯示準備說明。「詳細資訊」可開啟操作記錄。LG 範例圖片可以放大；請使用您自己電視上的代碼。

[LG Developer Mode](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

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

No-root: 在兩秒內短按 Home 三次可返回 LG Home。要重新啟動 Home 控制，請開啟 Home Helper，選擇啟動 Helper 並確認。已儲存的主畫面選擇會保留。 Root：在 Home 設定中啟用 **Change Home** 恢復。**Open LG Home** 只打開 LG Home 一次，不更改路由。要持續使用 LG Home，請關閉 **Change Home** 或執行 `cytv restore`。不要同時執行兩種控制器。若故障重復出現，請保持 LG Home 啟用。

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

## 1.3.0 新增功能

1.3.0 新增功能。檢查電視狀態、連線診斷或返回 LG Home 後，如有未完成的 No-root 移除，可對同一電視和連線選擇**恢復並重新安裝**。先檢查並明確確認完成移除（預設：否），再檢查內建版本並安裝。“設定我的電視”也可直接提供此恢復。單獨返回 LG Home 不會完成移除。

失敗時使用**儲存診斷報告…**儲存本次失敗的報告，並附到問題中，無需終端。如未能生成報告，請提供畫面錯誤。保留恢復檔案；失敗或結果不明的操作不會自動重試。這尚不能證明 G5 / 固件 43.21.71 的報告問題（#65）已修復。

## 1.3.0 新增功能 — #12

Android Tools 返回開始頁後保留所選電視、版本和 SSH 端口；No-root 通常為 9922。如 Home 設定無法驗證 Home 控制，將顯示未知狀態並隱藏 Change Home，直到收到有效響應。這不表示 Helper 停止，也不會重啟它。這些更改不在已發佈的 v1.2.0 包中。

1.3.0 Root 診斷（#55）：設定失敗後儲存該次嘗試的報告，其中可能包含分類後的恢復服務啟動故障。保留恢復狀態和舊驅動。尚未確認 OLED Flex 問題修復。

## 未發佈候選版：透過 Homebrew 設定 Root

此原始碼候選版新增獨立的 **CYTV Installer** 電視應用，**僅用於 Root**。它尚未發佈到 Homebrew 目錄。Windows、macOS、Linux、Android 上的 cytv 仍支援兩種版本；現有下載鏈接仍指向已發佈 cytv。

Installer 要求已有 root、可執行 root exec 的 Homebrew Channel、Node.js **8+** 和可用 Python **3.9+**。對於受支援的 ARMv7/`armv8l`/`aarch64` 32 位使用者空間，離線內建固定 Python。打開應用/查看狀態只讀取資訊：需明確準備缺失的 Python，再檢查，然後檢查安裝摘要。執行環境設定要求 **Installer 安裝後仍有 320 MiB 可用空間**，另需尚未測量的電視安裝套件暫存空間。不代表新增型號/固件兼容性。

設定會安裝 Root Home 和 Root Updater；準備 System Updater 是明確的可選步驟。驗證後單獨啟用 Change Home；設定絕不清除緊急停止或關閉狀態。經驗證的現有安裝可在 cytv/電視之間共享組態和恢復狀態，無需重裝或重置。未知舊基礎設施需先診斷；安裝套件偏好導入僅供首次設定，不用於瀏覽器儲存或基礎設施遷移。

中斷後先檢查狀態。只有原始快照/租約仍存在且最終回讀已確認時才顯示“繼續”。其他階段需要檢查狀態、恢復或診斷；原始碼 CLI 可明確恢復更多已識別階段。cytv 的“完成 Root 設定”不會重啟未完成的工作進程。不要刪除日誌或盲目重試。Homebrew 只更新 Installer；現有更新程式負責產品更新/已簽名完整發行集。刪除 Installer 不會刪除產品。

明確的完整移除會恢復 LG Home 並清理本項目的啟動鈎子，同時保留獨立恢復/歸檔證據及引用中的 Python 槽位。此路徑所有實機檢查仍待完成；上文 Root 0.2.0 的 C3 歷史結果不能驗證 Homebrew 設定。

啟動使用由收據標識歸屬的私有包裝指令碼，僅將已安裝套件的身分資訊作為資料檢查，不執行套件內的啟動指令碼。套件遺失或不安全時停止自動重新啟用；獨立復原仍可還原 LG Home。檢查可能短暫地在私有目錄暫存已驗證檔案，不會變更 Home 或產品。

[候選版設定與恢復（英文）](../INSTALL.md#candidate-on-tv-root-installation) · [待完成實機驗收（英文）](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


此原始碼候選版中，現有 Root 安裝需要經過驗證的復原和重新設定，才能取得修正後的私有執行環境。只更新 Installer 不會取代它。請保留復原記錄，並且只透過正常設定流程或設定頁面啟用 Home。

僅適用於下一候選版本：No-root 設定 → 開發者模式 → 顯示診斷會提供安全的儲存和 Home RPC 錯誤分類及實際服務版本。查看診斷不會啟用自動續期或啟動 Helper。狀態檢查失敗不代表 Helper 已停止。C5 上的修復尚未確認；參閱[診斷說明（英文）](../SETTINGS-DIAGNOSTICS.md)。

報告會取得遙控器焦點。上/下鍵捲動，左/右鍵或 OK 返回相鄰操作，返回鍵回到 Home 設定。

**尚未發布，#82：** 如果缺少 Home 設定，明確啟動的 Root 安裝可以將其設為 LG Home，並重新讀取驗證，然後完成復原準備。Status/doctor 不會寫入設定。結果不確定的寫入不會重複，請保留復原資料。解除安裝後明確的 LG Home 設定仍會保留。此韌體仍需實機測試。

## 未發佈候選版本：HDMI 聲音恢復（Root）

Home 設定 → HDMI 聲音提供 eARC 重新連接和已確認的 HDMI 輸出恢復。僅 ARC、
組合/WOW Orchestra 及未知模式會略過。開機/待機喚醒自動恢復是實驗功能，預設關閉；
需要支援的電源訂閱，可能中斷正常聲音。返回可關閉面板，清理仍會繼續。中斷後
請檢查狀態，僅在希望開啟 eARC 時恢復已儲存的設定。恢復 Home 或緊急停止會關閉
自動恢復，必須明確重新開啟。舊私有執行環境需要經過驗證的重新設定。尚未確認
電視相容性或聲音開始時間縮短。

[Device acceptance (English)](../development/ROOT-AUDIO-RECOVERY.md)

尚未發佈：專用 Python 檢查分別報告 ABI、目錄安全與空間不足。首次安裝需要 /var/lib 有 320 MiB 可用空間。較大的 WAM Session Storage 可能是原因；清除可能遺失應用程式工作階段狀態。請參閱[復原指南](../RECOVERY.md#private-python-and-low-var-space)。

在尚未發布的 1.4.0 候選版中，中斷的 No-root 安裝也可在**檢查電視狀態**後使用**恢復並重新安裝**。只有確定要移除 Clean Your TV 應用程式時才確認移除，然後在重新安裝前檢查版本。如果恢復失敗，請儲存該次診斷報告並停止操作。電視最初拒絕安裝套件的原因仍未確定，也尚未確認已修復（#21）。


**尚未發佈 — WAM:** `cytv clean-wam-cache --edition root`. 只請求 cache 和 codecache。不會清理 Session Storage、cookies、Local Storage、Service Worker 和 databases。 請先關閉電視應用程式。快取會重新下載或建立；下次啟動可能需要更多時間。 [WAM](../WAM-CLEANUP.md).

可以取消並自行清理空間。請按手動指南操作並再次檢查 /var/lib；刪除應用程式可能只清理其他分區。 **Session Storage (SSH):** 請先關閉電視應用程式。這會刪除工作階段狀態，可能登出帳號或遺失未儲存的資料。 [WAM](../WAM-CLEANUP.md#free-space-yourself-instead).

尚未發布的 Root 冷啟動修正：啟用 Home 控制且 LG 開機畫面設為 Home 時，保護檢查成功後，若仍顯示電視直播或 LG Home，可請求開啟 Clean 一次。最後一次畫面檢查時已顯示的其他應用程式會保留，不會重試。手動關閉及連按三次 Home 的緊急關閉狀態保持不變。需要透過已驗證的安裝或更新替換私有執行環境，僅更新應用程式並不足夠。修正版的電視驗證仍待完成。

[Cold-start investigation and acceptance (English)](../development/ROOT-COLD-BOOT.md)

OTA 修復候選（#115）：1.3.0 原版 System Updater 因允許的檔案清單變化而無法安裝 1.4.0。替換前中止不等於部分安裝。請保留復原記錄，不要重試、清除狀態或修改路徑清單。下個候選保留 1.3.0 的路徑和權限契約；電視上的升級與回退仍需協調測試。

尚未發佈的修正（#108/#109）：準備好 System Updater 後，更新指示點與「全部更新」使用同一版本類別檢查。若只有整體發佈版本變更、所有元件版本均相同，則不會建議重新安裝。檢查期間無法安裝。僅在 System Updater 不存在時使用舊版檢查。仍待實際電視確認。

尚未發佈的 #110 診斷：SSH root 存取不會自動授予 Home 呼叫 Homebrew 設定 API 的權限。介面區分存取遭拒、服務無法使用、服務未以 root 執行、逾時和不支援的回應。若存取遭拒，請在 Homebrew Channel 中變更設定。在 webOS 11 上，Homebrew 0.7.3 的權限可能阻止應用程式呼叫；仍需受支援的權限解決方案。不會自動變更權限或封鎖設定。
