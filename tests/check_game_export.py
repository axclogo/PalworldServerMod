"""以 FModel 原版导出核对竞技场、物品及可选的成长扩展。"""

import argparse
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


SHARED = Path(__file__).resolve().parents[1] / "mods/shared"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(directory, name):
    objects = read(directory / (name + ".json"))
    matches = [obj["Rows"] for obj in objects if obj.get("Name") == name and "Rows" in obj]
    if len(matches) != 1 or not matches[0]:
        raise ValueError(f"{name}.json 需要含一个同名且非空的 Rows 表")
    return matches[0]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def folded(values):
    return {value.casefold() for value in values}


def check_additions(label, original, added):
    """允许原版内部共用排序值；新增项必须唯一且未被原版占用。"""
    occupied = set(original)
    for key in added:
        require(key not in occupied, f"{label} 冲突：{key}")
        occupied.add(key)


def check_passive_fields(passives, game_passives):
    # raw 加载器会警告并跳过未知字段，即使这一行的其它字段已成功写入。
    native_fields = {field for row in game_passives.values() for field in row}
    native_effect_targets = {
        (row[f"EffectType{slot}"], row[f"TargetType{slot}"])
        for row in game_passives.values() for slot in range(1, 5)
    }
    for trait, row in passives.items():
        unknown = set(row) - native_fields
        require(not unknown, f"{trait} 包含原版被动结构中未见的字段：{sorted(unknown)}")
        for slot in range(1, 5):
            pair = row[f"EffectType{slot}"], row[f"TargetType{slot}"]
            require(pair in native_effect_targets, f"{trait} 第 {slot} 个效果和目标组合在原版中未见：{pair}")


