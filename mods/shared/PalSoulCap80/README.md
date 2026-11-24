# 升魂 80

生命、攻击、防御、工作速度分别能在石像升至 80 级。双端使用同一个 `PalSoulCap80_P.pak`。包内只有游戏的石像数据表，包含原版 1–20 级和本包的 21–80 级。升级、扣料、属性计算和存档都继续走游戏本身的逻辑。

Steam 专服 Build 25247047 的石像表访问器第一次查询上限时遍历行的 `Rank`，缓存最大值，后续查询直接返回缓存。把完整表作为游戏资源挂载后，第一次读取就含第 80 级。社区作者用同一张表发布了最高 255 级的方案。四项存档字段均可表示 80。游戏内扣料、属性和重启结果仍待联机验证。[社区作者说明](https://www.nexusmods.com/palworld/mods/3940) · [存档字段](https://github.com/localcc/PalworldModdingKit/blob/e6632458b97af0083eb81715775651b08104ef6a/Source/Pal/Public/PalIndividualCharacterSaveParameter.h)

## 材料规则

按目标等级计算下表费用。每个属性独立付费；例如从 20 升到 21，消耗 10 个究极帕鲁之魂。

| 目标等级 | 每级究极帕鲁之魂 |
| --- | ---: |
| 1–20 | 沿用原版 |
| 21–25 | 10 |
| 26–30 | 12 |
| 31–35 | 14 |
| 36–40 | 16 |
| 41–45 | 18 |
| 46–50 | 20 |
| 51–55 | 22 |
| 56–60 | 24 |
| 61–65 | 26 |
| 66–70 | 28 |
| 71–75 | 30 |
| 76–80 | 32 |

新增等级使用最高档的究极帕鲁之魂 `PalUpgradeStone4`（英文 Giant Pal Soul）。原版第 20 级消耗 4 个究极魂；新增等级从 10 个起，每 5 级增加 2 个，末档为 32 个，不采用指数增长。材料按用户要求改为最高档，既定数量保持不变。可用原版设施兑换魂，不新增兑换配方。名称见 [究极帕鲁之魂](https://op.gg/zh-cn/palworld/items/palupgradestone4)。

在公开游戏导出中，石像表是普通 DataTable，共 20 行，第 20 行的等级、魂 ID、数量和重置参数分别是 `20`、`PalUpgradeStone4`、`4`、`30000`。社区作者发布过 33 级和 255 级石像扩展。它们支持继续以数据表扩展为实现方向；不同游戏构建和专服仍要以石像真实扣料、存档重载为准。[原版石像表](https://github.com/Dhampyru/Palworld-Extracted/blob/d38105b4dc0cf6f36c5035997fbe54205bb2d753/Pal/Content/Pal/DataTable/Character/DT_CharacterUpgradeMasterDataTable.json) · [33 级方案](https://www.nexusmods.com/palworld/mods/2718?tab=description) · [255 级方案](https://www.nexusmods.com/palworld/mods/2068?tab=files)

单属性 20→80 共需 **1260 究极魂**；四属性均从 20→80 共需 **5040 究极魂**，不含 1–20 级开销。新增行的 `ResetRequiredMoney` 均设为 30000，沿用原版第 20 行数值；实际重置总价及材料返还由游戏逻辑计算，必须在测试存档核对，不能将此字段直接当作整次重置报价。

## 安装

按[玩家说明](../../../docs/玩家安装.txt)或[服主说明](../../../docs/服主安装.txt)安装。双端的文件最终都在 `Pal/Content/Paks/~mods/PalSoulCap80_P.pak`。从旧版升级需移走活动 UE4SS 目录中的 `Mods/PalSchema/mods/PalSoulCap80/`。

## 游戏内验证与卸载

- 分别验证四个属性的 20→21、25→26、79→80；80 后应无法继续升级。每次检查显示费用、实际扣除、属性实际收益。
- 材料不足时应拒绝升级且不扣材料；四项分别升级，确认不会互相消耗等级。
- 保存并重启测试服，重连后确认等级、属性收益与材料数量保留。
- 在独立测试存档验证重置：记录付出的各类魂、显示与实际金币费用、返还各类魂。数据表不等于退款实现，不能跳过这一步。
- 再与整合包其它组件一起测试；单独通过不代表组合通过。

卸载不会自动把存档里的 80 级恢复成 20 级。测试阶段优先恢复安装前的完整存档，并同步移除双端 Mod；若要保留测试后的进度，必须先在 Mod 仍启用时验证并完成所有超 20 级属性的重置，再移除。不要在存在高等级数据时直接删除此表扩展。

## 重制资源

石像原表取自 Steam Windows 专服 Build 25247047。游戏更新后，从目标版本解出同目录下的 `DT_CharacterUpgradeMasterDataTable.uasset` 和 `.uexp`。开发机准备 UAssetGUI（UAssetAPI 1.1 格式）及 repak 0.2.3，运行以下命令。两个工具也可用 `--uassetgui` 和 `--repak` 指定路径。[UAssetGUI 命令](https://github.com/atenfyr/UAssetGUI#command-line-arguments) · [repak](https://github.com/trumank/repak)

```sh
python3 -B scripts/build_soul80.py "/原版资产目录/DT_CharacterUpgradeMasterDataTable.uasset"
python3 -B build_pack.py
```

生成器保留原版行并扩展原版第 20 行。普通整合包构建直接使用已生成的 PAK。五轮整包检查会分别解出两个 ZIP 的 PAK，逐行比对原版导出和新增费用。
