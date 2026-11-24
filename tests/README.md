# 离线测试

在项目根目录用 Python 3.9 以上和 Lua 5.4 执行。构建与普通测试只用标准库。

```sh
python3 -B build_pack.py
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
lua tests/test_runtime.lua
```

| 入口 | 能验证的内容 |
| --- | --- |
| [test_pack.py](test_pack.py) | 升魂材料与档位、信赖经验与上限、商店追加和 50 万手术配方、共享字段冲突、与组件源码逐一比对玩家端和服务端安装包，验证分端内容、自动启用标记、客户端专属组件分端及安装说明 |
| [test_custom_traits.py](test_custom_traits.py) | 四个词条的 ID、颜色、目标、触发范围、数值、显示文本与商店到手术台的引用 |
| [test_runtime.lua](test_runtime.lua) | 用模拟 UE4SS 接口检查钓鱼输入、基地合并、地图自动去雾、滑翔搭档和普通装备的选择 |
| [check_game_export.py](check_game_export.py) | 可选。对照原版数据查真实行名、ID 与排序冲突、限购模板、图标、手术引用和究极魂材料。游戏更新后可用新构建的导出重跑 |

构建产物为 `安装包/幻兽帕鲁-玩家端.zip` 和 `安装包/幻兽帕鲁-服务端.zip`。包内入口是根目录的 `安装说明.txt`。两端的 `Mods/PalSchema/enabled.txt` 及各自 Lua 目录下的 `enabled.txt` 供已有的 UE4SS 在冷启动时读取。玩家包默认启用 `PalMapReveal` 与 `PalGliderVisual`。

### 两端整包五轮验收

构建一次，再向以下命令传入含下述九张原版表的目录。脚本每轮重新解压待交付的两个 ZIP，分别核对两端数据、运行包内 Lua，另检查包的重建、安装清单和共享文件。两端源码、说明、测试或安装包变化后，需要从第一轮重新开始。每轮从两份安装包内的 PAK 解出实际石像表，逐行核对 80 级。开发机需提供 Lua 5.4、repak 和支持 VER_UE5_1 的 UAssetGUI，可分别用 `--lua`、`--repak`、`--uassetgui` 指定程序位置。

```sh
python3 -B tests/check_release.py "/同一构建的九张原版表"
```

### 与原版表比对

传入一个目录，里面平放**同一个游戏构建**的七个原始 FModel 导出，每个文件保留含 DataTable `Rows` 的原始 JSON 结构。公开样本可参阅[游戏导出仓库](https://github.com/Dhampyru/Palworld-Extracted)。

```text
DT_ItemDataTable_Common.json
DT_ItemIconDataTable_Common.json
DT_ItemShopCreateData_Common.json
DT_OperatingTablePassiveSkillDataTable.json
DT_PassiveSkill_Main_Common.json
DT_SkillNameText_Common.json
DT_SkillDescText_Common.json
```

```sh
python3 -B tests/check_game_export.py "/实际的导出目录"
```

失败会指出缺失或冲突的条目，并以非零状态退出。公开样本只代表其导出构建；服内其它 Mod 也可能占用其中的空闲 ID。原始游戏资产无需放入项目或发给玩家。

还可从同一游戏构建导出 `DT_CharacterUpgradeMasterDataTable.json` 和 `DT_FriendshipRankTable.json`，在命令末尾加 `--growth-dir "/两张成长表所在目录"`。该项会按表行名和等级分别检查冲突，再核对升魂 20→21 及信赖 10→11 的衔接、完整区间和 99 级经验上限。[石像原表](https://github.com/Dhampyru/Palworld-Extracted/blob/d38105b4dc0cf6f36c5035997fbe54205bb2d753/Pal/Content/Pal/DataTable/Character/DT_CharacterUpgradeMasterDataTable.json) · [信赖原表](https://github.com/Dhampyru/Palworld-Extracted/blob/d38105b4dc0cf6f36c5035997fbe54205bb2d753/Pal/Content/Pal/DataTable/Friendship/DT_FriendshipRankTable.json)

服务端包中的 `检查植入物.py` 支持停服时将活动目录的 PalSchema 共享文件与独立解压的包逐字节对照，检查重复追加和替换竞技场库存的 raw 文件；也可单独读取临时服日志核对登记。打包测试另覆盖单次启动完整、漏项、重复记录、同名修改、删除和前置清理接口错误。

Lua 测试替身无法加载 Unreal、进行真实联机或保存世界。服务端是否接受升级、是否正确扣款与发奖、高信赖属性收益、卸载和存档恢复，都留在[游戏内验收](../docs/GAME_CHECKS.md)中。
