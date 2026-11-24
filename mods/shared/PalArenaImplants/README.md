# 竞技场植入物与四个自定义虹色词条

此组件随玩家端和服务端分别分发，双端安装位置均为 `Mods/PalSchema/mods/PalArenaImplants/`。两端按各自 ZIP 根目录的 `安装说明.txt` 合并 `Mods/`。使用原生手术台配方与重要物品类型，新增十四种持有后可反复用于手术的植入物：传说、圣天、炎帝、海皇、雷帝、精灵王、冰帝、岩帝、冥王、神龙，以及白猪战车、宅断腿、凯旋山野、纸老虎。

## 自定义词条

| 名称 | 原生效果与数值 | 生效条件 |
| --- | --- | --- |
| 白猪战车 | `MaxHP` ＋100%；`Defense` ＋150% | 自身常驻 |
| 宅断腿 | `Sanity_Decrease` －30%；`FullStomatch_Decrease` －30%；`MoveSpeed` －20%；`CraftSpeed` －15% | `InvokeWorker`，仅担任基地工作帕鲁时 |
| 凯旋山野 | `ElementBoost_Leaf` ＋20%；`ShotAttack` ＋15% | 自身常驻 |
| 纸老虎 | `ShotAttack` ＋40%；`Defense` －20% | 自身常驻 |

四个词条均 `Rank = 4`，效果目标为 `ToSelf`，不传给玩家或其它帕鲁。没有世界树专属标记或世界树资源效果；不新增野生抽取来源，`LotteryWeight = 0`。不改变原版词条和生存计算公式，不使用额外运行脚本。具体数值、实际收益和遗传行为仍须实测。

