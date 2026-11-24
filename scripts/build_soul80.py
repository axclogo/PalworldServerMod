"""从原版熟化石像表生成双端共用的升魂 PAK。仅开发者重制资源时使用。"""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
TABLE = "DT_CharacterUpgradeMasterDataTable"
ASSET = Path("Pal/Content/Pal/DataTable/Character") / (TABLE + ".uasset")
PAK = ROOT / "mods/shared/PalSoulCap80/PalSoulCap80_P.pak"
INSTALL_PATH = "Pal/Content/Paks/~mods/" + PAK.name


def extra_rows():
    return {str(rank): {"Rank": rank, "RequiredStaticItemId": "PalUpgradeStone4",
                        "RequiredItemNum": 10 + 2 * ((rank - 21) // 5), "ResetRequiredMoney": 30000}
            for rank in range(21, 81)}


def table_rows(asset):
    table, = asset["Exports"]
    if (table["ObjectName"] != TABLE or table["bNotForClient"] or table["bNotForServer"]
            or asset["FolderName"] != "/Game/Pal/DataTable/Character/" + TABLE):
        raise ValueError("需要双端均可加载的原版石像表")
    return table["Table"]["Data"]


def values(row):
    return {field["Name"]: field["Value"] for field in row["Value"]}


def extend(asset):
    rows = table_rows(asset)
    existing = {row["Name"]: row for row in rows}
    if len(rows) != 20 or set(existing) != {str(i) for i in range(1, 21)}:
        raise ValueError("原版等级已变化，请先核对当前版本的 1–20 级")
    template = existing["20"]
    if values(template) != {"Rank": 20, "RequiredStaticItemId": "PalUpgradeStone4",
                            "RequiredItemNum": 4, "ResetRequiredMoney": 30000}:
        raise ValueError("原版第 20 级材料、价格或结构已变化")
    added_names = []
    for name, fields in extra_rows().items():
        row = deepcopy(template)
        row["Name"] = name
        for prop in row["Value"]:
            prop["Value"] = fields[prop["Name"]]
        rows.append(row)
        if name not in asset["NameMap"]:
            added_names.append(name)
    # Cooked 包把导出数据引用的名字放在 NameMap 前部。
    boundary = asset["NamesReferencedFromExportDataCount"]
    asset["NameMap"][boundary:boundary] = added_names
    asset["NamesReferencedFromExportDataCount"] += len(added_names)
    asset["Generations"][-1]["NameCount"] = len(asset["NameMap"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="原版 .uasset 文件，.uexp 与它放在一起")
    parser.add_argument("--uassetgui", default="UAssetGUI")
    parser.add_argument("--repak", default="repak")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        work = Path(tmp)
        document = work / "table.json"
        cooked = work / "content" / ASSET
        cooked.parent.mkdir(parents=True)
        subprocess.run([args.uassetgui, "tojson", args.original, document, "VER_UE5_1"], check=True)
        asset = json.loads(document.read_text(encoding="utf-8-sig"))
        extend(asset)
        document.write_text(json.dumps(asset, ensure_ascii=False), encoding="utf-8")
        subprocess.run([args.uassetgui, "fromjson", document, cooked], check=True)
        expected = {row["Name"]: values(row) for row in table_rows(asset)}
        subprocess.run([args.uassetgui, "tojson", cooked, document, "VER_UE5_1"], check=True)
        saved = table_rows(json.loads(document.read_text(encoding="utf-8-sig")))
        if len(saved) != 80 or {row["Name"]: values(row) for row in saved} != expected:
            raise ValueError("熟化资产读回的等级或费用与设计不一致")
        output = work / PAK.name
        subprocess.run([args.repak, "pack", "--version", "V11", work / "content", output], check=True)
        PAK.write_bytes(output.read_bytes())


if __name__ == "__main__":
    main()