def check(directory, shared=SHARED):
    arena = shared / "PalArenaImplants"
    items = read(arena / "items/implants.json")
    passives = read(arena / "raw/custom_passives.json")["DT_PassiveSkill_Main"]
    surgery_table = "DT_OperatingTablePassiveSkillDataTable"
    recipes = read(arena / "raw/surgery.json")[surgery_table]
    game_items = rows(directory, "DT_ItemDataTable_Common")
    game_passives = rows(directory, "DT_PassiveSkill_Main_Common")
    game_recipes = rows(directory, surgery_table)
    for label, native, added in (("物品 ID", game_items, items), ("词条 ID", game_passives, passives),
                                 ("手术行 ID", game_recipes, recipes)):
        check_additions(label, folded(native), (k.casefold() for k in added))
    check_additions("物品 SortId", (r["SortId"] for r in game_items.values()), (r["SortId"] for r in items.values()))
    check_additions("手术 PassiveSkill", folded(r["PassiveSkill"] for r in game_recipes.values()),
                    (r["PassiveSkill"].casefold() for r in recipes.values()))
    check_additions("手术 RequireItemId", folded(r["RequireItemId"] for r in game_recipes.values()),
                    (r["RequireItemId"].casefold() for r in recipes.values()))
    check_passive_fields(passives, game_passives)

    texts = read(arena / "translations/global/custom_passives.json")
    for table, field in (("DT_SkillNameText", "OverrideNameTextID"), ("DT_SkillDescText", "OverrideDescMsgID")):
        local = texts[table]
        check_additions(table, folded(rows(directory, table + "_Common")), (key.casefold() for key in local))
        refs = folded(row[field] for row in passives.values())
        require(len(local) == len(passives) and refs == folded(local) and all(local.values()), f"{table} 翻译引用不完整")

    elements = ("Normal", "Fire", "Aqua", "Thunder", "Leaf", "Ice", "Earth", "Dark", "Dragon")
    native_traits = folded(["Legend"] + [f"ElementBoost_{e}_2_PAL" for e in elements])
    missing = native_traits - folded(game_passives)
    require(not missing, f"原版缺少指定词条：{sorted(missing)}")
    require(len(passives) == 4 and folded(recipes) == native_traits | folded(passives), "14 条手术的词条引用不符")
    for trait, recipe in recipes.items():
        require(recipe["RequireItemId"].casefold() == ("PalPack_Implant_" + trait).casefold(),
                f"{trait} 手术关联了其他植入物")
        require(recipe["PassiveSkill"].casefold() == trait.casefold() and recipe["Price"] == 500_000,
                f"{trait} 手术目标或金币价格错误")
    item_ids = folded(items)
    require(len(items) == len(recipes) and folded(r["RequireItemId"] for r in recipes.values()) == item_ids,
            "手术所需植入物与物品表不一一对应")
    require("palupgradestone4" in folded(game_items), "原版物品表缺少究极帕鲁之魂")

    icons = rows(directory, "DT_ItemIconDataTable_Common")
    template_icon = icons["PalPassiveSkillChange"]["Icon"]["AssetPathName"]
    icon_rows = read(arena / "raw/implant_icons.json")["DT_ItemIconDataTable"]
    check_additions("植入物图标行", folded(icons), (key.casefold() for key in icon_rows))
    require(set(icon_rows) == set(items), "每件植入物都需要独立的图标引用")
    for item_id, item in items.items():
        require(item["ItemBaseName"] == item_id, f"{item_id} 缺少对应的基础物品编号")
        require(item["IconTexture"] == icon_rows[item_id]["Icon"] == template_icon,
                f"{item_id} 图标与游戏永久植入物不符")
        name_key, desc_key = item["OverrideNameMsgID"], item["OverrideDescMsgID"]
        require(name_key == "ITEM_NAME_" + item_id and texts["DT_ItemNameText"].get(name_key),
                f"{item_id} 无法查到物品名称")
        require(desc_key == "ITEM_DESC_" + item_id and texts["DT_ItemDescriptionText"].get(desc_key),
                f"{item_id} 无法查到物品说明")

    shop_id = "Arena_Shop_1"
    original = rows(directory, "DT_ItemShopCreateData_Common")[shop_id]["productDataArray"]
    only_one = "EPalItemShopProductType::OnlyPurchaseOne"
    permanent = folded(k for k, item in game_items.items()
                       if item["TypeA"] == "EPalItemTypeA::Essential"
                       and item["TypeB"] == "EPalItemTypeB::Essential_PassiveSkillChange")
    paid_unlocks = folded(r["RequireItemId"] for r in game_recipes.values() if r["Price"] > 0)
    paid_permanent_ids = permanent & paid_unlocks
    id_key = next(key for key in original[0] if key.casefold() == "staticitemid")
    template = next((p for p in original if p[id_key].casefold() in paid_permanent_ids
                     and p["ProductType"] == only_one and p["Stock"] == 0 and p["ProductNum"] == 1), None)
    require(template is not None, "原竞技场缺少可解锁付费手术的限购永久植入物模板")
    patch = read(arena / "raw/arena_shop.json")
    require(set(patch) == {"DT_ItemShopCreateData"} and set(patch["DT_ItemShopCreateData"]) == {shop_id},
            "商店补丁修改了额外的表或行")
    shop = patch["DT_ItemShopCreateData"][shop_id]
    require(set(shop) == {"productDataArray"} and isinstance(shop["productDataArray"], dict)
            and set(shop["productDataArray"]) == {"Items"}, "原库存只能通过 productDataArray.Items 追加")
    products = shop["productDataArray"]["Items"]
    require(isinstance(products, list), "追加商品必须是数组")
    check_additions("竞技场商品", folded(p[id_key] for p in original),
                    (p["StaticItemId"].casefold() for p in products))
    require(folded(p["StaticItemId"] for p in products) == item_ids, "追加商品与新增植入物不一一对应")
    rarity = {key.casefold(): row["Rarity"] for key, row in items.items()}
    for p in products:
        require(p.get("StaticItemID") == p["StaticItemId"],
                f"{p['StaticItemId']} 的客户端与专服商品编号不一致")
        unknown = set(p) - set(template) - {"StaticItemId", "StaticItemID"}
        require(not unknown, f"{p['StaticItemId']} 的库存字段在原版模板中未见：{sorted(unknown)}")
        price = 250 if rarity[p["StaticItemId"].casefold()] == 4 else 150
        require((p["ProductType"], p["ProductNum"], p["Stock"], p["OverridePrice"]) == (only_one, 1, 0, price),
                f"{p['StaticItemId']} 限购属性或竞技场价格错误")
    print(f"七表核对通过。10 个原版词条、{len(passives)} 个新增词条、{len(recipes)} 项手术。"
          f"竞技场原有 {len(original)} 件，追加 {len(products)} 件。")