竞技场商人出售的传说及四个自定义植入物每件 250 张战斗券，九系帝王每件 150 张战斗券，每种限购一件。持有对应植入物时可选择该项手术，每次另付 50 万金币。可重复使用和重启后的限购状态仍待联机验证。[竞技场战斗券与手术台官方说明](https://steamcommunity.com/games/1623730/announcements/detail/518590951147438123)

## 文件与安装

- `raw/custom_passives.json`：只新增四个带 `PalPack_` 前缀的独立词条 ID。
- `translations/global/custom_passives.json`：名称与描述的中文文本，适用于全部客户端语言。
- `items/implants.json`：带 `PalPack_Implant_` 前缀的独立物品。
- `raw/implant_icons.json` 为每个植入物编号登记原版永久植入物的芯片贴图。
- `raw/surgery.json`：十四个词条与植入物的手术台关联。
- `raw/arena_shop.json`：向 `Arena_Shop_1` 追加十四项商品。

整个目录同时更新到服务器和客户端，不能只安装词条表或植入物。PalSchema 的数组对象 `{"Items": [...]}` 是追加语义，直接数组会替换原库存，本包不使用替换。保持自动重载关闭；开发时热重载追加数组可能产生重复商品，修改后完整重启。

## 原版数据与已知问题

商店、被动词条、名称和描述在游戏中各有一个无后缀的复合表，导出文件中的 `_Common` 是它们的父表。PalSchema 0.6.71 的 raw 加载器用复合表名称匹配配置，再把修改应用到对应父表。翻译加载器则按表名查找并加行，找不到表时会直接跳过。因此补丁保留无后缀表名，并在游戏内分别核对库存与中文显示。[原版商店复合表](https://github.com/Dhampyru/Palworld-Extracted/blob/main/Pal/Content/Pal/DataTable/ItemShop/DT_ItemShopCreateData.json) · [raw 复合表处理](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalRawTableLoader.cpp#L46-L61) · [翻译表查找](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalLanguageModLoader.cpp#L95-L135)

Steam Windows 专服 Build 25247047 的竞技场原有 56 件商品，其中七件为永久植入物。永久植入物采用 `OnlyPurchaseOne`、`ProductNum = 1`、`Stock = 0`。本包沿用该组合，向库存追加 14 件。原版植入物的排序号截至 6265，本包接续使用 6266–6279。排序号决定展示次序，存档和配方使用独立的物品 ID。游戏更新后需用对应构建重新比对原表。[竞技场商品](https://github.com/Dhampyru/Palworld-Extracted/blob/main/Pal/Content/Pal/DataTable/ItemShop/DT_ItemShopCreateData_Common.json) · [物品表](https://github.com/Dhampyru/Palworld-Extracted/blob/main/Pal/Content/Pal/DataTable/Item/DT_ItemDataTable_Common.json)

原版专服的库存条目把物品编号记作 `StaticItemID`，1.0.5 客户端反射表使用 `StaticItemId`。PalSchema 遍历数组元素的反射字段，按原样查 JSON 键。生成器为同一个编号输出这两种拼写，任一端都只创建一件商品。原版商店的价格控件默认显示 9999999。[加载器源码](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/SDK/Helper/PropertyHelper.cpp#L352-L374)

实际解包对照了 Zarqueam 的 Worthwhile Arena Shop：三条永久植入物商品都使用已有物品编号，每份 1 件、限购一次。原样复制其清空库存操作会替换原版商品，本包只追加。对于新物品，PalSchema 在填写物品数据、登记翻译后才把物品加入游戏的物品列表。本包让物品加载器只登记物品，中文名称和说明交给独立翻译表；每个物品显式引用自己的名称、说明、基础编号和永久芯片图标。参考项目也公开了专服通过物品管理器读到 87 件自定义植入物的结果，该实验只验证了它自己的物品注册。[社区商店作者](https://www.nexusmods.com/palworld/mods/3328) · [社区植入物定义](https://github.com/lincybreeze/Palworld-Better-Surgery-Table/blob/main/projects/pal-implant-expansion/workshop/PalSchema/items/implant-items.json) · [作者的专服注册结果](https://github.com/lincybreeze/Palworld-Better-Surgery-Table/blob/main/runtime-audit/dedicated-item-registry-probe-0.2.3.json) · [PalSchema 登记顺序](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalItemModLoader.cpp#L197-L215)

七月导出中有一条完整的购买和手术链路可供对照。竞技场以 50 张战斗券出售 `PalPassiveSkillChange_CoolTimeReduction_Up_1`，手术行通过 `RequireItemId` 引用它并收 50,000 金币。新植入物使用相同的永久物品分类，并给每个物品单独配一行。游戏公开接口按物品 ID 或被动 ID 查询手术，费用字段为 32 位整数，可以表示 500,000。另装“解锁全部手术”的 Mod 时，即使四个新词条的 ID 都独立，传说和帝王的手术行仍可能被另一个 Mod 改价或取消物品要求。[手术数据结构](https://github.com/localcc/PalworldModdingKit/blob/e6632458b97af0083eb81715775651b08104ef6a/Source/Pal/Public/PalOperatingTablePassiveSkillData.h) · [两种查询接口](https://github.com/localcc/PalworldModdingKit/blob/e6632458b97af0083eb81715775651b08104ef6a/Source/Pal/Public/PalMasterDataTableAccess_OperatingTablePassiveSkillData.h) · [社区手术解锁组件](https://steamcommunity.com/sharedfiles/filedetails/?id=3761679027)

原版 `Legend` 使用 `ShotAttack` 表示攻击；`WorldTree_ATK_DEF` 的描述将 `MaxHP` 标为最大生命百分比；`PAL_Sanity_Down_3` 和 `PAL_FullStomach_Down_3` 的负值分别表示消耗减慢。凯旋山野沿用原版草属性加伤的组合，`ElementBoost_Leaf` 选择技能属性，`TargetElementType = None` 保留其它属性帕鲁使用草技能的资格。社区 Passives Expanded 曾修复元素词条只对同属性帕鲁生效的问题。[原版被动表](https://github.com/Dhampyru/Palworld-Extracted/blob/main/Pal/Content/Pal/DataTable/PassiveSkill/DT_PassiveSkill_Main_Common.json) · [Passives Expanded 作者说明](https://www.nexusmods.com/palworld/mods/5266?tab=description)

PalSchema 读取存档物品时会清理无法识别的静态物品 ID。更新整合包时请先在独立测试存档核对物品加载，再打开已拥有植入物的存档。若日志出现 `is invalid. Deleting.` 或报告无法清理无效物品，退出并保留更新前的存档副本。[上游物品加载器及读档处理](https://github.com/Okaetsu/PalSchema/blob/302b4ffe958d219762058cade48685ef010723d8/src/Loader/PalItemModLoader.cpp#L457-L574)

## 游戏内验收

1. 原商品仍在；四个新词条显示正确中文、虹色和完整描述，不显示世界树专属效果。
2. 用尚未购买植入物的测试角色确认手术未解锁，再购买一件。用可支付的金币总额 499,999 测一次，应保留余额、原词条和植入物；补至 500,000 再做手术，应正好扣到零，目标帕鲁出现新词条。再次准备足额金币，在第二只帕鲁上重复手术，核对永久物品和限购记录。余下十三项分别核对关联，重连及重启后再确认。社区有“客户端能看到配方、专服不执行手术”的实际反馈，因此以扣款、服务端保存的词条及重新登录后均一致作为通过条件。[社区专服反馈](https://www.nexusmods.com/palworld/mods/3720?tab=posts)
3. 白猪战车：同一帕鲁同一等级前后核对最大生命和防御，不能把已有加成下的总面板直接乘 2 / 2.5。
4. 宅断腿：同样工作与食物条件下比较 SAN / 饱食消耗；移动和工作确实变慢；从基地移至队伍后四项效果停止，再放回基地重新生效。
5. 凯旋山野：选一只学会草系技能的非草系帕鲁，对同一目标各使用草系和非草系技能，对照植入前后的攻击面板和伤害。两种技能均有攻击加成，草系技能还应额外获得 20% 属伤。暴击、属性克制和帕鲁本系加成保持一致。
6. 纸老虎：攻击提高、防御降低；与鬼神、双刃圣剑分别比较，再检查叠加。
7. 取出 / 收回、重连、手术替换 / 移除、完整重启，以及与升魂 80 / 信赖 99 组合验证。繁育继承须单独实测，当前没有改写繁育逻辑。

未安装本组件的客户端不能参加测试。其它修改这些手术配方、同 ID 或替换竞技场库存的 Mod 需先停用。新增词条和物品会进入存档；卸载测试时恢复安装前完整存档，不能仅凭 JSON 正确认定存档安全。

实现参考：[原生被动结构](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/PalPassiveSkillDatabaseRow.h)、[原生效果枚举](https://github.com/localcc/PalworldModdingKit/blob/main/Source/Pal/Public/EPalPassiveSkillEffectType.h)、[PalSchema 翻译加载器](https://github.com/Okaetsu/PalSchema/blob/main/src/Loader/PalLanguageModLoader.cpp)、[物品加载器](https://github.com/Okaetsu/PalSchema/blob/main/src/Loader/PalItemModLoader.cpp)、[数组加载语义](https://github.com/Okaetsu/PalSchema/blob/main/src/SDK/Helper/PropertyHelper.cpp)。四个词条根据用户定稿独立实现，没有复制社区词条 Mod 的文件。
