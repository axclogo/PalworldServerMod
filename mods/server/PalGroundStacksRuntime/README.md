# 基地掉落物合并脚本

服主按 `安装包/幻兽帕鲁-服务端.zip` 根目录的 `安装说明.txt` 合并 `Mods/`。UE4SS 通过 `Mods/PalGroundStacksRuntime/enabled.txt` 启动基地脚本。两端的 `Mods/PalSchema/mods/PalGroundStacks/` 提供 5 米距离参数。单机或房主联机时，房主先装玩家端包，再从服务端包加装 `Mods/PalGroundStacksRuntime/`。

脚本每 15 秒从当前世界取得基地管理器和基地名册，只写入尚未开启的 `bMergeDropItems`。名册中的 `BaseCamp` 直接指向基地实例。基地尚未加载或已经移除时跳过，下次检查读取当时的名册。工作间隔、简化更新及其它字段沿用原版，此操作不写玩家存档。[原生基地名册](https://github.com/localcc/PalworldModdingKit/blob/e6632458/Source/Pal/Public/PalBaseCampRepInfo.h) · [社区基地合并实现](https://github.com/tsk-yagi/EnhancedBaseLogistics#dropped-item-merging)

新建或刚载入的基地在下一次检查时开启合并。两堆物品实际合并仍由游戏调度。基地内外、搬运及数量守恒的验收步骤见[联机验收](../../../docs/GAME_CHECKS.md)。
