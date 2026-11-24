"""从服务端包核对开服前的共享文件、竞技场配方或临时服冷启动日志。"""

import argparse
import json
from pathlib import Path
import re
import sys


SHARED = {
    "PalTrust99": ("raw/trust_rank_99.json", "blueprints/trust_limit.json"),
    "PalArenaImplants": ("items/implants.json", "raw/arena_shop.json", "raw/surgery.json", "raw/implant_icons.json",
                         "raw/custom_passives.json", "translations/global/custom_passives.json"),
    "PalGroundStacks": ("blueprints/merge_range.json",),
    "PalFishingWin": ("blueprints/catch_battle.json",),
}


CORE_TABLE = re.compile(
    r"\b(DT_(?:PassiveSkill_Main(?:_Common)?|OperatingTablePassiveSkillDataTable|"
    r"ItemIconDataTable(?:_Common)?|ItemShopCreateData(?:_Common)?|CharacterUpgradeMasterDataTable|FriendshipRankTable))"
    r": \d+ rows updated, \d+ rows added, \d+ rows deleted, ([0-9]+) errors?\."
)


def check_shared_files(mods, reference):
    if mods.resolve() == reference.resolve():
        raise ValueError("请从单独解压的服务端包运行，并将 --mods-dir 指向游戏实际使用的目录。")
    differences = []
    for mod, files in SHARED.items():
        for filename in files:
            relative = Path(mod) / filename
            source = reference / relative
            installed = mods / relative
            if not source.is_file():
                raise ValueError(f"服务端包缺少 {relative}，请重新完整解压。")
            if not installed.is_file():
                differences.append(f"缺少 {relative}")
            elif installed.read_bytes() != source.read_bytes():
                differences.append(f"内容不同 {relative}")
    if differences:
        raise ValueError("活动目录与这份安装包不一致：\n" + "\n".join(differences))


def check(lines, items):
    expected = {key.casefold(): key for key in items}
    if len(expected) != 14:
        raise ValueError("本包需要 14 个植入物定义，请重新完整解压服务端 ZIP。")
    added = set()
    issues = set()
    starts = 0
    for line in lines:
        if re.search(r"PalSchema v[\w.\-]+ by Okaetsu loaded\.", line):
            starts += 1
        if "unable to clean up invalid items" in line:
            issues.add("PalSchema 报告物品读档清理接口未就绪。")
        if not starts:
            continue
        table = CORE_TABLE.search(line)
        if table and int(table[2]):
            issues.add(f"{table[1]} 加载时报告 {table[2]} 个错误，请查看该表前面的具体报错。")
        event = re.search(r"(Added Item|Modified Item|Deleted Item|Property '[^']+' not found in Item|Item) '([^']+)'(.*)$", line)
        if not event:
            continue
        action, key, detail = event.groups()
        key = key.casefold()
        if key not in expected:
            continue
        if action == "Added Item":
            added.add(key)
        elif action != "Item" or "is invalid." in detail:
            issues.add(f"{expected[key]} 出现需核对的记录：{event.group().strip()}")
    if starts != 1:
        raise ValueError(f"找到 {starts} 次 PalSchema 启动记录，请使用临时服本次冷启动的 UE4SS.log。")
    if expected.keys() - added:
        issues.add("缺少新增记录：" + "、".join(expected[k] for k in sorted(expected.keys() - added)))
    if issues:
        raise ValueError("\n".join(sorted(issues)))


SURGERY = "DT_OperatingTablePassiveSkillDataTable"


def check_shop_rows(data, item_ids):
    for table in ("DT_ItemShopCreateData", "DT_ItemShopCreateData_Common"):
        for key, row in data.get(table, {}).items():
            if key.casefold() != "arena_shop_1" and "*" not in key:
                continue
            if row is None:
                yield f"{table} / {key} 删除商店"
                continue
            stock = next((v for k, v in row.items() if k.casefold() == "productdataarray"), None)
            if isinstance(stock, list) or isinstance(stock, dict) and stock.get("Action") == "Clear":
                yield f"{table} / {key} 清空或替换库存"
            elif isinstance(stock, dict):
                for product in stock.get("Items", []):
                    for field, value in product.items():
                        if field.casefold() == "staticitemid" and str(value).casefold() in item_ids:
                            yield f"{table} / {key} 再次上架 {value}"


