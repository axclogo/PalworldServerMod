"""生成竞技场永久植入物、商店追加项和手术台配方。"""

import json
from pathlib import Path

from .custom_traits import CUSTOM_TRAITS, build_passive_tables

SURGERY_PRICE = 500_000
TRAITS = {
    "Legend": "传说",
    "ElementBoost_Normal_2_PAL": "圣天",
    "ElementBoost_Fire_2_PAL": "炎帝",
    "ElementBoost_Aqua_2_PAL": "海皇",
    "ElementBoost_Thunder_2_PAL": "雷帝",
    "ElementBoost_Leaf_2_PAL": "精灵王",
    "ElementBoost_Ice_2_PAL": "冰帝",
    "ElementBoost_Earth_2_PAL": "岩帝",
    "ElementBoost_Dark_2_PAL": "冥王",
    "ElementBoost_Dragon_2_PAL": "神龙",
}


def main():
    mod = Path(__file__).resolve().parents[1] / "mods/shared/PalArenaImplants"
    items, recipes, products = {}, {}, []
    passives, translations = build_passive_tables()
    names, descriptions = {}, {}
    traits = TRAITS | {key: value["name"] for key, value in CUSTOM_TRAITS.items()}
    for index, (trait, name) in enumerate(traits.items()):
        rainbow = trait == "Legend" or trait in CUSTOM_TRAITS
        item_id = "PalPack_Implant_" + trait
        items[item_id] = {
            "Type": "Generic",
            "ItemBaseName": item_id,
            "OverrideNameMsgID": "ITEM_NAME_" + item_id,
            "OverrideDescMsgID": "ITEM_DESC_" + item_id,
            "IconTexture": "/Game/Others/InventoryItemIcon/Texture/T_itemicon_Material_PalPassiveSkillChange.T_itemicon_Material_PalPassiveSkillChange",
            "TypeA": "EPalItemTypeA::Essential",
            "TypeB": "EPalItemTypeB::Essential_PassiveSkillChange",
            "Rank": 4,
            "Rarity": 4 if rainbow else 3,
            "Price": 1,
            "MaxStackCount": 1,
            "SortId": 6266 + index,
            "Weight": 0.0,
            "bLegalInGame": True,
        }
        names[items[item_id]["OverrideNameMsgID"]] = name + "植入物"
        descriptions[items[item_id]["OverrideDescMsgID"]] = (
            f"持有此植入物时，可在帕鲁手术台选择「{name}」。每次手术花费 {SURGERY_PRICE:,} 金币。"
            + CUSTOM_TRAITS.get(trait, {}).get("description", "")
        )
        recipes[trait] = {
            "PassiveSkill": trait, "Price": SURGERY_PRICE, "RequireItemId": item_id
        }
        # PalSchema matches nested struct keys exactly. The client reflection and
        # the cooked WindowsServer shop use different casing for this one FName.
        products.append({
            "StaticItemId": item_id,
            "StaticItemID": item_id,
            "ProductType": "EPalItemShopProductType::OnlyPurchaseOne",
            "OverridePrice": 250 if rainbow else 150,
            "ProductNum": 1,
            "Stock": 0,
        })

    translations.update({"DT_ItemNameText": names, "DT_ItemDescriptionText": descriptions})
    # The shop and inventory can request an icon by item ID. The native implant
    # icon already exists in the game. Register references, without loading textures.
    icons = {key: {"Icon": item["IconTexture"]} for key, item in items.items()}
    files = {
        "items/implants.json": items,
        "raw/implant_icons.json": {"DT_ItemIconDataTable": icons},
        "raw/surgery.json": {"DT_OperatingTablePassiveSkillDataTable": recipes},
        "raw/arena_shop.json": {"DT_ItemShopCreateData": {
            "Arena_Shop_1": {"productDataArray": {"Items": products}}
        }},
        "raw/custom_passives.json": passives,
        "translations/global/custom_passives.json": translations,
    }
    for relative, value in files.items():
        path = mod / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("已生成 4 个自定义虹色词条，以及传说、九系帝王和自定义词条的 14 项竞技场植入物。")


if __name__ == "__main__":
    main()
