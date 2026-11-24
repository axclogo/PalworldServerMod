# 基地掉落物合并

双端包各自的 `Mods/PalSchema/mods/PalGroundStacks/` 将原生合并距离设为 500 厘米。服务端包的 `Mods/PalGroundStacksRuntime/` 随附 `enabled.txt`。服务端每 15 秒从当前世界的基地名册读取已登记的基地，打开各基地和原生距离档位的合并开关。新建或刚载入的基地可能要等下一轮，实际堆叠时机由游戏决定。单机或房主联机时，房主从服务端包加装这个脚本目录。安装路径见各自 ZIP 根目录的 `安装说明.txt`。

只覆盖基地范围，不是全地图自动合并。不同物品是否可合并、堆叠容量、数量转移和搬运均交给游戏原生逻辑；本包不自行删除、生成或复制掉落物，不改变背包堆叠上限，不运行逐帧扫描。

运行脚本原位修改 `bMergeDropItems`，不重建或增加档位数组，不改变距离、更新间隔及 `bUpdateSimple`。这是为了保留实际游戏当前档位结构，避免旧 Mod 的固定数组大小与新游戏不匹配。

需在测试服验证：基地内 5 米附近同类掉落物数量守恒；不同类不混合；搬运与人工拾取正常；近处玩家、远离基地后返回、重启后重新掉落均能合并；同时比较大量生产时帧耗时。范围外不生效属于当前边界。不能仅凭开关已改就承诺性能提升。禁用其它覆盖相同距离和档位设置的 Mod。

参考：[Super Stacks No Lag 作者说明](https://steamcommunity.com/sharedfiles/filedetails/?id=3770035710)、[原生基地管理器](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/PalBaseCampManager.h)。运行脚本独立实现，没有复制上游成品。
