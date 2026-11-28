# 待验证：解锁世界设置里的工作帕鲁上限

本目录**不会被 PalSchema 扫描**（它只读 `blueprints/`），所以不影响打包结果。

## 已经证实的

2026-11-28 本地实测日志：

```
[PalSchema] Loaded changes to BP_PalOptionSubsystem_C
[PalSchema] [warning] Property 'OptionWorldStaticSettings.BaseCampWorkerMaxNum.Max' does not exist in BP_PalOptionSubsystem_C
```

即：类能被 PalSchema 找到，但 `OptionWorldStaticSettings.BaseCampWorkerMaxNum.Max` 不是它上面的属性名。

## 两种待试写法

1. `worker_option_range.C_class.json`：键用 `BP_PalOptionSubsystem_C`（已证伪，保留作记录）
2. `worker_option_range.asset_path.json`：键用资产全路径 `Pal/Content/Pal/Blueprint/System/BP_PalOptionSubsystem`

## 拿到正确属性名的办法

社区 pak（如 `StarkyBase100_P.pak`）只改这一个值。用 repak 解包后读该 uasset 的属性名表，即可确认真实字段名与层级；无需启动游戏。