def check_arena_files(mods, shipped):
    own_file = mods / "PalArenaImplants/raw/surgery.json"
    expected = {k.casefold(): v for k, v in shipped[SURGERY].items()}
    item_ids = {row["RequireItemId"].casefold() for row in expected.values()}
    shop_file = own_file.with_name("arena_shop.json")
    overlaps = []
    for path in sorted(mods.glob("*/raw/*")):
        if path.suffix not in (".json", ".jsonc") or not path.is_file():
            continue
        source = path.read_text(encoding="utf-8-sig")
        if path.suffix == ".jsonc":
            # Keep quoted strings intact while removing the comments PalSchema permits in JSONC.
            source = re.sub(r'"(?:\\.|[^"\\])*"|//[^\r\n]*|/\*[\s\S]*?\*/',
                            lambda match: match[0] if match[0].startswith('"') else " ", source)
        try:
            data = json.loads(source)
        except ValueError as error:
            raise ValueError(f"无法核对 {path}：{error}") from error
        if not isinstance(data, dict):
            raise ValueError(f"raw 数据应为 JSON 对象：{path}")
        if path != shop_file:
            try:
                overlaps.extend(f"{path.relative_to(mods)} / {issue}" for issue in check_shop_rows(data, item_ids))
            except (AttributeError, TypeError) as error:
                raise ValueError(f"无法解析竞技场库存：{path}") from error
        if path == own_file:
            continue
        rows = data.get(SURGERY, {})
        if not isinstance(rows, dict):
            raise ValueError(f"手术表格式异常：{path}")
        for key, patch in rows.items():
            row = patch if isinstance(patch, dict) else {}
            fields = {name.casefold(): value for name, value in row.items()}
            skill = str(fields.get("passiveskill", "")).casefold()
            item = str(fields.get("requireitemid", "")).casefold()
            current = expected.get(key.casefold())
            if current and isinstance(patch, dict) and all(current.get(k) == v for k, v in row.items()):
                continue
            if current or skill in expected or item in item_ids or "*" in key:
                overlaps.append(f"{path.relative_to(mods)} / {key}")
    if overlaps:
        raise ValueError("以下竞技场库存或手术配方可能冲突，请核对后再使用旧档：\n" + "\n".join(overlaps))


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("log", type=Path, nargs="?", help="临时服本次启动的 UE4SS.log")
    cli.add_argument("--mods-dir", type=Path, help="游戏实际使用的 Mods/PalSchema/mods，可在开服前检查")
    args = cli.parse_args()
    if not args.log and not args.mods_dir:
        cli.error("请输入 --mods-dir 指向活动目录，或提供临时服日志。")
    reference = Path(__file__).resolve().parent / "Mods/PalSchema/mods"
    arena = reference / "PalArenaImplants"
    try:
        if args.mods_dir:
            check_shared_files(args.mods_dir, reference)
            recipes = json.loads((arena / "raw/surgery.json").read_text(encoding="utf-8"))
            check_arena_files(args.mods_dir, recipes)
            print("活动目录的共享文件与安装包一致，未发现所检查的竞技场库存或手术配方冲突。")
        if args.log:
            items = json.loads((arena / "items/implants.json").read_text(encoding="utf-8"))
            with args.log.open(encoding="utf-8-sig", errors="replace") as lines:
                check(lines, items)
            print("14 个植入物均有新增记录。请用旧世界副本核对购买、手术和重启后的保留情况。")
    except (OSError, ValueError) as error:
        sys.exit(f"检查未通过。{error}")
