# -*- coding: utf-8 -*-
"""
STANAG 5516 Edition 9 (Link 16) Teşhis Çıkarım Modülü
Format: [1 Harf Kimlik] + [2 Harf Platform] + [2 Harf Görev/Activity] (Örn: FFTCP, FBMBM, KFTIN)
"""


class Link16Ed9Extractor:
    # 1. Karakter: Kimlik (Poz 4 - DFI 279 / DUI 001)
    ID_MAP = {
        "0": ("P", "Pending (000)"),
        "1": ("U", "Unknown (001)"),
        "2": ("A", "Assumed Friend (010)"),
        "3": ("F", "Friend (011)"),
        "4": ("N", "Neutral (100)"),
        "5": ("S", "Suspect (101)"),
        "6": ("H", "Hostile (110)"),
    }

    # Hava (01) Entity (Poz 11-16) -> (Platform_2Harf, Varsayılan_Görev_2Harf, Açıklama)
    AIR_ENT = {
        "110000": ("FW", "NS", "Military Air"),
        "110100": ("FW", "NS", "Fixed Wing"),
        "110101": ("FT", "CP", "Fighter (CAP)"),
        "110102": ("FB", "AT", "Fighter/Bomber"),
        "110103": ("BM", "BM", "Bomber"),
        "110104": ("CA", "AL", "Cargo / Airlift"),
        "110105": ("JM", "JM", "ECM / Jammer"),
        "110106": ("TK", "TK", "Tanker"),
        "110107": ("PT", "PT", "Patrol"),
        "110108": ("RS", "SR", "Rescue / SAR"),
        "110109": ("RC", "RC", "Reconnaissance"),
        "110110": ("EW", "EW", "AEW / AWACS"),
        "110111": ("ES", "RC", "ESM / Surveillance"),
        "110112": ("AS", "AW", "ASW"),
        "110113": ("TR", "TR", "Trainer"),
        "110114": ("UT", "UT", "Utility"),
        "110115": ("CP", "CC", "Command Post (C2)"),
        "110123": ("AT", "AT", "Attack / Strike"),
        "110200": ("HL", "NS", "Helicopter"),
        "110300": ("UV", "RC", "UAV / İHA"),
        "110400": ("VS", "NS", "VSTOL"),
        "120000": ("CV", "CA", "Civil Aircraft"),
        "120100": ("CV", "PA", "Civil Fixed Wing"),
        "120200": ("CH", "CA", "Civil Helicopter"),
        "130000": ("DC", "DC", "Decoy"),
    }

    # Hava Sector 1 Modifier (Poz 17-18) -> (Platform_Override, Görev_2Harf, Açıklama)
    AIR_MOD1 = {
        "01": ("AT", "AT", "Attack"),
        "02": ("BM", "BM", "Bomber"),
        "03": ("CA", "AL", "Cargo / Airlift"),
        "04": ("FT", "CP", "Fighter / CAP"),
        "05": ("FT", "IN", "Interceptor"),
        "06": ("TK", "TK", "Tanker"),
        "07": ("UT", "UT", "Utility"),
        "08": ("VS", "NS", "VSTOL"),
        "09": ("CV", "PA", "Passenger"),
        "10": ("AS", "AW", "ASW"),
        "11": ("MC", "MC", "MCM"),
        "12": ("CP", "CC", "Command & Control (C2)"),
        "13": ("JM", "JM", "Jammer / ECM"),
        "14": ("ES", "EW", "Electronic Warfare"),
        "15": ("RC", "RC", "Reconnaissance"),
        "16": ("EW", "EW", "AEW / AWACS"),
        "17": ("AS", "SU", "ASUW"),
        "18": ("FB", "AT", "Fighter / Bomber"),
        "19": ("RS", "SR", "SAR"),
        "20": ("RS", "CS", "CSAR"),
        "24": ("SF", "SF", "SOF"),
        "29": ("TR", "TR", "Trainer"),
        "32": ("AT", "CS", "Close Air Support (CAS)"),
        "33": ("AT", "SD", "SEAD"),
    }

    # Deniz (30), Sualtı (35/36) ve Kara (10/15/20) özet eşleşmeleri
    OTHER_ENT = {
        "30": {
            "120100": ("CV", "AC", "Carrier"),
            "120202": ("CG", "SU", "Cruiser"),
            "120203": ("DD", "SU", "Destroyer"),
            "120204": ("FF", "SU", "Frigate"),
            "120205": ("FS", "PT", "Corvette"),
            "120300": ("AM", "AM", "Amphibious"),
            "120400": ("MW", "MC", "Mine Warfare"),
            "120500": ("PC", "PT", "Patrol Craft"),
            "140000": ("MC", "MR", "Merchant"),
            "150100": ("FV", "FS", "Fishing"),
        },
        "35": {
            "110100": ("SS", "PT", "Submarine"),
            "110101": ("SN", "PT", "Nuclear Submarine"),
            "110102": ("SK", "PT", "Conventional Submarine"),
            "130100": ("TP", "AT", "Torpedo"),
            "130200": ("MN", "MW", "Sea Mine"),
        },
        "10": {
            "120500": ("AR", "AT", "Armor / Tank"),
            "121100": ("IN", "GD", "Infantry"),
            "130100": ("AD", "AD", "Air Defense"),
            "130102": ("SM", "AD", "SAM"),
            "130300": ("FA", "FS", "Field Artillery"),
            "140700": ("RC", "RC", "Recon"),
            "150500": ("EW", "JM", "Electronic Warfare"),
            "151000": ("RD", "SV", "Radar"),
        },
    }

    # milstd2525e_sidc.py içindeki metin etiketlerinden otomatik yakalama (Fallback)
    KEYWORD_RULES = [
        ("fighter/bomber", ("FB", "AT")),
        ("fighter", ("FT", "CP")),
        ("interceptor", ("FT", "IN")),
        ("bomber", ("BM", "BM")),
        ("attack", ("AT", "AT")),
        ("strike", ("AT", "AT")),
        ("tanker", ("TK", "TK")),
        ("cargo", ("CA", "AL")),
        ("airlift", ("CA", "AL")),
        ("jammer", ("JM", "JM")),
        ("ecm", ("JM", "JM")),
        ("aew", ("EW", "EW")),
        ("awacs", ("EW", "EW")),
        ("recon", ("RC", "RC")),
        ("rescue", ("RS", "SR")),
        ("sar", ("RS", "SR")),
        ("asw", ("AS", "AW")),
        ("patrol", ("PT", "PT")),
        ("trainer", ("TR", "TR")),
        ("utility", ("UT", "UT")),
        ("uav", ("UV", "RC")),
        ("unmanned", ("UV", "RC")),
        ("helicopter", ("HL", "NS")),
        ("rotary", ("HL", "NS")),
        ("missile", ("MS", "AT")),
        ("frigate", ("FF", "SU")),
        ("destroyer", ("DD", "SU")),
        ("cruiser", ("CG", "SU")),
        ("carrier", ("CV", "AC")),
        ("submarine", ("SS", "PT")),
        ("mine", ("MN", "MW")),
    ]

    @classmethod
    def extract(cls, sidc: str, ent_label: str = "", mod1_label: str = "", mod2_label: str = "") -> dict:
        s = (sidc or "").strip()
        if len(s) < 20:
            return {"code": "-----", "summary": "Geçersiz SIDC", "detail": ""}

        ctx, ident, symset = s[2], s[3], s[4:6]
        entity, mod1, mod2 = s[10:16], s[16:18], s[18:20]

        # 1. Harf: Kimlik + Joker/Faker
        c1, id_desc = cls.ID_MAP.get(ident, ("U", "Unknown"))
        if ctx == "1":
            if ident == "6":
                c1, id_desc = "K", "FAKER (Exercise Hostile)"
            elif ident == "5":
                c1, id_desc = "J", "JOKER (Exercise Suspect)"

        # 2-3. Harf (Platform) ve 4-5. Harf (Görev/Activity)
        plat, act, desc = "NS", "NS", "Tanımsız"

        if symset == "01":
            row = cls._lookup(cls.AIR_ENT, entity)
            if row:
                plat, act, desc = row
            if mod1 in cls.AIR_MOD1:
                m_plat, m_act, m_desc = cls.AIR_MOD1[mod1]
                act = m_act
                # Entity genel "Fixed Wing (110100)" ise Platform kodunu da Modifier belirler:
                if entity in ("110000", "110100", "000000"):
                    plat = m_plat
                desc = f"{desc} + {m_desc}"
        elif symset == "02":
            plat, act, desc = "MS", "AT", "Air Missile"
        elif symset in ("05", "06"):
            plat, act, desc = "SV", "OR", "Space Vehicle"
        elif symset in cls.OTHER_ENT:
            row = cls._lookup(cls.OTHER_ENT[symset], entity)
            if row:
                plat, act, desc = row

        # Eğer tabloda özel karşılığı yoksa combobox metinlerinden otomatik çıkar:
        combined_text = f"{ent_label} {mod1_label} {mod2_label}".lower()
        if plat in ("NS", "FW") or act == "NS":
            for kw, (k_plat, k_act) in cls.KEYWORD_RULES:
                if kw in combined_text:
                    if plat in ("NS", "FW"):
                        plat = k_plat
                    if act == "NS":
                        act = k_act
                    break

        code_5char = f"{c1}{plat}{act}"
        return {
            "code": code_5char,
            "summary": f"[{c1}: Kimlik] + [{plat}: Platform] + [{act}: Görev]",
            "detail": f"Kimlik: {id_desc} | Entity: {entity} | Mod1: {mod1} ({desc})",
        }

    @staticmethod
    def _lookup(table: dict, entity: str):
        return (
            table.get(entity)
            or table.get(entity[:4] + "00")
            or table.get(entity[:2] + "0000")
        )