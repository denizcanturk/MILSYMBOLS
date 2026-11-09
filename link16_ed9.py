# -*- coding: utf-8 -*-
"""
STANAG 5516 Ed. 9 (Link 16) teşhis motoru.

30 haneli MIL-STD-2525E SIDC <-> 5 karakterli Link 16 teşhis kodu
([1:Kimlik] + [2:Platform] + [2:Activity]) dönüşümü.

Bu modül GUI'den bağımsızdır (tkinter içe aktarmaz); hem görselleştirici
hem de testler tarafından doğrudan kullanılır.
"""

from functools import lru_cache


class Link16Ed9Extractor:
    """
    30 haneli MIL-STD-2525E SIDC kodundan STANAG 5516 Edition 9
    5 karakterli teşhis kodunu ([1:Kimlik] + [2:Platform] + [2:Activity]) çıkarır.
    """

    ID_CHAR = {
        "0": ("P", "000", "Pending (Beklemede)"),
        "1": ("U", "001", "Unknown (Bilinmeyen)"),
        "2": ("A", "010", "Assumed Friend (Muhtemel Dost)"),
        "3": ("F", "011", "Friend (Dost)"),
        "4": ("N", "100", "Neutral (Tarafsız)"),
        "5": ("S", "101", "Suspect (Şüpheli)"),
        "6": ("H", "110", "Hostile (Düşman)"),
    }

    # SIDC Context (Poz 3) değerlerinden tatbikat (EX=1) sayılanlar:
    # 1 - Exercise, 5 - Restricted Target - Exercise, 6 - No-Strike Entity - Exercise
    EXERCISE_CONTEXTS = frozenset({"1", "5", "6"})

    # ------------------------------------------------------------------
    # Tablolar: anahtarlar milstd2525e_sidc.py menü tablosundaki 2525E
    # kodlarıyla birebir aynıdır (tests/ altındaki tutarlılık testi kontrol eder).
    # (Platform, Activity) harf kodları önceki sürümden aynen korunmuştur;
    # STANAG 5516 Ed.9 ile ayrıca doğrulanmamıştır.
    # ------------------------------------------------------------------

    # Hava (Symbol Set 01) Entity (Poz 11-16) -> (Platform, Activity, Açıklama)
    AIR_ENTITY_MAP = {
        "110000": ("NS", "NS", "Military Air (Askeri Hava Genel)"),
        "110100": ("FW", "NS", "Fixed Wing (Sabit Kanat)"),
        "110102": ("AT", "AT", "Attack/Strike (Taarruz)"),
        "110103": ("BM", "BM", "Bomber (Bombardıman)"),
        "110104": ("FT", "CP", "Fighter (Av/Önleme)"),
        "110105": ("FB", "AT", "Fighter Bomber (Av-Bombardıman)"),
        "110107": ("TP", "TP", "Cargo / Transport (Nakliye)"),
        "110108": ("EW", "EW", "EC/Jammer (EW/ECM)"),
        "110109": ("TK", "TK", "Tanker (Hava Yakıt İkmal)"),
        "110110": ("PL", "PL", "Patrol (Karakol)"),
        "110111": ("RE", "RE", "Reconnaissance (Keşif)"),
        "110112": ("TR", "TR", "Trainer (Eğitim)"),
        "110113": ("UT", "UT", "Utility (Genel Maksat)"),
        "110114": ("VS", "NS", "VSTOL"),
        "110115": ("AP", "CC", "Airborne Command Post (ACP)"),
        "110116": ("AE", "AE", "AEW & C / AWACS"),
        "110118": ("AS", "AW", "Anti-Submarine Warfare (ASW)"),
        "110120": ("SR", "CS", "Combat Search and Rescue (CSAR)"),
        "110125": ("SR", "SR", "Search and Rescue (Arama Kurtarma)"),
        "110200": ("HL", "NS", "Rotary Wing / Helicopter (Döner Kanat)"),
        "110300": ("RP", "RP", "Remotely Piloted Vehicle (RPV/UAV)"),
        "120000": ("CG", "CA", "Civil - General"),
        "120100": ("CA", "PA", "Civil - Fixed Wing / Airliner"),
        "120200": ("CH", "CA", "Civil Helicopter"),
        "130200": ("DE", "DE", "Decoy"),
    }

    # Hava Sector 1 Modifier (Poz 17-18)
    AIR_MOD1_MAP = {
        "01": ("AT", "AT", "Attack/Strike"),
        "02": ("BM", "BM", "Bomber"),
        "03": ("TP", "TP", "Cargo / Transport"),
        "04": ("FT", "CP", "Fighter / CAP"),
        "05": ("IN", "IN", "Interceptor"),
        "06": ("TK", "TK", "Tanker"),
        "07": ("UT", "UT", "Utility"),
        "08": ("VS", "NS", "VSTOL/VTOL"),
        "09": ("CA", "PA", "Passenger (Airliner)"),
        "11": ("AP", "CC", "Airborne Command Post"),
        "12": ("AE", "AE", "AEW & C"),
        "16": ("EW", "EW", "EC/Jammer"),
        "18": ("RE", "RE", "Reconnaissance"),
        "19": ("TR", "TR", "Trainer"),
        "22": ("AS", "AW", "ASW"),
        "25": ("HM", "MC", "Mine Countermeasures"),
        "26": ("SR", "SR", "Search and Rescue"),
        "30": ("SR", "CS", "CSAR"),
        "32": ("AM", "SU", "Antisurface Warfare (ASUW)"),
        "33": ("FB", "AT", "Fighter/Bomber"),
    }

    # Hava Sector 2 Modifier (Poz 19-20)
    AIR_MOD2_MAP = {
        "01": ("HV", "Heavy"),
        "02": ("MD", "Medium"),
        "03": ("LT", "Light"),
        "04": ("TB", "Tanker Boom Only"),
        "05": ("TD", "Tanker Drogue Only"),
    }

    # Deniz Suüstü (Symbol Set 30)
    SURFACE_ENTITY_MAP = {
        "120000": ("SC", "NS", "Military Combatant"),
        "120100": ("CV", "AC", "Aircraft Carrier"),
        "120200": ("SC", "SU", "Surface Combatant"),
        "120201": ("BB", "SU", "Battleship"),
        "120202": ("CC", "SU", "Cruiser"),
        "120203": ("DD", "SU", "Destroyer"),
        "120204": ("FF", "SU", "Frigate"),
        "120300": ("AM", "AM", "Amphibious"),
        "120400": ("MW", "MC", "Mine Warfare Ship"),
        "120500": ("PT", "PT", "Patrol Boat"),
        "130100": ("AS", "SP", "Auxiliary Ship"),
        "140100": ("MV", "MR", "Merchant Vessel"),
        "140101": ("AS", "CG", "Cargo, General"),
        "140109": ("TK", "TK", "Oiler/Tanker"),
        "140110": ("NM", "PA", "Passenger"),
        "140200": ("FV", "FS", "Fishing Vessel"),
    }

    # Sualtı (Symbol Set 35); deniz mayını Symbol Set 36'dadır
    SUBSURFACE_ENTITY_MAP = {
        "110000": ("SS", "NS", "Subsurface Military"),
        "110100": ("SS", "PT", "Submarine"),
        "130100": ("TP", "AT", "Torpedo"),
        "130300": ("DE", "DC", "Decoy"),
    }

    # Sector 2 modifier'ı platformu belirleyen özel durumlar:
    # symbol_set -> mod2 -> {entity: (Platform, Activity, Açıklama)}
    MOD2_OVERRIDES = {
        "30": {
            "09": {"120500": ("FP", "PT", "Fast Patrol Boat")},
        },
        "35": {
            "06": {"110100": ("NG", "PT", "Nuclear Powered Submarine (SSN)")},
            "02": {"110100": ("DG", "PT", "Diesel Electric Submarine (SSK)")},
        },
    }

    # Kara Birlik (Symbol Set 10)
    LAND_UNIT_MAP = {
        "110000": ("CC", "CC", "Command and Control"),
        "120500": ("AM", "AT", "Armor/Mechanized"),
        "120600": ("AV", "AS", "Army Aviation"),
        "121100": ("TC", "GD", "Infantry / Troop Concentration"),
        "121300": ("RE", "RC", "Reconnaissance"),
        "130100": ("AD", "AD", "Air Defense"),
        "130102": ("SA", "AD", "Air Defense Missile (SAM)"),
        "130300": ("FA", "FS", "Field Artillery"),
        "130700": ("ML", "AT", "Missile"),
        "140700": ("EN", "SP", "Engineer"),
        "150500": ("EW", "JM", "Electronic Warfare"),
    }

    # Kara Teçhizat (Symbol Set 15)
    LAND_EQUIPMENT_MAP = {
        "111000": ("ML", "AT", "Missile Launcher"),
        "111100": ("SA", "AD", "Air Defense Missile Launcher"),
        "120200": ("TK", "AT", "Tank"),
        "220300": ("RS", "SV", "Radar"),
    }

    # Yalnızca ters dönüşümde (Link 16 -> SIDC) kullanılan, 2525E'de ayrı
    # entity'si olmayan kodlar: (Platform, Activity) -> (set, entity, mod1, mod2, mesaj)
    REVERSE_ONLY = {
        ("LS", "RC"): ("01", "110111", "00", "00",
                       "Hava: Airborne Land Surveillance → 2525E'de karşılığı yok, Reconnaissance kullanıldı"),
        ("MP", "PT"): ("01", "110110", "00", "00",
                       "Hava: Maritime Patrol Aircraft → 2525E'de karşılığı yok, Patrol kullanıldı"),
    }

    # Hava entity'lerinde Mod1'in platform harflerini de belirlediği "genel" kodlar
    _AIR_GENERIC = frozenset({"110000", "110100", "000000"})

    # ------------------------------------------------------------------
    # SIDC -> Link 16
    # ------------------------------------------------------------------
    @classmethod
    def extract(cls, sidc: str) -> dict:
        """SIDC'den 5 karakterli teşhis kodu ve açıklamaları üretir.

        Aynı SIDC için sonuç önbellekten döner (GUI her değişimde çağırır).
        Dönen sözlük paylaşımlıdır; çağıran tarafından değiştirilmemelidir.
        """
        return cls._extract_cached((sidc or "").strip())

    @classmethod
    @lru_cache(maxsize=1024)
    def _extract_cached(cls, s: str) -> dict:
        if len(s) < 20:
            return {
                "code_5char": "-----",
                "breakdown": "Geçersiz SIDC",
                "details": "SIDC en az 20 hane olmalıdır.",
            }

        ctx = s[2]
        ident = s[3]
        symset = s[4:6]
        entity = s[10:16]
        mod1 = s[16:18]
        mod2 = s[18:20]

        c1, id_desc = cls._identity(ctx, ident)
        j_msg, plat_2c, act_2c, desc = cls._platform(symset, entity, mod1, mod2)

        code_5char = f"{c1}{plat_2c}{act_2c}"
        breakdown = f"[{c1}: Kimlik] + [{plat_2c}: Platform] + [{act_2c}: Görev/Activity]"
        details = (
            f"• 5516 Ed.9 Mesaj : {j_msg}\n"
            f"• Kimlik (1. Harf): {c1} — {id_desc}\n"
            f"• Platform (2-3)  : {plat_2c} (SIDC Entity: {entity})\n"
            f"• Görev/Act (4-5) : {act_2c} (SIDC Mod1: {mod1}, Mod2: {mod2})\n"
            f"• Taktik Açıklama : {desc}"
        )
        return {"code_5char": code_5char, "breakdown": breakdown, "details": details}

    @classmethod
    def _identity(cls, ctx: str, ident: str):
        c1, bits, id_desc = cls.ID_CHAR.get(ident, ("U", "001", "Unknown"))
        if ctx not in cls.EXERCISE_CONTEXTS:
            return c1, f"{id_desc} (EX=0, Bits={bits})"
        if ident == "6":
            return "K", f"FAKER (Tatbikat Düşmanı - EX=1, ID=6 [{bits}])"
        if ident == "5":
            return "J", f"JOKER (Tatbikat Şüphelisi - EX=1, ID=5 [{bits}])"
        return c1, f"Exercise {id_desc} (EX=1, Bits={bits})"

    @classmethod
    def _platform(cls, symset: str, entity: str, mod1: str, mod2: str):
        """(j_msg, platform, activity, açıklama) döndürür."""
        if symset == "01":
            j_msg = "J3.2 (Air Track) / J2.2 (Air PPLI)"
            plat, act, desc = cls._lookup(cls.AIR_ENTITY_MAP, entity) or (
                "NS", "NS", "No Statement (Tanımsız)")
            if mod1 in cls.AIR_MOD1_MAP:
                m_plat, act, m_desc = cls.AIR_MOD1_MAP[mod1]
                if entity in cls._AIR_GENERIC:
                    plat = m_plat
                    desc = f"{desc} -> {m_desc}"
                else:
                    desc = f"{desc} | Görev: {m_desc}"
            if mod2 in cls.AIR_MOD2_MAP:
                desc = f"{desc} ({cls.AIR_MOD2_MAP[mod2][1]})"
            return (j_msg, plat, act, desc)

        if symset == "02":
            return ("J3.2 (Air Track - Missile)", "MS", "AT", "Missile")

        if symset in ("05", "06"):
            return ("J3.6 (Space Track)", "SV", "OR", "Space Vehicle")

        if symset == "30":
            row = (cls._mod2_override(symset, entity, mod2)
                   or cls._lookup(cls.SURFACE_ENTITY_MAP, entity)
                   or ("SC", "NS", f"Surface Entity ({entity})"))
            return ("J3.3 (Surface Track) / J2.3 (Surface PPLI)", *row)

        if symset == "36":
            return ("J3.4 (Subsurface Track)", "MN", "MW", "Sea Mine")

        if symset == "35":
            row = (cls._mod2_override(symset, entity, mod2)
                   or cls._lookup(cls.SUBSURFACE_ENTITY_MAP, entity)
                   or ("SS", "NS", f"Subsurface Entity ({entity})"))
            return ("J3.4 (Subsurface Track)", *row)

        if symset in ("10", "11", "15", "20"):
            table = {"10": cls.LAND_UNIT_MAP, "15": cls.LAND_EQUIPMENT_MAP}.get(symset, {})
            row = cls._lookup(table, entity) or ("NS", "NS", f"Ground Entity ({entity})")
            return ("J3.5 (Land Track/Point) / J2.5 (Land PPLI)", *row)

        if symset == "25":
            return ("J3.0 (Reference Point)", "RP", "NS",
                    f"Reference Point / Control Measure ({entity})")

        return ("J3.x", "NS", "NS", "No Statement (Tanımsız)")

    # ------------------------------------------------------------------
    # Link 16 -> SIDC
    # ------------------------------------------------------------------
    @classmethod
    def _mod2_override(cls, symset: str, entity: str, mod2: str):
        table = cls.MOD2_OVERRIDES.get(symset, {}).get(mod2)
        return cls._lookup(table, entity) if table else None

    @classmethod
    @lru_cache(maxsize=None)
    def _reverse_index(cls) -> dict:
        """(platform, activity) -> (symbol_set, entity, mod1, mod2, mesaj).

        Tablolar bir kez taranır; ilk eşleşme önceliklidir
        (Hava Entity > Hava Mod1 > Suüstü > Sualtı > Kara Birlik > Kara Teçhizat
        > Mod2 özel durumları > sabit kodlar > yalnızca-ters kodlar).
        """
        idx = {}

        def add(key, value):
            idx.setdefault(key, value)

        for ent, (p, a, d) in cls.AIR_ENTITY_MAP.items():
            add((p, a), ("01", ent, "00", "00", f"Hava Entity: {d}"))
        for m, (p, a, d) in cls.AIR_MOD1_MAP.items():
            add((p, a), ("01", "110100", m, "00", f"Hava Modifier: {d}"))
        for ent, (p, a, d) in cls.SURFACE_ENTITY_MAP.items():
            add((p, a), ("30", ent, "00", "00", f"Suüstü: {d}"))
        for ent, (p, a, d) in cls.SUBSURFACE_ENTITY_MAP.items():
            add((p, a), ("35", ent, "00", "00", f"Sualtı: {d}"))
        for ent, (p, a, d) in cls.LAND_UNIT_MAP.items():
            add((p, a), ("10", ent, "00", "00", f"Kara Birlik: {d}"))
        for ent, (p, a, d) in cls.LAND_EQUIPMENT_MAP.items():
            add((p, a), ("15", ent, "00", "00", f"Kara Teçhizat: {d}"))
        for ss, by_mod2 in cls.MOD2_OVERRIDES.items():
            for m2, rows in by_mod2.items():
                for ent, (p, a, d) in rows.items():
                    add((p, a), (ss, ent, "00", m2, f"{'Suüstü' if ss == '30' else 'Sualtı'}: {d}"))
        add(("MS", "AT"), ("02", "110000", "00", "00", "Hava Füzesi"))
        add(("SV", "OR"), ("05", "110000", "00", "00", "Uzay Platformu"))
        add(("MN", "MW"), ("36", "110000", "00", "00", "Deniz Mayını"))
        for key, value in cls.REVERSE_ONLY.items():
            add(key, value)
        return idx

    @classmethod
    @lru_cache(maxsize=None)
    def _id_by_char(cls) -> dict:
        return {v[0]: k for k, v in cls.ID_CHAR.items()}

    @classmethod
    def reverse(cls, code_5char: str) -> dict:
        code = (code_5char or "").strip().upper()
        if len(code) != 5:
            return {
                "success": False,
                "suggested_sidc": "",
                "message": "Teşhis kodu tam 5 karakter olmalıdır (örn: FFTCP, FBMBM, KFTIN).",
            }

        c1, plat, act = code[0], code[1:3], code[3:5]

        if c1 == "K":
            ident, ctx = "6", "1"
        elif c1 == "J":
            ident, ctx = "5", "1"
        elif c1 in cls._id_by_char():
            ident, ctx = cls._id_by_char()[c1], "0"
        else:
            valid = ", ".join(list(cls._id_by_char()) + ["K", "J"])
            return {
                "success": False,
                "suggested_sidc": "",
                "message": f"Geçersiz kimlik harfi '{c1}'. Geçerli harfler: {valid}.",
            }

        hit = cls._reverse_index().get((plat, act))
        if hit:
            symbol_set, entity, mod1, mod2, msg = hit
        elif plat == "RP":
            symbol_set, entity, mod1, mod2 = "25", "110000", "00", "00"
            msg = "Referans Noktası / Control Measure"
        else:
            symbol_set, entity, mod1, mod2 = "01", "110100", "00", "00"
            msg = f"Eşleşme bulunamadı → varsayılan Hava Fixed Wing (Platform={plat}, Act={act})"

        suggested = f"13{ctx}{ident}{symbol_set}0000{entity}{mod1}{mod2}0000000000"

        return {
            "success": True,
            "suggested_sidc": suggested,
            "identity": ident,
            "context": ctx,
            "symbol_set": symbol_set,
            "entity": entity,
            "mod1": mod1,
            "mod2": mod2,
            "message": msg,
        }

    @staticmethod
    def _lookup(table: dict, entity: str):
        """Tam eşleşme yoksa sırasıyla subtype ve type seviyesine düşer."""
        for key in (entity, entity[:4] + "00", entity[:2] + "0000"):
            if key in table:
                return table[key]
        return None
