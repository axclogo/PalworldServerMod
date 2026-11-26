"""验证实际生成物的业务边界及双端安装包；不模拟游戏引擎。"""

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from scripts import build_soul80
from scripts.check_implant_log import check as check_implant_log
from scripts.check_implant_log import check_arena_files, check_shared_files

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "mods/shared"
INSTALL_PACKAGES = {
    "client": ("幻兽帕鲁-玩家端.zip", "玩家安装.txt", "PalFishingWin"),
    "server": ("幻兽帕鲁-服务端.zip", "服主安装.txt", None),
}
SHARED_FILES = (
    "PalTrust99/raw/trust_rank_99.json",
    "PalTrust99/blueprints/trust_limit.json",
    "PalArenaImplants/items/implants.json",
    "PalArenaImplants/raw/arena_shop.json",
    "PalArenaImplants/raw/implant_icons.json",
    "PalArenaImplants/raw/custom_passives.json",
    "PalArenaImplants/raw/surgery.json",
    "PalArenaImplants/translations/global/custom_passives.json",
    "PalFishingWin/blueprints/catch_battle.json",
    "PalElixirUncap/blueprints/elixir_cap.json",
)


def read(relative):
    return json.loads((SHARED / relative).read_text(encoding="utf-8"))


class PackTests(unittest.TestCase):
    def test_other_surgery_files_cannot_redirect_a_pack_implant_unnoticed(self):
        recipes = read("PalArenaImplants/raw/surgery.json")
        with TemporaryDirectory() as temp:
            mods = Path(temp)
            own = mods / "PalArenaImplants/raw/surgery.json"
            own.parent.mkdir(parents=True)
            own.write_text(json.dumps(recipes))
            other = mods / "Other/raw/surgery.jsonc"
            other.parent.mkdir(parents=True)
            table = "DT_OperatingTablePassiveSkillDataTable"
            for row, patch in (("Legend", {"Price": 0}), ("Legend", None),
                               ("AnotherName", {"PassiveSkill": "legend"}),
                               ("AnotherName", {"RequireItemId": "PalPack_Implant_Legend"})):
                other.write_text("// competing recipe\n" + json.dumps({table: {row: patch}}))
                with self.subTest(patch=patch), self.assertRaisesRegex(ValueError, "Other/raw/surgery"):
                    check_arena_files(mods, recipes)
            other.write_text(json.dumps({table: {"Other": {"RequireItemId": "Other"}}}))
            check_arena_files(mods, recipes)

    def test_prelaunch_requires_the_installed_shared_files_from_this_release(self):
        with TemporaryDirectory() as temp:
            active = Path(temp) / "active"
            shutil.copytree(SHARED, active)
            check_shared_files(active, SHARED)
            with self.assertRaisesRegex(ValueError, "单独解压"):
                check_shared_files(SHARED, SHARED)
            (active / "PalArenaImplants/raw/custom_passives.json").unlink()
            (active / "PalTrust99/blueprints/trust_limit.json").write_text("{}")
            with self.assertRaises(ValueError) as invalid:
                check_shared_files(active, SHARED)
            self.assertIn("缺少 PalArenaImplants/raw/custom_passives.json", str(invalid.exception))
            self.assertIn("内容不同 PalTrust99/blueprints/trust_limit.json", str(invalid.exception))

    def test_arena_detects_a_second_shop_append_even_when_recipes_are_identical(self):
        recipes = read("PalArenaImplants/raw/surgery.json")
        with TemporaryDirectory() as temp:
            active = Path(temp)
            shutil.copytree(SHARED / "PalArenaImplants", active / "PalArenaImplants")
            other = active / "PalArenaImplants.old"
            shutil.copytree(active / "PalArenaImplants", other)
            with self.assertRaisesRegex(ValueError, "再次上架 PalPack_Implant_Legend"):
                check_arena_files(active, recipes)
            shop = other / "raw/arena_shop.json"
            for stock in ([], {"Action": "Clear"}):
                shop.write_text(json.dumps({"DT_ItemShopCreateData_Common": {"Arena_Shop_1": {"productDataArray": stock}}}))
                with self.assertRaisesRegex(ValueError, "清空或替换库存"):
                    check_arena_files(active, recipes)
            shop.write_text(json.dumps({"DT_ItemShopCreateData": {"Arena_Shop_1": {
                "productDataArray": {"Items": [{"StaticItemId": "AnotherModItem"}]}}}}))
            check_arena_files(active, recipes)

    def test_cold_start_log_requires_each_published_item(self):
        items = read("PalArenaImplants/items/implants.json")
        banner = "[PalSchema] PalSchema v0.6.71 by Okaetsu loaded."
        records = [f"[PalSchema] Added Item '{item}'" for item in items]
        check_implant_log([banner, *records], items)
        for lines in ([banner, *records[:-1], records[0]], [*records, banner], [banner, *records, banner]):
            with self.subTest(lines=lines[-1]), self.assertRaises(ValueError):
                check_implant_log(lines, items)

    def test_cold_start_log_exposes_item_load_risks(self):
        items = read("PalArenaImplants/items/implants.json")
        records = ["[PalSchema] PalSchema v0.6.71 by Okaetsu loaded.",
                   *(f"[PalSchema] Added Item '{item}'" for item in items)]
        key = next(iter(items))
        check_implant_log([*records, "Modified Item 'Unrelated'", "Property 'TypeB' not found in Item 'Unrelated'."], items)
        # The loader warns about missing fields before reporting that the item was added.
        warning = f"Property 'TypeB' not found in Item '{key}'."
        with self.assertRaisesRegex(ValueError, "TypeB"):
            check_implant_log([records[0], warning, *records[1:]], items)
        for event in (f"Modified Item '{key}'", f"Deleted Item '{key}'", f"Item '{key}' is invalid. Deleting.",
                      "PalSchema will be unable to clean up invalid items"):
            with self.subTest(event=event), self.assertRaises(ValueError):
                check_implant_log([*records, event], items)

    def test_native_table_errors_are_visible_even_after_all_items_registered(self):
        items = read("PalArenaImplants/items/implants.json")
        log = ["PalSchema v0.6.71 by Okaetsu loaded.", *(f"Added Item '{item}'" for item in items)]
        summary = "DT_PassiveSkill_Main_Common: 0 rows updated, 4 rows added, 0 rows deleted, "
        check_implant_log([*log, summary + "0 errors."], items)
        for result in ("1 error.", "2 errors."):
            with self.assertRaisesRegex(ValueError, "DT_PassiveSkill_Main_Common"):
                check_implant_log([*log, summary + result], items)

    def test_soul_bounds_preserve_vanilla(self):
        rows = build_soul80.extra_rows()
        self.assertEqual(set(rows), {str(n) for n in range(21, 81)})
        self.assertEqual([r["Rank"] for r in rows.values()], list(range(21, 81)))

    def test_soul_cost_tiers_and_material(self):
        rows = build_soul80.extra_rows()
        costs = [r["RequiredItemNum"] for r in rows.values()]
        self.assertEqual(costs, [cost for cost in range(10, 33, 2) for _ in range(5)])
        self.assertEqual(sum(costs), 1260)
        self.assertEqual({r["RequiredStaticItemId"] for r in rows.values()}, {"PalUpgradeStone4"})
        self.assertEqual({r["ResetRequiredMoney"] for r in rows.values()}, {30000})

    def test_trust_ranks_and_cap_agree(self):
        rows = read("PalTrust99/raw/trust_rank_99.json")["DT_FriendshipRankTable"]
        self.assertEqual(set(rows), {f"Friendship_Rank_{n}" for n in range(11, 100)})
        points = []
        for rank in range(11, 100):
            row = rows[f"Friendship_Rank_{rank}"]
            self.assertEqual(row["FriendshipRank"], rank)
            points.append(row["RequiredPoint"])
        self.assertEqual(points[0], 250000)
        self.assertEqual(set(b - a for a, b in zip(points, points[1:])), {50000})
        settings = read("PalTrust99/blueprints/trust_limit.json")["BP_PalGameSetting_C"]
        self.assertEqual(settings, {"FriendshipPoint_Max": points[-1]})
        self.assertEqual(points[-1], 4650000)

    def test_published_implant_ids_still_resolve_to_the_same_surgery(self):
        # Existing saves carry the item IDs even if every generated cross-reference is renamed together.
        items = read("PalArenaImplants/items/implants.json")
        recipes = read("PalArenaImplants/raw/surgery.json")["DT_OperatingTablePassiveSkillDataTable"]
        traits = ["Legend", "PalPack_Juggernaut", "PalPack_Homebody", "PalPack_KaiWilderness", "PalPack_PaperTiger"]
        elements = ["Normal", "Fire", "Aqua", "Thunder", "Leaf", "Ice", "Earth", "Dark", "Dragon"]
        traits.extend(f"ElementBoost_{element}_2_PAL" for element in elements)
        for trait in traits:
            with self.subTest(trait=trait):
                saved_item_id = "PalPack_Implant_" + trait
                self.assertIn(saved_item_id, items)
                self.assertEqual(recipes[trait]["RequireItemId"], saved_item_id)
                self.assertEqual(recipes[trait]["PassiveSkill"], trait)

    def test_arena_item_recipe_and_stock_links(self):
        items = read("PalArenaImplants/items/implants.json")
        recipes = read("PalArenaImplants/raw/surgery.json")["DT_OperatingTablePassiveSkillDataTable"]
        shop = read("PalArenaImplants/raw/arena_shop.json")
        self.assertEqual(set(shop), {"DT_ItemShopCreateData"})
        self.assertEqual(set(shop["DT_ItemShopCreateData"]), {"Arena_Shop_1"})
        row = shop["DT_ItemShopCreateData"]["Arena_Shop_1"]
        self.assertEqual(set(row), {"productDataArray"})
        # PalSchema 的 Items 对象追加，直接数组或 Action:Clear 都会破坏原库存。
        self.assertEqual(set(row["productDataArray"]), {"Items"})
        products = row["productDataArray"]["Items"]
        self.assertEqual(len(items), 14)
        self.assertEqual(len(recipes), 14)
        self.assertEqual(len(products), 14)
        self.assertEqual(set(items), {p["StaticItemId"] for p in products})
        self.assertEqual(set(items), {r["RequireItemId"] for r in recipes.values()})
        for trait, recipe in recipes.items():
            self.assertEqual(recipe["PassiveSkill"], trait)
            self.assertEqual(recipe["Price"], 500_000)
            item = items[recipe["RequireItemId"]]
            self.assertEqual(item["TypeB"], "EPalItemTypeB::Essential_PassiveSkillChange")
            self.assertEqual(item["TypeA"], "EPalItemTypeA::Essential")
            self.assertEqual(item["MaxStackCount"], 1)
        for product in products:
            self.assertEqual(product["ProductType"], "EPalItemShopProductType::OnlyPurchaseOne")
            self.assertEqual(product["ProductNum"], 1)
            self.assertEqual(product["OverridePrice"], 250 if items[product["StaticItemId"]]["Rarity"] == 4 else 150)

    def test_both_archives_resolve_arena_display_from_the_sold_item(self):
        expected = {"传说", "圣天", "炎帝", "海皇", "雷帝", "精灵王", "冰帝", "岩帝", "冥王", "神龙",
                    "白猪战车", "宅断腿", "凯旋山野", "纸老虎"}
        prefix = "Mods/PalSchema/mods/PalArenaImplants/"
        for archive, _, _ in INSTALL_PACKAGES.values():
            with self.subTest(archive=archive), ZipFile(ROOT / "安装包" / archive) as package:
                items = json.loads(package.read(prefix + "items/implants.json"))
                texts = json.loads(package.read(prefix + "translations/global/custom_passives.json"))
                icons = json.loads(package.read(prefix + "raw/implant_icons.json"))["DT_ItemIconDataTable"]
                shop = json.loads(package.read(prefix + "raw/arena_shop.json"))
                stock = shop["DT_ItemShopCreateData"]["Arena_Shop_1"]["productDataArray"]["Items"]
                names = []
                for product in stock:
                    # PalSchema reads the one key supplied by the reflected struct.
                    self.assertEqual(product["StaticItemID"], product["StaticItemId"])
                    item_id = product["StaticItemID"]
                    item = items[item_id]
                    self.assertEqual(item["ItemBaseName"], item_id)
                    names.append(texts["DT_ItemNameText"][item["OverrideNameMsgID"]])
                    desc = texts["DT_ItemDescriptionText"][item["OverrideDescMsgID"]]
                    self.assertIn("500,000", desc)
                    self.assertEqual(icons[item["ItemBaseName"]]["Icon"], item["IconTexture"])
                    self.assertNotIn("Name", item)  # 物品登记过程不依赖翻译表。
                    self.assertNotIn("Description", item)
                self.assertCountEqual(names, [name + "植入物" for name in expected])

    def test_shared_blueprint_fields_do_not_conflict(self):
        owners = {}
        for path in SHARED.glob("*/blueprints/*.json"):
            for target, values in json.loads(path.read_text()).items():
                for field in values:
                    key = target, field
                    self.assertNotIn(key, owners, f"duplicate field {key}: {path}")
                    owners[key] = path
        self.assertEqual(set(owners), {
            ("BP_PalGameSetting_C", "FriendshipPoint_Max"),
            ("BP_PalFishingSystem_C", "CatchBattleParameter"),
            ("BP_PalGameSetting_C", "MaxUseablePoint_SumStatusPointAndExStatusPoint_PerParameter"),
        })

    def test_fishing_only_changes_native_battle_progress(self):
        fields = read("PalFishingWin/blueprints/catch_battle.json")["BP_PalFishingSystem_C"]
        self.assertEqual(fields, {"CatchBattleParameter": {
            "RequiredCatchAmount": 1.0, "DefaultProgressAmount": 1.0, "MissFightCatchAmount": 0.0,
        }})
        self.assertTrue(all(type(value) is float for value in fields["CatchBattleParameter"].values()))

    def test_clean_build_reproduces_the_two_distributed_packages(self):
        with TemporaryDirectory() as temp:
            project = Path(temp)
            for directory in ("scripts", "mods", "docs"):
                shutil.copytree(ROOT / directory, project / directory)
            for name in ("build_pack.py", "THIRD_PARTY_NOTICES.md"):
                shutil.copy2(ROOT / name, project / name)
            # Rebuild the generated PalSchema payloads from source.
            for mod in ("PalArenaImplants", "PalTrust99"):
                for output in (project / "mods/shared" / mod).rglob("*.json"):
                    output.unlink()
            result = subprocess.run([sys.executable, "-B", "build_pack.py"], cwd=project,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({p.relative_to(project) for p in project.rglob("*.zip")},
                             {Path("安装包") / name for name, _, _ in INSTALL_PACKAGES.values()})
            for name, _, _ in INSTALL_PACKAGES.values():
                relative = Path("安装包") / name
                with ZipFile(project / relative) as rebuilt, ZipFile(ROOT / relative) as distributed:
                    self.assertCountEqual(rebuilt.namelist(), distributed.namelist())
                    for member in rebuilt.namelist():
                        self.assertEqual(rebuilt.read(member), distributed.read(member), f"{name}/{member}")

    def test_install_packages_match_role_and_sources(self):
        for side, (archive, guide, lua_mod) in INSTALL_PACKAGES.items():
            with self.subTest(side=side), ZipFile(ROOT / "安装包" / archive) as package:
                expected = {f"Mods/PalSchema/mods/{name}": (SHARED / name).read_bytes()
                            for name in SHARED_FILES}
                guide_text = (ROOT / "docs" / guide).read_text(encoding="utf-8-sig")
                expected["安装说明.txt"] = guide_text.replace("\n", "\r\n").encode("utf-8-sig")
                expected["Pal/Content/Paks/~mods/PalSoulCap80_P.pak"] = build_soul80.PAK.read_bytes()
                expected["Mods/PalSchema/enabled.txt"] = b""
                if lua_mod:
                    expected[f"Mods/{lua_mod}/enabled.txt"] = b""
                    lua_path = Path(lua_mod) / "Scripts/main.lua"
                    expected[f"Mods/{lua_path.as_posix()}"] = (ROOT / "mods" / side / lua_path).read_bytes()
                if side == "client":
                    for name in ("PalMapReveal", "PalGliderVisual"):
                        expected[f"Mods/{name}/enabled.txt"] = b""
                        expected[f"Mods/{name}/Scripts/main.lua"] = (
                            ROOT / "mods/client" / name / "Scripts/main.lua").read_bytes()
                    expected["Mods/PalFishingWin/THIRD_PARTY_NOTICES.md"] = (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes()
                else:
                    expected["检查植入物.py"] = (ROOT / "scripts/check_implant_log.py").read_bytes()
                self.assertCountEqual(package.namelist(), expected.keys())
                for name, contents in expected.items():
                    self.assertEqual(package.read(name), contents, name)

    def test_project_document_links_resolve(self):
        for doc in ROOT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((doc.parent / target.split("#")[0]).exists(), f"{doc.name}: {target}")


if __name__ == "__main__":
    unittest.main()
