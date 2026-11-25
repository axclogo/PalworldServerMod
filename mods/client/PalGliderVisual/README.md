# 帕鲁滑翔伞

玩家包默认启用。把天擒鸟放进队伍，装备一把普通滑翔伞，起跳后在空中再按一次跳跃展开。游戏选中天擒鸟时，伞面应显示天擒鸟。鲁米儿等滑翔搭档同理。喷气背包沿用游戏自身的外观。

玩家端同时识别角色和专属装备的滑翔展开事件。角色的搭档编号晚到时，专属伞可以按游戏已经生成的装备识别对应物种，普通伞则读取游戏选中的搭档。已核对原版的 35 个装备类，包括每档的 `XXX_TierN_C` 和各物种的 `XXXBase_C`（含 `WindChimes_Ice_Base_C`、`FlyingManta_ThunderBase_C`），`Item_Base_C` 是普通伞基类不计入。游戏为每个物种另备了伞面网格（天擒鸟是 `SK_Glider_Eagle`，与本体 `SK_Eagle` 不是同一份资源），伞面组件自带 90° 翻滚，角色网格不能继承这个旋转；脚本换模后按 `ADJUST` 表写入绝对相对旋转与父空间偏移，天擒鸟实测为 `pitch=-90, yaw=-90, roll=0, x=20, y=150, z=0`（2026-11-26 实机确认），收伞时按 `snapshot` 记录还原网格、材质、位置、朝向与缩放。找不到匹配的飞行动画时仍会恢复骨架更新。普通伞重复刷新相同外观时不重复换模，移走搭档时恢复原有模型和材质。首次实际展开一个尚未加载的物种仍可能短暂停顿。

只需更新玩家端。每位玩家的客户端负责自己画面上的外观。天擒鸟的姿态与位置已实机确认；其它物种（鲁米儿、飞螳、妖恋蝠）与远程玩家视角仍按各自物种需要单独核对握点。[游戏滑翔组件](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalGliderComponent.h) · [滑翔蓝图事件](https://github.com/itzzjunny/PALWORLD/blob/master/SDK/BP_GliderComponent_classes.hpp) · [社区作者的 1.0 版本说明](https://www.nexusmods.com/palworld/mods/2454?tab=files)
