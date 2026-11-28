# 鎺掓煡涓庤俯鍧戣褰?
鎸夌幇鍦哄鐜扮殑椤哄簭璁板綍宸茬‘璁よ繃鐨勬晠闅滐細鐜拌薄銆佽瘉鎹€佹牴鍥犮€佸缃€佸楠屻€傚彧鍐欏疄娴嬭兘寰楀埌鐨勪笢瑗匡紝鏈鐜扮殑鐚滄祴涓嶈繘杩欓噷銆傝瀹屽墠缃殑鐜板満鑷瑙佹枃鏈竻鍗曘€?
## 閫熸煡

| 鐜拌薄 | 鏍瑰洜 | 澶勭疆 |
| --- | --- | --- |
| 鍚姩鏁扮鑷充簩鍗佺鍐呴€€鍑猴紝鍚屼竴涓敊璇鍙嶅鍑虹幇锛宍ue4ss` 涓嬫柊澧?`crash_*.dmp` | UE4SS 鐢ㄤ簡涓婃父 4.0.0锛屼笉鏄笗椴佸垎鏀?2281fa31 | 鏁村鎹㈠洖 2281fa31锛屽苟琛?`ue4ss\MemberVariableLayout.ini` |
| 娓告垙鑳借繘锛屼絾淇¤禆銆佹鍏ョ墿銆侀挀楸煎弬鏁板叏鏃犳晥鏋?| `Mods\PalSchema` 鍙湁 `mods/` 鏁版嵁锛岀己 `dlls/main.dll` | 鍙﹁ PalSchema 0.6.71 鐨?`dlls`锛屼笌鍖呭唴 `mods/` 鍚堝苟 |
| `Mods\NativeMods\UE4SS` 鍙墿 `Mods/` 鍜屾棩蹇楋紝娌℃湁 DLL | 宸ュ潑鍓嶇疆涓庢墜宸ュ墠缃苟瀛樿繃锛屽垏鎹㈡椂娌℃湁娓呯悊 | 绉昏蛋璇ョ洰褰曪紝涓ょ閮藉彧淇濈暀涓€濂楀墠缃?|

## 2026-11-25 瀹㈡埛绔惎鍔ㄥ嵆宕?
**鐜拌薄銆?* 鍚姩鍚庢暟绉掕嚦浜屽崄绉掑唴杩涚▼閫€鍑猴紝鐢ㄦ埛鐪嬪埌鍚屼竴涓敊璇杩炵画鍑虹幇涓ゆ锛宍Pal\Binaries\Win64\ue4ss` 涓嬫柊澧炰袱浠?`crash_*.dmp`銆俙UE4SS.log` 姣忔閮藉仠鍦?`Mod 'PalFishingWin' has enabled.txt, starting mod.`锛屼箣鍚庢病鏈?`Event loop start`銆?
**鐜板満銆?* 鍔犺浇鍣ㄤ负 `UE4SS - v4.0.0 - Git SHA #30afe5ff`锛屽嵆涓婃父 RE-UE4SS 鏋勫缓锛沗ue4ss` 鐩綍閲屾病鏈?`MemberVariableLayout.ini`锛涙父鎴忎晶鍙︽湁 11 鏈?14 鏃ュ伐鍧婂墠缃暀涓嬬殑 `Mods\NativeMods\UE4SS` 娈嬬己鐩綍銆?
**璇佹嵁銆?* 涓や唤 dump 鐨勫紓甯歌褰曞畬鍏ㄤ竴鑷达細`0xC0000005` 璇诲湴鍧€ `0x1`锛屾寚浠や綅浜?`VCRUNTIME140.dll+0x1dc0d`銆傚穿婧冩椂鍒讳笌鏃ュ織鏈€鍚庝竴琛?`starting mod` 钀藉湪鍚屼竴姣銆?
**璇垽杩囩▼銆?* 鍋滅敤 `PalFishingWin` 鍚庢父鎴忔甯歌繘鏍囬锛涙妸 `main.lua` 鎹㈡垚绌鸿剼鏈€佸彧鐣?`StaticFindObject`銆佸彧鐣欐灇涓惧潡銆佸彧鐣?`RegisterHook`锛屼篃閮戒笉宕┿€傝繖鍥涚鏀规硶閮藉彧鏀瑰彉缁勪欢娉ㄥ叆鏃舵満锛屼笉鏄牴鍥狅細鍚屼竴浠藉師鑴氭湰鎹㈠埌 2281fa31 鍚庨挬瀛愯兘姝ｅ父娉ㄥ唽銆佹父鎴忔甯歌繘鏍囬锛岃鏄庤剼鏈湰韬病鏈夐敊銆傘€岀鐢ㄦ煇涓粍浠跺氨涓嶅穿銆嶅彧鑳戒綔涓虹缉灏忚寖鍥寸殑鎵嬫锛屼笉鑳藉綋缁撹銆?
**鏍瑰洜銆?* 甯曢瞾瑕佹眰 Okaetsu 鐨?Palworld 鍒嗘敮 UE4SS锛屽苟鍦?`ue4ss` 鍚岀洰褰曟彁渚?`MemberVariableLayout.ini`銆備笂娓告瀯寤哄湪璇ユ父鎴忔瀯寤轰笂鍚姩闃舵宕╂簝锛屼笌鏈寘缁勪欢鏃犲叧銆?
**澶勭疆銆?* 鏁村鏇挎崲鍓嶇疆锛屼笉娣疯锛氭妸 `UE4SS-Palworld-g2281fa31.zip` 鐨?`dwmapi.dll` 涓?`ue4ss/` 瑕嗙洊杩?`Pal\Binaries\Win64\`锛屼繚鐣?`ue4ss\Mods` 涓嬪凡鏈夌粍浠讹紱鎶?`PalSchema_0.6.71.zip` 鐨?`PalSchema/dlls` 骞跺叆 `ue4ss\Mods\PalSchema`锛涚Щ璧?`Mods\NativeMods\UE4SS`銆傛浛鎹㈠墠鎶婃棫鐨?`dwmapi.dll`銆佹暣涓?`ue4ss` 鐩綍鍜屾畫鐣欏墠缃浠藉埌娓告垙鐩綍澶栥€?
**澶嶉獙銆?* 鏃ュ織渚濇鍑虹幇 `UE4SS - v3.0.1 Beta #0 - Git SHA #2281fa31`銆乣PalSchema v0.6.71 by Okaetsu loaded`銆乣MemberVariableLayout.ini loaded`銆乣[Lua] [PalFishingWin] Fishing state hook registered`锛岃繘鏍囬鍚?55 绉掓棤宕╂簝銆?
涓嬭浇涓庢牎楠岋紙2026-11-25 瀹炴祴锛夛細

