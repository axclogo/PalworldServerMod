# 据点工作帕鲁扩容 80（仅满级）

只把**据点等级 35（最后一级）**的工作帕鲁上限从 30 提到 **80**，1–34 级完全保持原版。

## 生效链条（三层，缺一层就达不到 80）

```
每据点工作帕鲁 = min(据点等级给的 WorkerMaxNum, 世界设置 BaseCampWorkerMaxNum, 选项上限)
```

| 层 | 原版 | 本包 / 服主要做的 |
| --- | --- | --- |
| 等级表 `DT_BaseCampLevelData` | 1 级 1 只、逐级 +1、30 级 30、31–35 保持 30 | 本包只写第 35 行 = **80**，其余不写 |
| 世界设置 `BaseCampWorkerMaxNum` | 默认 15 | 服主改成 **80** |
| 选项范围（`BP_PalOptionSubsystem`） | **硬上限 50** | 需要第三方 pak 解锁，见下 |

## 必需的第三方前置：解锁 50 硬上限

原版把世界设置的取值范围锁在 50，纯数据改不出来。社区已有多份成品 pak 覆盖 `BP_PalOptionSubsystem`：

| 成品 | 解锁到 | 说明 |
| --- | --- | --- |
| [Starkys 100 base pals](https://www.nexusmods.com/palworld/mods/5857) | 100 | 只把世界设置上限从 50 提到 100，其余不动；双端装 |
| [100/150/200 基地工作帕鲁](https://www.nexusmods.com/palworld/mods/3890) | 100 / 150 / 200 | 只补 `BP_PalOptionSubsystem` 一个值；双端装 |

装法（**双端都要**）：

```
服端：<服根>/Pal/Content/Paks/~mods/<该 pak>.pak
客户：<游戏根>/Pal/Content/Paks/~mods/<该 pak>.pak
```

装完在游戏「世界设置 → 自定义难度 → 基地最大帕鲁工作数」里填 80；面板拒绝 >50 时直接改 ini。

## 服主还要改一行（不随包）

`PalWorldSettings.ini` 的 `OptionSettings`：

```ini
BaseCampWorkerMaxNum=80
```

## 风险与边界

- 只有据点等级到 35 才拿到 80；30–34 级仍是原版 30，满级后从 30 跳到 80。
- 官方参数表把 `BaseCampWorkerMaxNum` 写作 max 50，80 依赖上面的 pak 解锁；pak 不装则最多 50。
- 80 只帕鲁同据点，寻路与工作调度开销明显，Server FPS 会掉；社区作者标注"提高处理负载"。
- 只改工作帕鲁数量，不动公会据点数。
- 数据要双端一致，客户端才显示对应工作槽位。
- 未核对：满级槽位显示、80 只同时工作、重启与重连后的保留。
