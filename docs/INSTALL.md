# 高级安装与存档回退

首次安装按[玩家说明](玩家安装.txt)或[服主说明](服主安装.txt)操作。本页供已有其他 Mod、使用托管面板或需要更新和回退的服主查阅。装完前置的现场自检、已复现的故障和崩溃 dump 的读法见[排查与踩坑记录](TROUBLESHOOTING.md)。

## 定位实际运行的加载器

Linux 宿主应先确认进程是 Wine 下的 Windows 版 PalServer。原生 Linux 专服加载本包前置的链路尚未验证。示例容器可能在启动时更新依赖，排查时请记下实际游戏与加载器构建。[官方支持平台](https://github.com/pocketpairjp/PalworldModUploader/blob/main/PalworldModUploader/docs/en/01-General.md) · [Wine 示例](https://github.com/thijsvanloef/palworld-server-docker/blob/main/examples/mods/compose.yaml)

双端各将 ZIP 内的 `Pal/` 合并到运行游戏的根目录，石像表实际位置为 `Pal/Content/Paks/~mods/PalSoulCap80_P.pak`。容器要将这个文件部署到重建后仍可恢复的位置。回退旧包时移走这份 PAK，再恢复对应备份。

仓库的 `安装包/前置/` 直接放了两份已核对的前置压缩包：`UE4SS-Palworld-g2281fa31.zip` 与 `PalSchema_0.6.71.zip`，SHA256 记在[排查与踩坑记录](TROUBLESHOOTING.md)。服务器上直接取这两份即可，不必再去 GitHub 找，避免下成上游版或漏掉 `MemberVariableLayout.ini`。

每端选一套前置。安装包里的 `Mods/` 与 UE4SS 实际使用的同名目录合并。PalSchema 固定从 UE4SS 工作目录下的 `Mods/PalSchema/mods/` 读取共享数据；托管面板的额外 Lua 搜索路径只影响脚本。可通过活动目录中的 `PalSchema/mods/PalArenaImplants/raw/surgery.json` 核对层级和大小写。[PalSchema 加载器](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalMainLoader.cpp#L115-L120)

| 现有前置 | 运行目录与配置 |
| --- | --- |
| 手工安装 | 普通版 `UE4SS-Palworld-g2281fa31.zip` 根目录中的 `dwmapi.dll` 和整个 `ue4ss/` 放入 `Pal/Binaries/Win64/`。`PalSchema_0.6.71.zip` 根目录只有 `PalSchema/`，将其放进 `Pal/Binaries/Win64/ue4ss/Mods/`。[UE4SS 2281fa31](https://github.com/Okaetsu/RE-UE4SS/releases/tag/2281fa31) · [PalSchema 0.6.71](https://github.com/Okaetsu/PalSchema/releases/tag/0.6.71) |
| 据点工作帕鲁 80 的选项上限 | 原版把世界设置取值锁在 50，需要第三方 pak 覆盖 `BP_PalOptionSubsystem`（如 [Starkys 100 base pals](https://www.nexusmods.com/palworld/mods/5857)），**双端**放进 `Pal/Content/Paks/~mods/`，再把 `BaseCampWorkerMaxNum` 设为 80。[本组件说明](../mods/shared/PalBaseCampCap/README.md) |
| thijsvanloef Wine 容器的 Mod 管理器 | 该镜像自行部署 GitHub UE4SS 与工坊 PalSchema。把服务端 ZIP 的整个 `Mods/` 放在持久卷的 `Mods/NativeMods/PalworldServerPack/` 下，运行容器的 `mods-update` 或启用其启动同步。最终运行目录是 `/palworld/Pal/Binaries/Win64/ue4ss/Mods/`。已有独立实例可沿用原安装方式。[部署脚本](https://github.com/thijsvanloef/palworld-server-docker/blob/main/scripts/mods/update.sh) · [容器 Mod 配置](https://github.com/thijsvanloef/palworld-server-docker/blob/main/examples/mods/compose.yaml) |
| Steam 工坊客户端 | 订阅、启用前置并完整重启，活动目录为 `<游戏根>/Mods/NativeMods/UE4SS/Mods/`。[UE4SS](https://steamcommunity.com/sharedfiles/filedetails/?id=3625223587) · [PalSchema](https://steamcommunity.com/sharedfiles/filedetails/?id=3625280368) |
| 工坊前置的 Windows 专服 | 从 `steamapps/workshop/content/1623730/` 取两个订阅目录，放入 `<服根>/Mods/Workshop/`，各目录直接包含 `Info.json`，且安装规则带有 `IsServer: true`。首次启动临时服生成 `Mods/PalModSettings.ini` 后关服，在 `[PalModSettings]` 中设 `bGlobalEnableMod=true`，每个前置单列一行 `ActiveModList=<其 PackageName>`。重启后用 `Mods/ManagedMods/<PackageName>/InstallManifest.json` 核对部署，活动目录为 `<服根>/Mods/NativeMods/UE4SS/Mods/`。[官方专服步骤](https://docs.palworldgame.com/settings-and-operation/mod/) |

两条工坊订阅公开了不同的更新时间。PalSchema 工坊最近一条公开说明对应 GitHub 0.6.7 的外观修复，GitHub 0.6.71 又更新了签名。核对工坊实际装入的版本时，查看活动 `Mods/` 上一级的 `UE4SS.log`，搜索 `by Okaetsu loaded.`。若只有脚本启动记录而词条和商店都缺失，再检查 `Mods/PalSchema/dlls/main.dll` 与 UE4SS 同目录下的 `MemberVariableLayout.ini`。上游源码会在缺少该布局文件时中止 PalSchema 初始化。工坊更新后仍然加载旧版本时，按作者指引重新订阅，再查看实际版本和临时世界里的商品。[工坊变更](https://steamcommunity.com/sharedfiles/filedetails/changelog/3625280368) · [GitHub 0.6.71](https://github.com/Okaetsu/PalSchema/releases/tag/0.6.71) · [初始化与版本日志](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/dllmain.cpp#L19-L56)

从手工安装切到工坊时，先将旧手动 UE4SS 的加载入口 `dwmapi.dll` 或 `xinput1_3.dll` 移出 `Pal/Binaries/Win64/`。已核对的 UE4SS 普通版自带帕鲁的 `MemberVariableLayout.ini`，对象数组缓存和图形控制台默认关闭，可以保留包内设置。[UE4SS 工坊作者说明](https://steamcommunity.com/sharedfiles/filedetails/?id=3625223587) · [设置说明](https://pwmodding.wiki/docs/users/ue4ss/configuration)

Wine 手装后如果没有日志或服务刚监听端口就崩溃，先在临时实例只装两项前置，核对生效的 Wine 构建、启动服务的 `WINEDLLOVERRIDES` 和 DLL 目录。2026 年 2 月的上游记录涉及 Wine Staging 11.1，早于本包核对的 2281fa31。报告人改用 Proton Experimental 和当时的 Palworld 专用 UE4SS 后，在原始目录结构下成功加载。Linux 宿主使用现有 Wine 容器时应沿用其运行环境。[上游问题与后续复测](https://github.com/UE4SS-RE/RE-UE4SS/issues/1189) · [容器启动环境](https://github.com/thijsvanloef/palworld-server-docker/blob/main/scripts/start.sh#L89-L117)

## 配置、更新和回退

- 新服停服后，若 `Pal/Saved/Config/WindowsServer/PalWorldSettings.ini` 缺失或为空，将服根的 `DefaultPalWorldSettings.ini` 复制为该文件。已有非空配置时保留原文件。从目标文件的 `OptionSettings` 中启用 `bAllowClientMod=True`。若面板会重写配置，在面板中设置。PalSchema 的 `config/config.json` 保持 `enableAutoReload=false`，更新后完整重启，避免重复追加竞技场商品。[专服参数](https://docs.palworldgame.com/settings-and-operation/configuration/)
- 两端组件由各目录的空 `enabled.txt` 启用。玩家包安装钓鱼、滑翔伞和自动去雾脚本。专服包不再包含 Lua 脚本，只用 PalSchema 共享数据与石像 PAK。[UE4SS 加载顺序](https://github.com/Okaetsu/RE-UE4SS/blob/2281fa31/UE4SS/src/UE4SSProgram.cpp#L1466-L1564)
- Linux 服主可在停服和部署完成后，从独立解压的服务端包运行 `python3 检查植入物.py --mods-dir "/实际路径/Mods/PalSchema/mods"`。工具把活动目录中的 PalSchema 共享文件与安装包逐字节比对，并检查其他 PalSchema raw 文件对竞技场库存和手术配方的修改。将备份移出加载器扫描目录，尤其是整份旧的竞技场组件。临时服冷启动后再运行 `python3 检查植入物.py "/实际路径/UE4SS.log"`，核对 14 个植入物的登记，以及日志里已出现的五张核心表加载错误。购买、扣款、词条及重启后的保留需要旧档副本联测。[PalSchema 目录扫描](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalMainLoader.cpp#L115-L128) · [物品登记](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalItemModLoader.cpp#L80-L110)
- 如需专服定期备份，可在实际生效的 `OptionSettings` 中启用 `bIsUseBackupSaveData=True`，启动后在世界存档目录检查 `backup/` 是否生成。更新前的离线副本另存到服务器目录外，便于回到更新前的时间点。[官方专服配置](https://docs.palworldgame.com/settings-and-operation/configuration/)
- 更新前停服、退出游戏，将完整 `Pal/Saved/` 备份到游戏目录外，另存双端正在使用的整合包、实际加载的前置和 Mod 启用配置。使用容器部署时一起保留对应部署源。玩家若用过地图也备份对应世界的 `LocalData.sav`。将本包的旧 Lua 组件以及 `PalSchema/mods/` 里的 `PalSoulCap80`、`PalTrust99`、`PalArenaImplants`、`PalFishingWin` 移出后再装新版。保留 PalSchema 前置和其它作者的组件。
- 先开临时世界，用已更新的玩家端检查商店、词条和手术台。已有存档使用副本验证。若 `UE4SS.log` 出现植入物 ID 后接 `is invalid. Deleting.`，先停服核对双端物品表与前置，继续保存可能丢失物品。重复商品或数值异常时，检查同功能 Mod。[物品加载机制](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalItemModLoader.cpp#L457-L574)
- 回退时停服并退出客户端，把当前 `Pal/Saved/` 移到服务器目录外，再将整份备份恢复至原位置。升级前的备份若已使用本包，双端恢复当时的组件及前置后再开服。恢复至首次装本包前的备份时，移出本包组件，清理手动添加的本包 Lua 启用项，保留其他 Mod 的前置。客户端需要还原探索记录时恢复同一世界对应的地图副本。后续验证见[游戏内验收](GAME_CHECKS.md)。
