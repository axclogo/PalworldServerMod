"""生成信赖 99 的等级表与经验上限。"""

import json
from pathlib import Path


def main():
    rows = {
        f"Friendship_Rank_{rank}": {
            "FriendshipRank": rank,
            "RequiredPoint": 200000 + (rank - 10) * 50000,
        }
        for rank in range(11, 100)
    }
    root = Path(__file__).resolve().parents[1]
    mod = root / "mods/shared/PalTrust99"
    target = mod / "raw/trust_rank_99.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"DT_FriendshipRankTable": rows}, indent=2) + "\n",
        encoding="utf-8",
    )
    settings = mod / "blueprints/trust_limit.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({
        "BP_PalGameSetting_C": {"FriendshipPoint_Max": 4650000}
    }, indent=2) + "\n", encoding="utf-8")
    print(f"已生成 {target} 和 {settings}")


if __name__ == "__main__":
    main()
