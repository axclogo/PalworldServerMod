"""按用户定稿核对生成物，防止错属性、错正负号、漏翻译或漏植入物。"""

import json
from pathlib import Path
import unittest


MOD = Path(__file__).resolve().parents[1] / "mods/shared/PalArenaImplants"
EXPECTED = {
    "PalPack_Juggernaut": ("白猪战车", {"MaxHP": 100, "Defense": 150}),
    "PalPack_Homebody": ("宅断腿", {"Sanity_Decrease": -30, "FullStomatch_Decrease": -30,
                                  "MoveSpeed": -20, "CraftSpeed": -15}),
    "PalPack_KaiWilderness": ("凯旋山野", {"ElementBoost_Leaf": 20, "ShotAttack": 15}),
    "PalPack_PaperTiger": ("纸老虎", {"ShotAttack": 40, "Defense": -20}),
}


def read(name):
    return json.loads((MOD / name).read_text(encoding="utf-8"))


class CustomTraitTests(unittest.TestCase):
    def setUp(self):
        self.rows = read("raw/custom_passives.json")["DT_PassiveSkill_Main"]

    def test_exact_effects_values_and_self_targets(self):
        self.assertEqual(set(self.rows), set(EXPECTED))
        for skill_id, (_, expected) in EXPECTED.items():
            row = self.rows[skill_id]
            effects = {}
            for slot in range(1, 5):
                effect = row[f"EffectType{slot}"].removeprefix("EPalPassiveSkillEffectType::")
                value = row[f"EffectValue{slot}"]
                target = row[f"TargetType{slot}"]
                if effect == "no":
                    self.assertEqual(value, 0)
                    self.assertEqual(target, "EPalPassiveSkillEffectTargetType::None")
                else:
                    self.assertNotIn(effect, effects)
                    effects[effect] = value
                    self.assertEqual(target, "EPalPassiveSkillEffectTargetType::ToSelf")
            self.assertEqual(effects, expected, skill_id)

    def test_rainbow_not_world_tree_or_random_spawns(self):
        for row in self.rows.values():
            self.assertEqual(row["Rank"], 4)
            self.assertEqual(row["LotteryWeight"], 0)
            for field in ("AddPal", "AddRarePal", "AddWorldTreePal", "AddMutationPal",
                          "AddShotWeapon", "AddMeleeWeapon", "AddArmor", "AddAccessory"):
                self.assertIs(row[field], False)
            self.assertEqual(row["Category"], "EPalPassiveCategory::SortDisplayable")

    def test_homebody_only_applies_as_base_worker(self):
        for skill_id, row in self.rows.items():
            self.assertEqual(row["InvokeWorker"], skill_id == "PalPack_Homebody")
            self.assertEqual(row["InvokeAlways"], skill_id != "PalPack_Homebody")
            for field in ("InvokeActiveOtomo", "InvokeRiding", "InvokeReserve", "InvokeInOtomo", "InvokeInBaseCamp"):
                self.assertIs(row[field], False)
            for slot in (1, 2):
                self.assertEqual(row[f"AddInvokeTriggerType_{slot}"], "EPalPassiveAddTriggerType::None")

    def test_kai_grass_damage_does_not_require_a_grass_pal(self):
        row = self.rows["PalPack_KaiWilderness"]
        self.assertEqual(row["TargetElementType"], "EPalElementType::None")
        self.assertEqual(row["EffectType1"], "EPalPassiveSkillEffectType::ElementBoost_Leaf")

    def test_localization_resolves_names_and_descriptions(self):
        text = read("translations/global/custom_passives.json")
        self.assertEqual(len(text["DT_SkillNameText"]), 4)
        self.assertEqual(len(text["DT_SkillDescText"]), 4)
        for skill_id, (name, _) in EXPECTED.items():
            row = self.rows[skill_id]
            self.assertEqual(text["DT_SkillNameText"][row["OverrideNameTextID"]], name)
            description = text["DT_SkillDescText"][row["OverrideDescMsgID"]]
            self.assertTrue(description)
        kai = text["DT_SkillDescText"][self.rows["PalPack_KaiWilderness"]["OverrideDescMsgID"]]
        self.assertEqual(kai, "草属性伤害＋20%；攻击＋15%。")

    def test_all_four_have_one_purchase_and_native_surgery_recipe(self):
        recipes = read("raw/surgery.json")["DT_OperatingTablePassiveSkillDataTable"]
        items = read("items/implants.json")
        products = read("raw/arena_shop.json")["DT_ItemShopCreateData"]["Arena_Shop_1"]["productDataArray"]["Items"]
        for skill_id, (name, _) in EXPECTED.items():
            recipe = recipes[skill_id]
            self.assertEqual(recipe["PassiveSkill"], skill_id)
            item_id = recipe["RequireItemId"]
            names = read("translations/global/custom_passives.json")["DT_ItemNameText"]
            self.assertEqual(names[items[item_id]["OverrideNameMsgID"]], name + "植入物")
            self.assertEqual(items[item_id]["Rarity"], 4)
            listed = [p for p in products if p["StaticItemId"] == item_id]
            self.assertEqual(len(listed), 1)
            self.assertEqual(listed[0]["OverridePrice"], 250)
            self.assertEqual(listed[0]["ProductType"], "EPalItemShopProductType::OnlyPurchaseOne")
            self.assertEqual(recipe["Price"], 500_000)


if __name__ == "__main__":
    unittest.main()
