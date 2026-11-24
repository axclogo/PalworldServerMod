"""直接从待发的两份 ZIP 连续五次验收。需要 Python 3.9+、Lua 5.4、repak、UAssetGUI 和九张原版导出表。"""

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from check_game_export import check, check_growth


ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = {"client": "幻兽帕鲁-玩家端.zip", "server": "幻兽帕鲁-服务端.zip"}


def fingerprint():
    return {p.relative_to(ROOT): sha256(p.read_bytes()).digest()
            for p in ROOT.rglob("*") if p.is_file()
            and not any(part.startswith(".") or part == "__pycache__" for part in p.relative_to(ROOT).parts)}


def check_both_archives(game_tables, lua, unpacked, repak, uassetgui):
    for side, archive in ARCHIVES.items():
        with ZipFile(ROOT / "安装包" / archive) as package:
            corrupt = package.testzip()
            if corrupt:
                raise ValueError(f"{archive} 中 {corrupt} 损坏")
            package.extractall(unpacked / side)
        shared = unpacked / side / "Mods/PalSchema/mods"
        check(game_tables, shared)
        check_growth(game_tables, shared, soul_pak=unpacked / side / "Pal/Content/Paks/~mods/PalSoulCap80_P.pak",
                     repak=repak, uassetgui=uassetgui)
    subprocess.run([sys.executable, "-B", unpacked / "server/检查植入物.py", "--mods-dir",
                    unpacked / "client/Mods/PalSchema/mods"], check=True)
    subprocess.run([lua, ROOT / "tests/test_runtime.lua", unpacked], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_tables", type=Path)
    parser.add_argument("--lua", default="lua")
    parser.add_argument("--repak", default="repak")
    parser.add_argument("--uassetgui", default="UAssetGUI")
    args = parser.parse_args()
    initial = fingerprint()
    for round_number in range(1, 6):
        subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests",
                        "-p", "test_*.py"], cwd=ROOT, check=True)
        with TemporaryDirectory() as temporary:
            check_both_archives(args.game_tables, args.lua, Path(temporary), args.repak, args.uassetgui)
        if fingerprint() != initial:
            sys.exit("验收期间文件有变化。请重新构建并从第一轮开始。")
        print(f"整包离线验收 {round_number}/5 通过", flush=True)


if __name__ == "__main__":
    main()
