# 无限秘药

把玩家单项属性的可用点数上限从原版（每项合计 50 点）提高到 **10000**，生命、耐力、攻击、防御、负重、捕获、工作速度这项，原版把「等级给的属性点 + 秘药/遗物给的额外点（ExStatusPoint）」合并限制在 50，现在上限是 10000。

只改一个字段：`BP_PalGameSetting_C.MaxUseablePoint_SumStatusPointAndExStatusPoint_PerParameter`。它同时是「属性点 + 秘药/遗物（ExStatusPoint）」合计的每项可用上限，所以调高后两者都放开；不新增物品、不改每瓶的增量（增量在 DT_GainStatusPointsItem），也不改经验。

## 为什么是这个字段

SDK 里该字段的字面含义就是「每项参数上，可用的状态点与额外状态点之和的最大值」（`PalGameSetting.h`）：

```cpp
UPROPERTY(BlueprintReadWrite, EditAnywhere)
int32 MaxUseablePoint_SumStatusPointAndExStatusPoint_PerParameter;
```

同一处还有各属性的单点收益字段（`AddMaxHPPerStatusPoint`、`AddPowerPerStatusPoint` 等），本包只动上限，不动收益。

## 风险与边界

- 属性点本身仍受角色等级限制，这个字段放开的是「每项能分配/吃到的上限」，不会凭空发点数或秘药。
- 单机与专服都需要这一份数据：秘药使用与属性结算在服务端，客户端读同值显示。
- 原版 UI 可能把进度显示成 `x/10000`；数值极大时面板排版未核对。
- 与其它改写 `BP_PalGameSetting_C` 同一字段的 Mod 冲突，后加载者生效。
- 未核对：吃满大量秘药后的属性面板、存档体积、重连与重启后的保留。
