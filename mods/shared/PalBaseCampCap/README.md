# 据点工作帕鲁扩容 60（仅满级）

只把**据点等级 35（最后一级）**的工作帕鲁上限从 30 提到 **60**，前面 1–34 级完全保持原版。

## 机制

实际生效数量是两者取小：

```
每据点工作帕鲁 = min(据点等级给的 WorkerMaxNum, 世界设置 BaseCampWorkerMaxNum)
```

- **等级表**：`DT_BaseCampLevelData`（35 行，字段 `Level` / `WorkerMaxNum` / `BaseCampMaxNumInGuild`）。原版 1 级 1 只、逐级 +1、30 级 30 只、31–35 级保持 30。本包**只改第 35 行**为 60，其余行不写，保持原版。
- **世界设置**：`BaseCampWorkerMaxNum` 原版 15、官方上限 50。必须同步改成 60，否则被压回去。

## 服主要改的（不随包）

`PalWorldSettings.ini` 的 `OptionSettings`：

```ini
BaseCampWorkerMaxNum=60
```

改完进游戏还是 15 或 50，说明该值以 `WorldOption.sav` 为准，需要在服务端面板里改。

## 风险与边界

- 只有据点等级到 35 才拿到 60；30–34 级仍是原版 30，满级后从 30 直接跳到 60。
- **官方上限是 50**：官方参数表把 `BaseCampWorkerMaxNum` 写作 max 50。60 属越界值，可能被程序夹回 50；实机不生效就需要客户端 pak 解锁滑块。
- 60 只帕鲁同据点，寻路与工作调度开销明显，Server FPS 会掉。
- 只改工作帕鲁数量，不动公会据点数。
- 双端都要有这份数据，客户端才显示对应工作槽位。
- 未核对：满级槽位显示、60 只同时工作、重启与重连后的保留。
