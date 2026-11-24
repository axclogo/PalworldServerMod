# 信赖 99

扩展信赖上限至 99，并沿用每种帕鲁自身的信赖属性系数，让生命、攻击、防御随信赖等级继续增长。游戏中的属性计算、读档加载顺序、联机表现尚未验证。

## 规则与实现

- 保留原版负等级及 0–10 级，不改已有经验门槛。
- `DT_FriendshipRankTable` 新增 11–99 级共 89 行。10 级累计 200000 点，之后每级增加 50000 点，99 级累计 4650000 点。
- 同时设置 `BP_PalGameSetting_C.FriendshipPoint_Max = 4650000`，使经验点上限与等级表一致。该字段已在 SDK 的 `PalGameSetting.h` 核对为 int32。
- 不修改抚摸、陪伴、工作或桃子的经验收益，不自动发放信赖。
- 保留物种的 `Friendship_HP`、`Friendship_ShotAttack`、`Friendship_Defense`。不另乘 10，不直接改最终属性。99 级不代表最终战斗属性是原版的 9.9 倍。
- 不额外添加工作速度收益；SDK 虽有 `Friendship_CraftSpeed` 字段，实际物种可能为零。

## 安装与验证

专服使用 `安装包/幻兽帕鲁-服务端.zip`，玩家使用 `安装包/幻兽帕鲁-玩家端.zip`。按各自 ZIP 根目录的 `安装说明.txt` 配好 UE4SS 和 PalSchema，合并 `Mods/`。两端的 `Mods/PalSchema/mods/PalTrust99/` 均应包含 `raw/trust_rank_99.json` 和 `blueprints/trust_limit.json`。其中一份提供经验表，另一份提供上限；两份同时生效才能验证 99 级。

先在完整备份的独立测试存档验证：

1. 10→11 级门槛为累计 250000 点，生命、攻击、防御实际增长。
2. 经验超过原版上限仍能增长；98→99 正常，不出现 100 级。
3. 分别在 11、26、99 级保存并完整重启专服，客户端重连后检查等级、经验与实际属性一致。
4. 使用基础属性不同的帕鲁验证各自系数，再与升魂 80 一起检查生命、面板属性和战斗伤害。

社区作者记录过两种故障。缺少经验上限组件时，其最小费用变体在 26 级封顶。加入 100 级行后，其测试中经验增长冻结。本包将 99 级设为最后一行，经验上限和 99 级门槛共用数值 4650000，两份 JSON 同时打包。26 级来自作者的特定曲线，只作为本包的重启检查点。作者还在两种帕鲁身上观察到不同的 99 级攻击增幅，因此本包验收选择不同物种，并固定个体值、被动和升魂等级后比较。[作者的文件说明](https://www.nexusmods.com/palworld/mods/2575?tab=files) · [作者的 100 级测试](https://www.nexusmods.com/palworld/mods/2575)

PalSchema 的蓝图加载器在 `PostEngineInit` 登记短类名，在蓝图类加载后的回调中写入默认对象。日志里的 `Loaded changes to BP_PalGameSetting_C` 只表示已登记。用户构建上是否赶在读档前生效，仍需上方第 3 项验证。卸载后请恢复安装前的完整存档，高经验进度可能在原版读档时被截断。[蓝图加载器时序](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalBlueprintModLoader.cpp)

## 来源与维护

- [真实表名、行名及原版门槛](https://github.com/Dhampyru/Palworld-Extracted/blob/d38105b4dc0cf6f36c5035997fbe54205bb2d753/Pal/Content/Pal/DataTable/Friendship/DT_FriendshipRankTable.json)，该资产导出仓库标注 2026-07-22。
- [SDK 等级结构](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/PalFriendshipRankDataRow.h)。
- [SDK 经验上限字段](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/PalGameSetting.h)：直接源码中的 `FriendshipPoint_Max`。
- [SDK 信赖属性字段](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/PalCharacterParameterDatabaseRow.h)。
- [PalSchema 蓝图配置格式](https://github.com/Okaetsu/PalSchema/blob/main/assets/examples/HalfSprintStamina/blueprints/sp_setting.jsonc)。
- [社区 99 级先例及旧版问题记录](https://www.nexusmods.com/palworld/mods/2575)：仅参考机制，未复制其限制分发的成品。

在项目根目录运行 `python3 -B -m scripts.build_trust99` 可重新生成两份信赖 JSON。运行 `python3 -B build_pack.py` 可重新生成玩家端及服务端安装包。
