# 帕鲁滑翔伞

玩家包默认启用。把天擒鸟放进队伍，装备一把普通滑翔伞，起跳后在空中再按一次跳跃展开。游戏选中天擒鸟时，伞面应显示天擒鸟。鲁米儿等滑翔搭档同理。喷气背包沿用游戏自身的外观。

玩家端同时识别角色和专属装备的滑翔展开事件。角色的搭档编号晚到时，专属伞可以按游戏已经生成的装备识别对应物种，普通伞则读取游戏选中的搭档。已核对原版的 35 个装备类，包括首档直接使用基础蓝图的搭档 `WindChimes`。模型和材质取自该物种。天擒鸟、鲁米儿等专属伞在播放适配的飞行动画时开启骨架更新，收伞时恢复原来的更新开关。普通伞重复刷新相同外观时跳过重复换模，移走搭档时恢复普通伞的模型和材质。首次实际展开一个尚未加载的物种仍可能短暂停顿。

只需更新玩家端。每位玩家的客户端负责自己画面上的外观。模型握点、具体物种动画和远程玩家视角还没有经过修订后的 Windows 游戏验证。[游戏滑翔组件](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalGliderComponent.h) · [滑翔蓝图事件](https://github.com/itzzjunny/PALWORLD/blob/master/SDK/BP_GliderComponent_classes.hpp) · [社区作者的 1.0 版本说明](https://www.nexusmods.com/palworld/mods/2454?tab=files)
