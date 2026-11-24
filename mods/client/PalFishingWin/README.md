# 钓鱼必中

玩家正常抛竿。本机玩家的鱼竿进入咬钩状态 `WaitHit` 时，脚本调用原生提竿输入。游戏接管随后的小游戏、扣饵、战利品和入库。两位玩家各自在自己的客户端处理提竿。[原生鱼竿接口](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalFishingComponent.h) · [自动提竿的社区实测](https://github.com/lbcamargo94/palworld-mods/blob/c392e874/lua/BetterFishing/Scripts/main.lua#L495-L530)

玩家端和服务端的 PalSchema 各装同一份[小游戏参数](../../shared/PalFishingWin/blueprints/catch_battle.json)。它只调整 `BP_PalFishingSystem_C` 的三个进度字段，目标量为 1、默认进度量为 1、失误变化量为 0。PalSchema 按字段写入结构体，另外 16 个字段沿用游戏值。鱼种、钓点、奖励和鱼饵继续使用各自的原版配置。公开 SDK 声明了这些字段，社区 1.0 的数据版也验证过由原生小游戏判胜的路线。本包这组数值在目标游戏构建上的胜负判定仍待联机验证。[蓝图映射](https://github.com/PalworldModding/UsefulFiles/blob/acdf1a6a6076f84fae3275e7c1cdd08188994da8/Mappings.usmap) · [钓鱼系统](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalFishingSystem.h#L42-L44) · [结构字段](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalFishingCatchBattleParameter.h) · [PalSchema 结构写入](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/SDK/Helper/PropertyHelper.cpp#L351-L375) · [社区数据版作者说明](https://www.nexusmods.com/palworld/mods/3798?tab=description)

脚本启动时按游戏枚举中的名字读取 `WaitHit` 的值。若更新后找不到这个名字，日志会显示 `WaitHit missing`，本次启动仍可手动提竿。[UE4SS 枚举接口](https://github.com/Okaetsu/RE-UE4SS/blob/2281fa31/UE4SS/src/LuaType/LuaUEnum.cpp#L63-L98)

## 安装与游戏内确认

两端各按自己 ZIP 里的安装说明复制 `Mods/`。在双方活动目录中均能找到 `PalSchema/mods/PalFishingWin/blueprints/catch_battle.json`，玩家端另有 `PalFishingWin/Scripts/main.lua` 与启用标记。测试时两人各自用饵，正常抛竿，其中一人先取消再抛。观察咬钩后能否放开操作、由游戏完成小游戏，再核对背包或帕鲁终端与扣饵数量，重连复核。

玩家端的 `Mods/PalFishingWin/THIRD_PARTY_NOTICES.md` 收录了 BetterFishing 的署名和 MIT 许可。