def check_soul_pak(pak, vanilla, repak, uassetgui):
    name = "DT_CharacterUpgradeMasterDataTable"
    asset = Path("Pal/Content/Pal/DataTable/Character") / (name + ".uasset")
    with TemporaryDirectory() as tmp:
        output = Path(tmp) / "files"
        subprocess.run([repak, "unpack", "-q", "-o", output, pak], check=True)
        require({p.relative_to(output) for p in output.rglob("*") if p.is_file()}
                == {asset, asset.with_suffix(".uexp")}, "PAK 内需要且只允许原版挂载路径的石像表")
        document = Path(tmp) / "actual.json"
        subprocess.run([uassetgui, "tojson", output / asset, document, "VER_UE5_1"], check=True)
        cooked = read(document)
    table, = cooked["Exports"]
    require(cooked["FolderName"] == "/Game/Pal/DataTable/Character/" + name
            and table["ObjectName"] == name and not table["bNotForClient"] and not table["bNotForServer"],
            "石像表包名、导出对象或双端加载标记异常")
    data = table["Table"]["Data"]
    require(len(data) == 80 and {row["Name"] for row in data} == {str(i) for i in range(1, 81)},
            "石像表须含 80 个唯一等级")
    for row in data:
        rank = int(row["Name"])
        fields = {p["Name"]: p["Value"] for p in row["Value"]}
        expected = vanilla[row["Name"]] if rank <= 20 else {
            "Rank": rank, "RequiredStaticItemId": "PalUpgradeStone4",
            "RequiredItemNum": 10 + 2 * ((rank - 21) // 5), "ResetRequiredMoney": 30000,
        }
        require(row["StructType"] == "PalCharacterUpgradeMasterData" and fields == expected,
                f"石像表第 {rank} 行与原版或新增费用不一致")


def check_growth(directory, shared=SHARED, *, soul_pak=None, repak="repak", uassetgui="UAssetGUI"):
    soul_table = "DT_CharacterUpgradeMasterDataTable"
    trust_table = "DT_FriendshipRankTable"
    native_souls = rows(directory, soul_table)
    require(set(native_souls) == {str(i) for i in range(1, 21)}, "目标版本原版升魂等级已变化")
    check_soul_pak(soul_pak or SHARED / "PalSoulCap80/PalSoulCap80_P.pak", native_souls, repak, uassetgui)
    native_trust = rows(directory, trust_table)
    extra_trust = read(shared / "PalTrust99/raw/trust_rank_99.json")[trust_table]
    check_additions(trust_table + " 行名", folded(native_trust), (key.casefold() for key in extra_trust))
    check_additions(trust_table + " 等级", (r["FriendshipRank"] for r in native_trust.values()),
                    (r["FriendshipRank"] for r in extra_trust.values()))
    fields = set(next(iter(native_trust.values())))
    for key, row in extra_trust.items():
        require(set(row) == fields, f"{trust_table}/{key} 与原版行字段不符")

    thresholds = {r["FriendshipRank"]: r["RequiredPoint"] for r in (native_trust | extra_trust).values()}
    ranks = sorted(thresholds)
    require(ranks == list(range(ranks[0], 100)), "信赖等级与原版合并后存在缺级或超过 99")
    require(all(thresholds[a] < thresholds[b] for a, b in zip(ranks, ranks[1:])),
            "信赖经验门槛在原版和新增等级之间未严格递增")
    require(thresholds[11] - thresholds[10] == 50_000, "原版 10 级与新增 11 级门槛未正确衔接")
    cap = read(shared / "PalTrust99/blueprints/trust_limit.json")["BP_PalGameSetting_C"]["FriendshipPoint_Max"]
    require(thresholds[99] == cap, "99 级所需经验与蓝图上限不一致")
    print(f"成长两表核对通过。升魂 1–80，信赖 {ranks[0]}–99，99 级累计 {cap} 点。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="平放七个 JSON 的 FModel 导出目录")
    parser.add_argument("--growth-dir", type=Path, help="同一游戏构建的石像与信赖两张原版表所在目录")
    args = parser.parse_args()
    try:
        check(args.directory)
        if args.growth_dir:
            check_growth(args.growth_dir)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        sys.exit(f"核对失败：{exc}")