| 涓嬭浇椤?| 鍙栫敤鏂囦欢 | SHA256 |
| --- | --- | --- |
| [Palworld (2281fa31)](https://github.com/Okaetsu/RE-UE4SS/releases/tag/2281fa31) | `UE4SS-Palworld-g2281fa31.zip` | `F7543D57F8FDF5EAB3731AC52121E6E7FF142FB3BFA17156E931037D0E44875B` |
| [PalSchema 0.6.71](https://github.com/Okaetsu/PalSchema/releases/tag/0.6.71) | `PalSchema_0.6.71.zip` | `15FD72CCCF2F56F6D5737355D0EA0A911838A0E5BF4108470477266B85418195` |

`UE4SS.dll` 涓?`dwmapi.dll` 鏄悓涓€涓彂甯冩瀯寤洪噷鐨勪袱浠芥枃浠讹紝瀹炴祴涓ょ増 `dwmapi.dll` 鐨?SHA256 涓嶅悓锛屾浛鎹㈡椂鎴愬杩涜锛屼笉瑕佸拰鏃?proxy 娣风敤銆俒瀹夎灞傜骇](INSTALL.md) 路 [鍓嶇疆鐗堟湰瑕佹眰](https://okaetsu.github.io/PalSchema/docs/dev/gettingstarted) 路 [涓婃父鏋勫缓鐨勫凡鐭ユ晠闅淽(https://doodesch-mods.github.io/PalCodex/troubleshooting/compatibility-and-updates/)

## 2026-11-25 PalSchema 鍙湁鏁版嵁娌℃湁鍔犺浇鍣?
**鐜拌薄銆?* 鍓嶇疆鎹㈠涔嬪悗娓告垙鑳借繘锛屼絾淇¤禆銆佺珵鎶€鍦烘鍏ョ墿銆侀挀楸煎皬娓告垙鍙傛暟鍏ㄩ兘娌℃湁鏁堟灉锛屽彧鏈夊崌榄?PAK 鍦ㄨ捣浣滅敤銆?
**璇佹嵁銆?* `ue4ss\Mods\PalSchema` 涓嬪彧鏈?`mods/` 涓?`enabled.txt`锛屾病鏈?`dlls/main.dll`锛涙崲鍓嶇疆鍓嶇殑 `UE4SS.log` 閲岃繛 `Mod 'PalSchema'` 閮芥病鏈夛紝璇存槑鍔犺浇鍣ㄦ牴鏈病鍚姩銆?
**鏍瑰洜銆?* 瀹夎鍖?`Mods/PalSchema` 鍙槸鍏变韩鏁版嵁锛坄mods/` 涓嬬殑 raw銆乥lueprints銆乮tems銆乼ranslations锛夛紝涓嶆槸鍓嶇疆鏈綋銆傚畠蹇呴』骞跺叆宸茬粡瑁呭ソ鐨?PalSchema 0.6.71锛宍dlls/main.dll` 鐢卞墠缃崟鐙彁渚涳紱`build_pack.py` 鍙墦鍖呮暟鎹紝涓嶄細甯?DLL銆?
**澶勭疆銆?* 瑁?0.6.71 鐨?`PalSchema/`锛屽啀鎶婂寘鍐?`Mods/PalSchema/mods/` 鍚堝苟杩涘幓銆傚崌绾ф棫鍖呮椂鍙﹀绉昏蛋 `PalSchema/mods/PalSoulCap80` 鏃х洰褰曘€?
**澶嶉獙銆?* 鏃ュ織鍑虹幇 `Loader 'raw' initialized.` 绛変簲涓?loader 鍒濆鍖栵紝浠ュ強 `DT_FriendshipRankTable: 0 rows updated, 89 rows added`銆乣DT_OperatingTablePassiveSkillDataTable: 鈥?14 rows added`銆乣DT_PassiveSkill_Main_Common: 鈥?4 rows added`銆乣DT_ItemShopCreateData_Common: 1 rows updated`銆乣DT_ItemIconDataTable_Common: 鈥?14 rows added`锛?4 涓鍏ョ墿閫愭潯 `Added Item`锛岄厤缃嚜鍔ㄧ敓鎴愪笖 `enableAutoReload=false`銆?
## 宕╂簝 dump 鐨勮娉?
UE4SS 鑷繁鍐?dump锛屽墠鎻愭槸 `UE4SS-settings.ini` 鐨?`[CrashDump] EnableDumping = 1`锛堥粯璁ゅ紑鍚級銆傛病鏈?WinDbg 鏃跺彲鎸?MINIDUMP 缁撴瀯鐩存帴璇伙細

- 澶撮儴 `MDMP`锛屽亸绉?8 鏄祦鏁伴噺銆?2 鏄洰褰曞亸绉伙紱姣忎釜鐩綍椤?12 瀛楄妭锛屼緷娆′负娴佺被鍨嬨€佸ぇ灏忋€佸亸绉汇€?- 娴?6锛坄ExceptionStream`锛夌粰鍑哄紓甯哥嚎绋嬪彿銆佸紓甯哥爜鍜屾寚浠ゅ湴鍧€锛涙祦 4锛坄ModuleListStream`锛夋妸鍦板潃鏄犲皠鍒版ā鍧楀姞鍋忕Щ銆?- 璇诲湴鍧€鍦?`ExceptionInformation[1]`锛歚0xC0000005` 涓斿弬鏁颁负 `0, 0x1` 灏辨槸銆岃 0x1銆嶏紝閫氬父鏄┖鎸囬拡鍔犲亸绉绘垨閲庢寚閽堛€?- 娴?3锛坄ThreadListStream`锛夐噷璁板綍鐨勯偅涓€屽紓甯哥嚎绋嬨€嶅疄闄呮槸鍐?dump 鐨勭嚎绋嬶紝鏍堥噷鏄?`dbghelp`/`dbgcore` 鐨勫抚锛屼笉鑳藉綋宕╂簝璋冪敤鏍堢敤銆傚垽鏂緷鎹簲鏄紓甯哥爜銆佹ā鍧楀亸绉诲拰 `UE4SS.log` 鏈€鍚庝竴琛屼笁鑰呭榻愩€?- 宕╂簝鍚庣珛鍒诲己鍒剁粨鏉熻繘绋嬩細鐣欎笅 0 瀛楄妭鐨?`crash_*.dmp`锛岃繖绉?dump 娌℃湁淇℃伅锛屽埆鎷挎潵姣斿銆?
## 瀹㈡埛绔瀹岃嚜妫€

| 妫€鏌ラ」 | 閫氳繃鏍囧噯 |
| --- | --- |
| 鍓嶇疆鐗堟湰 | `UE4SS.log` 鍑虹幇 `v3.0.1 Beta #0 - Git SHA #2281fa31` |
| 甯冨眬鏂囦欢 | 鍚岀洰褰曞瓨鍦?`MemberVariableLayout.ini`锛屾棩蹇楀嚭鐜?`MemberVariableLayout.ini loaded` |
| PalSchema | 鏃ュ織鍑虹幇 `PalSchema v0.6.71 by Okaetsu loaded.`锛屽苟涓旀湁浜旇琛ㄥ啓鍏ヨ褰?|
| 瀹㈡埛绔粍浠?| 鏃ュ織鍑虹幇 `[PalFishingWin] Fishing state hook registered`锛宍PalGliderComponent` 涓変釜閽╁瓙娉ㄥ唽锛宍PalMapReveal` 鍚姩 |
| 鍖呮枃浠?| 19 涓枃浠朵笌鐜╁绔?ZIP 閫愬瓧鑺備竴鑷达紝`Pal\Content\Paks\~mods\PalSoulCap80_P.pak` 瀛樺湪 |
| 娈嬬暀 | `Mods\NativeMods\UE4SS` 涓嶅瓨鍦紝`ue4ss` 涓嬫病鏈夋棫鐨?`crash_*.dmp` |

鑷閫氳繃鍙唬琛ㄥ姞杞介摼鍜屾暟鎹啓鍏ユ纭紝璐拱銆佹墜鏈€佸崌榄傛墸鏂欍€佸幓闆俱€佹粦缈斿瑙傚拰閽撻奔缁撶畻浠嶆寜[娓告垙鍐呴獙鏀禲(GAME_CHECKS.md)鍦ㄥ疄鏈烘牳瀵广€?
## UE4SS 3.0.1 在本机的能力边界

排查滑翔外观时逐个试出来的结论，写下来避免重复踩：

| 能力 | 结果 | 影响 |
| --- | --- | --- |
| `KismetSystemLibrary:PrintString` | 调用成功但不显示（`屏幕打印方式=不可用`） | 不能用它做游戏内提示，只能看 UE4SS 控制台或 `UE4SS.log` |
| `K2_SetWorldLocationAndRotation` | 不可调用 | 不能用世界坐标摆放组件，只能写相对属性 |
| Lua `Key` 枚举 | 没有 `Insert`/`Delete`/`Home`/`End`/`PageUp` | 绑定这些键会静默失败，必须用 `F1`–`F12` 这类确实存在的名字 |
| `F5` | 绑定成功但不触发 | 换项不要用 F5；`F6`/`F7`/`F8`/`F9`/`F10`/`F1`–`F4` 实测可用 |
| 外部控制台窗口 | 由代理启动时出现，Steam 正常启动时不出现 | 需要画面外反馈时，看 `UE4SS.log` 最稳 |

改 `main.lua` 之后**先用离线测试解析一遍再装**：Lua 语法错误会让整个组件不加载，日志里只有一行 `Error loading script: ... ')' expected near '['`，游戏里表现为该 Mod 完全没生效（例如滑翔伞连原版伞面都不见了）。

## 2026-11-26 无限秘药随包后滑翔伞异常（已回退，原因未隔离）

**现象。** 在玩家端包里加入 `PalElixirUncap`（只有一个 blueprint JSON）后，天擒鸟滑翔伞出现异常；换回不含它的包后恢复正常。

**对比结论。** 含秘药与不含秘药的两份玩家端包，除该 JSON 外 19 个文件**逐字节相同**，包括 `PalGliderVisual/Scripts/main.lua`（11635 字节）。所以不是滑翔脚本被改坏。

**另一个同时发生的变量。** 核对本地安装时发现 12 个文件仍是 11-25 首次安装的旧版本（比包内小），本次一并覆盖成包内版本。因此"恢复"可能来自「去掉秘药」或「补齐旧数据」两者之一，尚未隔离。

**处置。** 秘药组件移到 `mods/parked/PalElixirUncap/`，不再进入打包清单（`check_implant_log.SHARED`）；玩家端包重新生成后与那个可用的包逐字节一致。README 功能表、`GAME_CHECKS` 与 `ACCEPTANCE` 同步：该项记为暂缓。

**隔离方法。** 在已确认正常的包上，只把 `elixir_cap.json` 放回 `PalSchema/mods/PalElixirUncap/blueprints/`，重启复测天擒鸟；正常则说明与秘药无关，异常则说明需要换实现（社区同类模组走的是客户端蓝图逻辑/Lua，而不是 PalSchema 数据）。

## 2026-11-28 据点工作帕鲁：等级表补丁有效，选项上限的蓝图属性名未找到

**已证实有效的部分。** `DT_BaseCampLevelData` 的 raw 补丁能正常加载，PalSchema 日志：

```
[PalSchema] DT_BaseCampLevelData: 1 rows updated, 0 rows added, 0 rows deleted, 0 errors.
```

**未解决的部分。** 原版把世界设置 `BaseCampWorkerMaxNum` 锁在 50，需要改 `BP_PalOptionSubsystem`。按社区模组公布的写法尝试：

```json
{ "BP_PalOptionSubsystem_C": { "OptionWorldStaticSettings.BaseCampWorkerMaxNum.Max": 80 } }
```

日志给出：

```
[PalSchema] Loaded changes to BP_PalOptionSubsystem_C
[PalSchema] [warning] Property 'OptionWorldStaticSettings.BaseCampWorkerMaxNum.Max' does not exist in BP_PalOptionSubsystem_C
```

类能被找到，属性路径不对。该补丁已移到 `mods/shared/PalBaseCampCap/pending/`（PalSchema 不扫描该目录，不进包），备选写法见该目录 README。

**取正确属性名的办法。** 解包社区成品 pak（如 `StarkyBase100_P.pak`）读其 uasset 属性名表，无需启动游戏。
