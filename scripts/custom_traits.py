"""四个普通虹色词条的当前定义；使用游戏原生效果，不增加运行脚本。"""


CUSTOM_TRAITS = {
    "PalPack_Juggernaut": {
        "name": "白猪战车",
        "description": "最大生命值＋100%；防御＋150%。",
        "effects": [("MaxHP", 100), ("Defense", 150)],
        "worker_only": False,
    },
    "PalPack_Homebody": {
        "name": "宅断腿",
        "description": "担任基地工作帕鲁时：SAN值下降速度－30%；饱食度下降速度－30%；移动速度－20%；工作速度－15%。",
        "effects": [("Sanity_Decrease", -30), ("FullStomatch_Decrease", -30),
                    ("MoveSpeed", -20), ("CraftSpeed", -15)],
        "worker_only": True,
    },
    "PalPack_KaiWilderness": {
        "name": "凯旋山野",
        "description": "草属性伤害＋20%；攻击＋15%。",
        "effects": [("ElementBoost_Leaf", 20), ("ShotAttack", 15)],
        "worker_only": False,
    },
    "PalPack_PaperTiger": {
        "name": "纸老虎",
        "description": "攻击＋40%；防御－20%。",
        "effects": [("ShotAttack", 40), ("Defense", -20)],
        "worker_only": False,
    },
}


def build_passive_tables():
    rows, names, descriptions = {}, {}, {}
    for skill_id, trait in CUSTOM_TRAITS.items():
        name_id = "PASSIVE_" + skill_id
        desc_id = name_id + "_DESC"
        row = {
            "Rank": 4,
            "LotteryWeight": 0,
            "OverrideNameTextID": name_id,
            "OverrideDescMsgID": desc_id,
            "TargetElementType": "EPalElementType::None",
            "Category": "EPalPassiveCategory::SortDisplayable",
            "InvokeActiveOtomo": False,
            "InvokeWorker": trait["worker_only"],
            "InvokeRiding": False,
            "InvokeReserve": False,
            "InvokeInOtomo": False,
            "InvokeAlways": not trait["worker_only"],
            "InvokeInBaseCamp": False,
            "AddInvokeTriggerType_1": "EPalPassiveAddTriggerType::None",
            "AddInvokeTriggerType_2": "EPalPassiveAddTriggerType::None",
            "AddPal": False,
            "AddRarePal": False,
            "AddWorldTreePal": False,
            "AddMutationPal": False,
            "AddShotWeapon": False,
            "AddMeleeWeapon": False,
            "AddArmor": False,
            "AddAccessory": False,
            "IsStackablePartnerSkillBySameTribe": False,
        }
        for slot in range(1, 5):
            effect, value = trait["effects"][slot - 1] if slot <= len(trait["effects"]) else ("no", 0)
            row[f"EffectType{slot}"] = "EPalPassiveSkillEffectType::" + effect
            row[f"EffectValue{slot}"] = value
            row[f"TargetType{slot}"] = "EPalPassiveSkillEffectTargetType::" + ("None" if effect == "no" else "ToSelf")
        rows[skill_id] = row
        names[name_id] = trait["name"]
        descriptions[desc_id] = trait["description"]
    return {"DT_PassiveSkill_Main": rows}, {
        "DT_SkillNameText": names, "DT_SkillDescText": descriptions,
    }
