"""重新生成双端共享数据和两份中文安装包。Python 3.9+。"""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from scripts import build_arena, build_soul80, build_trust99
from scripts.check_implant_log import SHARED


ROOT = Path(__file__).resolve().parent

def write_package(side, title, guide, lua_mods):
    archive = ROOT / "安装包" / f"幻兽帕鲁-{title}.zip"
    text = (ROOT / "docs" / guide).read_text(encoding="utf-8")
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as package:
        package.writestr("安装说明.txt", text.replace("\n", "\r\n").encode("utf-8-sig"))
        package.write(build_soul80.PAK, build_soul80.INSTALL_PATH)
        for mod, files in SHARED.items():
            for file in files:
                source = ROOT / "mods/shared" / mod / file
                package.write(source, f"Mods/PalSchema/mods/{mod}/{file}")
        package.writestr("Mods/PalSchema/enabled.txt", b"")
        for name in lua_mods:
            package.write(ROOT / "mods" / side / name / "Scripts/main.lua", f"Mods/{name}/Scripts/main.lua")
            package.writestr(f"Mods/{name}/enabled.txt", b"")
        if side == "client":
            package.write(ROOT / "THIRD_PARTY_NOTICES.md", "Mods/PalFishingWin/THIRD_PARTY_NOTICES.md")
        else:
            package.write(ROOT / "scripts/check_implant_log.py", "检查植入物.py")
    print(f"已打包 {archive}")


def main():
    build_trust99.main()
    build_arena.main()
    (ROOT / "安装包").mkdir(exist_ok=True)
    write_package("server", "服务端", "服主安装.txt", ("PalGroundStacksRuntime",))
    write_package("client", "玩家端", "玩家安装.txt", ("PalFishingWin", "PalMapReveal", "PalGliderVisual"))


if __name__ == "__main__":
    main()
