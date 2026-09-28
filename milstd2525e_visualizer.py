# -*- coding: utf-8 -*-
"""
MIL-STD-2525E Symbol Visualizer + STANAG 5516 Ed. 9 ID Extractor
----------------------------------------------------------------
Uses the user's original SIDC generator/decoder as the data source,
milsymbol-py for SVG rendering, and extracts STANAG 5516 Ed. 9 tactical IDs.

Files:
  milstd2525e_sidc.py        Original user code/data
  milstd2525e_visualizer.py  Visual browser + renderer + Link 16 ID extractor

Install (Linux):
  sudo apt install python3-tk libcairo2
  pip install milsymbol cairosvg Pillow

Run:
  python3 milstd2525e_visualizer.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from io import BytesIO
from pathlib import Path

from milstd2525e_sidc import MilStd2525EApp as BaseApp
from link16_ed9 import Link16Ed9Extractor

try:
    from milsymbol import Symbol
except Exception:
    Symbol = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = ImageTk = None

try:
    import cairosvg
except (ImportError, OSError, Exception):
    cairosvg = None


# =====================================================================
# 1. STANAG 5516 ED. 9 TEŞHİS ÇIKARIM MOTORU
# =====================================================================
class Link16Ed9Extractor:
    """
    30 haneli MIL-STD-2525E SIDC kodundan STANAG 5516 Edition 9
    5 karakterli teşhis kodunu ([1:Kimlik] + [2:Platform] + [2:Activity])
    ve DFI/DUI detaylarını çıkarır (Örn: FFTCP, FBMBM, KFTIN).
    """

    # 1. Karakter: Kimlik (DFI 279 / DUI 001 - 3 Bit)
    ID_CHAR = {
        "0": ("P", "000", "Pending (Beklemede)"),
        "1": ("U", "001", "Unknown (Bilinmeyen)"),
        "2": ("A", "010", "Assumed Friend (Muhtemel Dost)"),
        "3": ("F", "011", "Friend (Dost)"),
        "4": ("N", "100", "Neutral (Tarafsız)"),
        "5": ("S", "101", "Suspect (Şüpheli)"),
        "6": ("H", "110", "Hostile (Düşman)"),
    }

    # Hava (Symbol Set 01) Entity (Poz 11-16) -> (Platform 2-Harf, Varsayılan Activity 2-Harf, Açıklama)
    AIR_ENTITY_MAP = {
        "110000": ("FW", "NS", "Military Air (Askeri Hava Genel)"),
        "110100": ("FW", "NS", "Fixed Wing (Sabit Kanat)"),
        "110101": ("FT", "CP", "Fighter (Av/Önleme)"),
        "110102": ("FB", "AT", "Fighter / Bomber (Av-Bombardıman)"),
        "110103": ("BM", "BM", "Bomber (Bombardıman)"),
        "110104": ("CA", "AL", "Cargo / Airlift (Nakliye)"),
        "110105": ("JM", "JM", "Electronic Attack (ECM/Jammer)"),
        "110106": ("TK", "TK", "Tanker (Hava Yakıt İkmal)"),
        "110107": ("PT", "PT", "Patrol (Karakol)"),
        "110108": ("RS", "SR", "Rescue (Arama Kurtarma / SAR)"),
        "110109": ("RC", "RC", "Reconnaissance (Keşif / İGK)"),
        "110110": ("EW", "EW", "AEW / AWACS (Hava Erken İhbar)"),
        "110111": ("ES", "RC", "Electronic Surveillance (ESM)"),
        "110112": ("AS", "AW", "ASW / Carrier Based (Denizaltı Savunma)"),
        "110113": ("TR", "TR", "Trainer (Eğitim)"),
        "110114": ("UT", "UT", "Utility (Genel Maksat)"),
        "110115": ("CP", "CC", "Command Post (Havadan K2)"),
        "110116": ("MP", "PT", "Maritime Patrol (Deniz Karakol - MPA)"),
        "110123": ("AT", "AT", "Attack / Strike (Taarruz)"),
        "110200": ("HL", "NS", "Helicopter (Döner Kanat)"),
        "110300": ("UV", "RC", "UAV / RPV (İnsansız Hava Aracı)"),
        "110400": ("VS", "NS", "VSTOL (Dikine İniş/Kalkış)"),
        "120000": ("CV", "CA", "Civil Aircraft (Sivil Hava Aracı)"),
        "120100": ("CV", "PA", "Civil Fixed Wing (Ticari/Yolcu)"),
        "120200": ("CH", "CA", "Civil Helicopter (Sivil Helikopter)"),
        "130000": ("DC", "DC", "Decoy (Sahte Hedef / Aldatıcı)"),
    }

    # Hava Sector 1 Modifier (Poz 17-18) -> (Override Platform 2-Harf, Activity 2-Harf, Açıklama)
    AIR_MOD1_MAP = {
        "01": ("AT", "AT", "Attack / Strike (Taarruz)"),
        "02": ("BM", "BM", "Bomber (Bombardıman)"),
        "03": ("CA", "AL", "Cargo / Airlift (Nakliye)"),
        "04": ("FT", "CP", "Fighter / CAP (Muharebe Hava Devriyesi)"),
        "05": ("FT", "IN", "Interceptor (Önleme)"),
        "06": ("TK", "TK", "Tanker (Yakıt İkmal)"),
        "07": ("UT", "UT", "Utility (Genel Maksat)"),
        "08": ("VS", "NS", "VSTOL"),
        "09": ("CV", "PA", "Passenger (Yolcu Taşıma)"),
        "10": ("AS", "AW", "ASW (Denizaltı Savunma Harbi)"),
        "11": ("MC", "MC", "MCM (Mayın Karşı Tedbir)"),
        "12": ("CP", "CC", "Command & Control (Komuta Kontrol)"),
        "13": ("JM", "JM", "Jammer / ECM (Elektronik Taarruz)"),
        "14": ("ES", "EW", "Electronic Warfare (Elektronik Harp)"),
        "15": ("RC", "RC", "Reconnaissance (Keşif)"),
        "16": ("EW", "EW", "AEW / AWACS (Hava Erken İhbar)"),
        "17": ("AS", "SU", "ASUW (Suüstü Harbi)"),
        "18": ("FB", "AT", "Fighter / Bomber (Av-Bombardıman)"),
        "19": ("RS", "SR", "SAR (Arama Kurtarma)"),
        "20": ("RS", "CS", "CSAR (Muharebe Arama Kurtarma)"),
        "24": ("SF", "SF", "SOF (Özel Kuvvetler)"),
        "29": ("TR", "TR", "Trainer (Eğitim)"),
        "32": ("AT", "CS", "Close Air Support (Yakın Hava Desteği - CAS)"),
        "33": ("AT", "SD", "SEAD (Hava Savunma Baskılama)"),
    }

    # Hava Sector 2 Modifier (Poz 19-20) -> (Ek Görev / Nitelik 2-Harf, Açıklama)
    AIR_MOD2_MAP = {
        "01": ("HV", "Heavy (Ağır)"),
        "02": ("MD", "Medium (Orta)"),
        "03": ("LT", "Light (Hafif)"),
        "04": ("BO", "Boom-Only (Sadece Boom İkmal)"),
        "05": ("DR", "Drogue-Only (Sadece Sepet İkmal)"),
        "06": ("BD", "Boom and Drogue"),
        "07": ("CR", "Close Range (Yakın Menzil)"),
        "08": ("SR", "Short Range (Kısa Menzil)"),
        "09": ("MR", "Medium Range (Orta Menzil)"),
        "10": ("LR", "Long Range (Uzun Menzil)"),
    }

    # Deniz Suüstü (Symbol Set 30) Entity -> (Platform 2-Harf, Activity 2-Harf, Açıklama)
    SURFACE_ENTITY_MAP = {
        "110000": ("SC", "NS", "Military Combatant (Askeri Suüstü Genel)"),
        "120100": ("CV", "AC", "Carrier (Uçak Gemisi)"),
        "120200": ("SC", "SU", "Surface Combatant (Suüstü Muharip)"),
        "120201": ("BB", "SU", "Battleship (Zırhlı)"),
        "120202": ("CG", "SU", "Cruiser (Kruvazör)"),
        "120203": ("DD", "SU", "Destroyer (Muhrip)"),
        "120204": ("FF", "SU", "Frigate (Fırkateyn)"),
        "120205": ("FS", "PT", "Corvette (Korvet)"),
        "120206": ("LC", "PT", "Littoral Combatant Ship (Kıyı Muharebe Gemisi)"),
        "120300": ("AM", "AM", "Amphibious Warfare Ship (Amfibi Harp Gemisi)"),
        "120400": ("MW", "MC", "Mine Warfare Vessel (Mayın Harp Gemisi)"),
        "120500": ("PC", "PT", "Patrol Craft (Karakol Botu)"),
        "120700": ("HC", "PT", "Hovercraft / ACV"),
        "120800": ("TF", "CC", "Navy Task Force / Group (Görev Grubu)"),
        "130000": ("AX", "SP", "Non-Combatant / Auxiliary (Yardımcı Sınıf)"),
        "140000": ("MC", "MR", "Merchant Ship (Ticari Gemi)"),
        "140100": ("MC", "CG", "Cargo Ship (Yük Gemisi)"),
        "140200": ("PS", "PA", "Passenger Ship (Yolcu Gemisi)"),
        "140500": ("TG", "SP", "Tug (Römorkör)"),
        "140600": ("FE", "PA", "Ferry (Feribot)"),
        "140800": ("AO", "TK", "Tanker / Oiler (Akaryakıt Gemisi)"),
        "150100": ("FV", "FS", "Fishing Vessel (Balıkçı Gemisi)"),
    }

    # Sualtı (Symbol Set 35 & 36)
    SUBSURFACE_ENTITY_MAP = {
        "110000": ("SB", "NS", "Subsurface Military (Sualtı Genel)"),
        "110100": ("SS", "PT", "Submarine (Denizaltı)"),
        "110101": ("SN", "PT", "Nuclear Submarine (Nükleer Denizaltı - SSN/SSBN)"),
        "110102": ("SK", "PT", "Conventional Submarine (Klasik Denizaltı - SSK)"),
        "110200": ("SM", "NS", "Other Submersible (Diğer Sualtı Aracı)"),
        "110400": ("UV", "RC", "Autonomous Underwater Vehicle (İDA / UUV)"),
        "120000": ("DC", "DC", "Subsurface Decoy (Sualtı Aldatıcı)"),
        "130100": ("TP", "AT", "Torpedo (Torpido)"),
        "130200": ("MN", "MW", "Sea Mine (Deniz Mayını)"),
    }

    # Kara (Symbol Set 10, 11, 15, 20)
    LAND_ENTITY_MAP = {
        "110000": ("GR", "NS", "Land Unit (Kara Birliği Genel)"),
        "120500": ("AR", "AT", "Armor / Tank (Zırhlı / Tank)"),
        "120600": ("HL", "AS", "Army Aviation (Kara Havacılık)"),
        "121100": ("IN", "GD", "Infantry (Piyade)"),
        "121102": ("MI", "GD", "Mechanized Infantry (Mekanize Piyade)"),
        "130100": ("AD", "AD", "Air Defense (Hava Savunma)"),
        "130102": ("SM", "AD", "SAM System (Karadan Havaya Füze)"),
        "130300": ("FA", "FS", "Field Artillery (Sahra Topçusu)"),
        "130800": ("MS", "AT", "Surface-to-Surface Missile (Karadan Karaya Füze)"),
        "140100": ("EN", "SP", "Engineer (İstihkam)"),
        "140700": ("RC", "RC", "Reconnaissance (Keşif)"),
        "150500": ("EW", "JM", "Electronic Warfare (Elektronik Harp)"),
        "151000": ("RD", "SV", "Radar / Sensor (Radar / Gözetleme)"),
    }

    @classmethod
    def extract(cls, sidc: str) -> dict:
        s = (sidc or "").strip()
        if len(s) < 20:
            return {
                "code_5char": "-----",
                "breakdown": "Geçersiz SIDC",
                "details": "SIDC en az 20 hane olmalıdır."
            }

        ctx = s[2]          # Poz 3: Context (0=Real, 1=Exercise, 2=Sim)
        ident = s[3]        # Poz 4: Identity (0-6)
        symset = s[4:6]     # Poz 5-6: Symbol Set
        entity = s[10:16]   # Poz 11-16: Entity
        mod1 = s[16:18]     # Poz 17-18: Sector 1 Modifier
        mod2 = s[18:20]     # Poz 19-20: Sector 2 Modifier

        # --- 1. HARF: KİMLİK (IDENTITY + JOKER/FAKER) ---
        c1, bits, id_desc = cls.ID_CHAR.get(ident, ("U", "001", "Unknown"))
        if ctx == "1":  # Exercise (Tatbikat)
            if ident == "6":
                c1, id_desc = "K", f"FAKER (Tatbikat Düşmanı - EX=1, ID=6 [{bits}])"
            elif ident == "5":
                c1, id_desc = "J", f"JOKER (Tatbikat Şüphelisi - EX=1, ID=5 [{bits}])"
            else:
                id_desc = f"Exercise {id_desc} (EX=1, Bits={bits})"
        else:
            id_desc = f"{id_desc} (EX=0, Bits={bits})"

        # --- 2-3. HARF (PLATFORM) & 4-5. HARF (ACTIVITY) ---
        plat_2c, act_2c, desc = "NS", "NS", "No Statement (Tanımsız)"
        j_msg = "J3.x"

        if symset == "01":  # HAVA (AIR)
            j_msg = "J3.2 (Air Track) / J2.2 (Air PPLI)"
            row = cls._lookup(cls.AIR_ENTITY_MAP, entity)
            if row:
                plat_2c, act_2c, desc = row

            # Sector 1 Modifier (Poz 17-18) varsa Activity ve genel Platformu ez:
            if mod1 in cls.AIR_MOD1_MAP:
                m_plat, m_act, m_desc = cls.AIR_MOD1_MAP[mod1]
                act_2c = m_act
                if entity in ("110000", "110100", "000000"):
                    plat_2c = m_plat
                    desc = f"{desc} -> {m_desc}"
                else:
                    desc = f"{desc} | Görev: {m_desc}"

            if mod2 in cls.AIR_MOD2_MAP:
                _, m2_desc = cls.AIR_MOD2_MAP[mod2]
                desc = f"{desc} ({m2_desc})"

        elif symset == "02":  # HAVA FÜZESİ (AIR MISSILE)
            j_msg = "J3.2 (Air Track - Missile)"
            plat_2c, act_2c, desc = "MS", "AT", "Air Missile (Hava Füzesi)"

        elif symset in ("05", "06"):  # UZAY (SPACE)
            j_msg = "J3.6 (Space Track)"
            plat_2c, act_2c, desc = "SV", "OR", "Space Vehicle (Uzay Platformu)"

        elif symset == "30":  # SUÜSTÜ (SEA SURFACE)
            j_msg = "J3.3 (Surface Track) / J2.3 (Surface PPLI)"
            row = cls._lookup(cls.SURFACE_ENTITY_MAP, entity)
            if row:
                plat_2c, act_2c, desc = row
            else:
                plat_2c, act_2c, desc = "SC", "NS", f"Surface Entity ({entity})"

        elif symset in ("35", "36"):  # SUALTI (SUBSURFACE)
            j_msg = "J3.4 (Subsurface Track)"
            if symset == "36":
                plat_2c, act_2c, desc = "MN", "MW", "Sea Mine (Deniz Mayını)"
            else:
                row = cls._lookup(cls.SUBSURFACE_ENTITY_MAP, entity)
                if row:
                    plat_2c, act_2c, desc = row
                else:
                    plat_2c, act_2c, desc = "SS", "NS", f"Subsurface Entity ({entity})"

        elif symset in ("10", "11", "15", "20"):  # KARA (LAND)
            j_msg = "J3.5 (Land Track/Point) / J2.5 (Land PPLI)"
            row = cls._lookup(cls.LAND_ENTITY_MAP, entity)
            if row:
                plat_2c, act_2c, desc = row
            else:
                plat_2c, act_2c, desc = "GR", "NS", f"Ground Entity ({entity})"

        elif symset == "25":  # KONTROL NOKTASI (CONTROL MEASURE)
            j_msg = "J3.0 (Reference Point)"
            plat_2c, act_2c, desc = "RP", "NS", f"Reference Point / Control Measure ({entity})"

        code_5char = f"{c1}{plat_2c}{act_2c}"
        breakdown = f"[{c1}: Kimlik] + [{plat_2c}: Platform] + [{act_2c}: Görev/Activity]"
        details = (
            f"• 5516 Ed.9 Mesaj : {j_msg}\n"
            f"• Kimlik (1. Harf): {c1} — {id_desc}\n"
            f"• Platform (2-3)  : {plat_2c} (SIDC Entity: {entity})\n"
            f"• Görev/Act (4-5) : {act_2c} (SIDC Mod1: {mod1}, Mod2: {mod2})\n"
            f"• Taktik Açıklama : {desc}"
        )

        return {
            "code_5char": code_5char,
            "breakdown": breakdown,
            "details": details,
        }

    @staticmethod
    def _lookup(table: dict, entity: str):
        if entity in table:
            return table[entity]
        if entity[:4] + "00" in table:
            return table[entity[:4] + "00"]
        if entity[:2] + "0000" in table:
            return table[entity[:2] + "0000"]
        return None


# =====================================================================
# 2. GÖRSELLEŞTİRİCİ ARAYÜZ SINIFI
# =====================================================================
class MilStd2525EVisualizer(BaseApp):
    """Visual browser built on top of the supplied SIDC generator."""

    def __init__(self, root):
        self.symbol_photo = None
        self.render_after_id = None
        self._last_svg = None
        self._last_used_sidc = ""
        super().__init__(root)
        self.root.minsize(1150, 840)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.render_after_id is not None:
            try:
                self.root.after_cancel(self.render_after_id)
            except Exception:
                pass
        self.root.destroy()

    def build_ui(self):
        self.root.title("MIL-STD-2525E Sembol Görselleştirici & STANAG 5516 Ed.9 Teşhis")
        self.root.geometry("1300x920")

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ---------------- SOL PANEL: SIDC KONTROLLERİ ----------------
        left = ttk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fa = ttk.LabelFrame(left, text="SET A — Pozisyon 1–10", padding=7)
        fa.pack(fill=tk.X, pady=3)

        self.cb_ver = self.mk_cb(
            fa, "Poz 1-2 (Version):",
            self.versions, "13 - MIL-STD-2525E", 0
        )
        self.cb_ctx = self.mk_cb(
            fa, "Poz 3 (Context):",
            self.contexts, "0 - Reality", 1
        )
        self.cb_id = self.mk_cb(
            fa, "Poz 4 (Identity):",
            self.identities, "3 - Friend", 2
        )
        self.cb_ss = self.mk_cb(
            fa, "Poz 5-6 (Symbol Set):",
            self.symbol_sets, "01 - Air", 3
        )
        self.cb_ss.bind(
            "<<ComboboxSelected>>",
            lambda e: self.on_symset_change()
        )
        self.cb_st = self.mk_cb(
            fa, "Poz 7 (Status):",
            self.statuses, "0 - Present", 4
        )
        self.cb_hq = self.mk_cb(
            fa, "Poz 8 (HQ/TF/Dummy):",
            self.hq_tf, "0 - Unknown (No Statement)", 5
        )
        self.cb_amp = self.mk_cb(
            fa, "Poz 9-10 (Amplifier):",
            self.amplifiers, "00 - Unknown (No Statement)", 6
        )

        fb = ttk.LabelFrame(
            left,
            text="SET B — Pozisyon 11–20 & Set/Common Modifiers",
            padding=7
        )
        fb.pack(fill=tk.X, pady=3)

        ttk.Label(fb, text="Entity Arama:", width=34).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.ent_q = ttk.Entry(fb, width=42)
        self.ent_q.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_q.bind("<KeyRelease>", self.filter_ent)

        self.cb_ent = self.mk_cb(
            fb, "Poz 11-16 (Entity/Type/Subtype):", {}, "", 1
        )
        self.cb_s1 = self.mk_cb(
            fb, "Poz 17-18 (Set Sector 1 Mod):", {}, "", 2
        )
        self.cb_s2 = self.mk_cb(
            fb, "Poz 19-20 (Set Sector 2 Mod):", {}, "", 3
        )
        self.cb_c1 = self.mk_cb(
            fb, "Tablo A-IX (Common Sector 1):",
            self.common_s1,
            "000 - Yok (Set Özel Mod. Kullan)", 4
        )
        self.cb_c2 = self.mk_cb(
            fb, "Tablo A-X (Common Sector 2):",
            self.common_s2,
            "000 - Yok (Set Özel Mod. Kullan)", 5
        )

        fc = ttk.LabelFrame(left, text="SET C — Pozisyon 21–30", padding=7)
        fc.pack(fill=tk.X, pady=3)

        ttk.Label(
            fc, text="Poz 21-22 (Common Mod ID 1 & 2):", width=34
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_cid = ttk.Label(
            fc, text="00", font=("DejaVu Sans Mono", 10, "bold")
        )
        self.lbl_cid.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        self.cb_frm = self.mk_cb(
            fc, "Poz 23 (Frame Shape - A-LX):",
            self.frames, "0 - Unknown", 1
        )

        ttk.Label(fc, text="Poz 24-27 (Reserved):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Label(fc, text="0000 (Sabit)").grid(
            row=2, column=1, sticky=tk.W, padx=10, pady=2
        )

        ttk.Label(fc, text="Poz 28-30 (Country Code):").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        self.ent_cnt = ttk.Entry(fc, width=12)
        self.ent_cnt.insert(0, "000")
        self.ent_cnt.grid(row=3, column=1, sticky=tk.W, padx=10, pady=2)
        self.ent_cnt.bind("<KeyRelease>", lambda e: self.update_sidc())

        # SIDC / Decoder
        fo = ttk.LabelFrame(left, text="SIDC — 30 Hane", padding=8)
        fo.pack(fill=tk.X, pady=5)

        self.sidc_var = tk.StringVar()
        ttk.Entry(
            fo, textvariable=self.sidc_var,
            font=("DejaVu Sans Mono", 14, "bold"),
            justify="center", state="readonly"
        ).pack(fill=tk.X, pady=3)

        self.brk_var = tk.StringVar()
        ttk.Label(
            fo, textvariable=self.brk_var,
            font=("DejaVu Sans Mono", 9)
        ).pack(pady=2)

        row = ttk.Frame(fo)
        row.pack(fill=tk.X, pady=4)

        ttk.Button(
            row, text="Panoya Kopyala", command=self.copy_sidc
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            row, text="SVG Kaydet", command=self.save_svg
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            row, text="PNG Kaydet", command=self.save_png
        ).pack(side=tk.LEFT, padx=3)

        ttk.Label(row, text="  SIDC Çözümle:").pack(side=tk.LEFT)
        self.ent_dec = ttk.Entry(row, width=32, font=("DejaVu Sans Mono", 10))
        self.ent_dec.insert(0, "130310000012000000000200000000")
        self.ent_dec.pack(side=tk.LEFT, padx=4)
        ttk.Button(
            row, text="Çözümle", command=self.decode_sidc
        ).pack(side=tk.LEFT, padx=3)

        # Hızlı Sembol Tarama Listesi
        quick = ttk.LabelFrame(left, text="Hızlı Sembol Tarama", padding=7)
        quick.pack(fill=tk.BOTH, expand=True, pady=3)

        ttk.Label(
            quick,
            text="Aşağıdaki listeden Entity seçerek doğrudan görselleştirebilirsin."
        ).pack(anchor=tk.W)

        list_frame = ttk.Frame(quick)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.entity_list = tk.Listbox(
            list_frame, height=8, exportselection=False
        )
        scroll = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL,
            command=self.entity_list.yview
        )
        self.entity_list.configure(yscrollcommand=scroll.set)
        self.entity_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_list.bind("<<ListboxSelect>>", self.on_entity_list_select)

        # ---------------- SAĞ PANEL: SEMBOL ÖNİZLEME & LINK 16 ID ----------------
        right = ttk.LabelFrame(main, text="2525E SEMBOL ÖNİZLEME", padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.preview_canvas = tk.Canvas(
            right, bg="#f4f4f4",
            highlightthickness=1,
            highlightbackground="#b0b0b0"
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        l16_box = ttk.LabelFrame(right, text="STANAG 5516 Ed.9 Teşhis Kodu", padding=6)
        l16_box.pack(fill=tk.X, pady=(8, 4))

        self.l16_code_var = tk.StringVar(value="-----")
        ttk.Label(
            l16_box, textvariable=self.l16_code_var,
            font=("DejaVu Sans Mono", 16, "bold"), foreground="#0055aa"
        ).pack(anchor=tk.W)

        self.l16_info_var = tk.StringVar()
        ttk.Label(
            l16_box, textvariable=self.l16_info_var,
            font=("DejaVu Sans Mono", 9), justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(2, 0))
        self.preview_canvas.bind("<Configure>", self._on_canvas_resize)

        # STANAG 5516 ED.9 TEŞHİS GÖSTERGE PANELİ
        l16_frame = ttk.LabelFrame(
            right, text="STANAG 5516 Ed.9 — Link 16 Teşhis Çıktısı", padding=8
        )
        l16_frame.pack(fill=tk.X, pady=(8, 4))

        top_l16 = ttk.Frame(l16_frame)
        top_l16.pack(fill=tk.X)

        ttk.Label(
            top_l16, text="Link 16 Teşhis Kodu:",
            font=("TkDefaultFont", 10, "bold")
        ).pack(side=tk.LEFT)

        self.l16_code_var = tk.StringVar(value="-----")
        ttk.Label(
            top_l16, textvariable=self.l16_code_var,
            font=("DejaVu Sans Mono", 16, "bold"),
            foreground="#0055aa"
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            top_l16, text="Kodu Kopyala",
            command=self.copy_l16_code
        ).pack(side=tk.RIGHT)

        self.l16_brk_var = tk.StringVar()
        ttk.Label(
            l16_frame, textvariable=self.l16_brk_var,
            font=("DejaVu Sans Mono", 9, "bold")
        ).pack(anchor=tk.W, pady=(2, 4))

        self.l16_det_var = tk.StringVar()
        ttk.Label(
            l16_frame, textvariable=self.l16_det_var,
            font=("DejaVu Sans Mono", 9),
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # Sembol Render Durumu
        info = ttk.Frame(right)
        info.pack(fill=tk.X, pady=(6, 0))

        self.render_status = tk.StringVar(value="Sembol oluşturuluyor...")
        ttk.Label(
            info, textvariable=self.render_status,
            font=("TkDefaultFont", 9, "bold")
        ).pack(anchor=tk.W)

        self.meta_var = tk.StringVar()
        ttk.Label(
            info, textvariable=self.meta_var,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(3, 0))

    def copy_l16_code(self):
        code = self.l16_code_var.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("Kopyalandı", f"Link 16 Teşhis Kodu kopyalandı: {code}")

    def _on_canvas_resize(self, event):
        if self.preview_canvas.find_withtag("center_item"):
            self.preview_canvas.coords(
                "center_item", event.width // 2, event.height // 2
            )

    def _fill_entity_list(self):
        if not hasattr(self, "entity_list"):
            return
        self.entity_list.delete(0, tk.END)
        for key in self.cur_e.keys():
            self.entity_list.insert(tk.END, key)

    def on_symset_change(self, init_mode=False):
        super().on_symset_change(init_mode=init_mode)
        self._fill_entity_list()

    def filter_ent(self, event=None):
        super().filter_ent(event)
        self._fill_entity_list()
        q = self.ent_q.get().strip().lower()
        if q:
            for i, item in enumerate(self.entity_list.get(0, tk.END)):
                if q in item.lower():
                    self.entity_list.selection_clear(0, tk.END)
                    self.entity_list.selection_set(i)
                    self.entity_list.see(i)
                    break

    def on_entity_list_select(self, event=None):
        sel = self.entity_list.curselection()
        if not sel:
            return
        key = self.entity_list.get(sel[0])
        self.cb_ent.set(key)
        self.update_sidc()

    def update_sidc(self):
        super().update_sidc()
        if self.render_after_id is not None:
            try:
                self.root.after_cancel(self.render_after_id)
            except Exception:
                pass
        self.render_after_id = self.root.after(80, self.render_symbol)

    def _extract_svg_from_symbol(self, sym):
        if hasattr(sym, "as_svg"):
            return sym.as_svg()
        if hasattr(sym, "asSVG"):
            return sym.asSVG()
        raise RuntimeError("milsymbol Symbol nesnesinde SVG metodu bulunamadı.")

    def _get_svg(self):
        if Symbol is None:
            raise RuntimeError(
                "milsymbol bulunamadı. Paketleri kurun:\n"
                "pip install -r requirements.txt"
            )

        raw_sidc = self.sidc_var.get().strip()
        candidates = [raw_sidc]

        if len(raw_sidc) >= 20:
            candidates.append(raw_sidc[:20])
            candidates.append("10" + raw_sidc[2:20])

        last_err = None
        for candidate in candidates:
            try:
                sym = Symbol(candidate, size=180)
                if hasattr(sym, "is_valid") and not sym.is_valid():
                    continue
                svg = self._extract_svg_from_symbol(sym)
                if svg and "<svg" in svg:
                    self._last_used_sidc = candidate
                    return svg
            except Exception as exc:
                last_err = exc

        try:
            sym = Symbol(candidates[-1], size=180)
            self._last_used_sidc = candidates[-1]
            return self._extract_svg_from_symbol(sym)
        except Exception as exc:
            raise ValueError(
                f"Bu SIDC için sembol üretilemedi ({last_err or exc})."
            )

    def render_symbol(self):
        self.render_after_id = None
        if not hasattr(self, "preview_canvas"):
            return

        full_sidc = self.sidc_var.get().strip()

        # HER SIDC DEĞİŞİMİNDE LINK 16 KODUNU HESAPLA VE GÖSTER
        if hasattr(self, "l16_code_var"):
            l16_res = Link16Ed9Extractor.extract(full_sidc)
            self.l16_code_var.set(l16_res["code_5char"])
            self.l16_brk_var.set(l16_res["breakdown"])
            self.l16_det_var.set(l16_res["details"])

        w = max(self.preview_canvas.winfo_width(), 500)
        h = max(self.preview_canvas.winfo_height(), 420)


        try:
            svg = self._get_svg()
            self._last_svg = svg

            if cairosvg is None or Image is None or ImageTk is None:
                self.render_status.set(
                    "SVG üretildi. Görsel önizleme için cairosvg + pillow kurulmalı."
                )
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(
                    w // 2, h // 2,
                    text="SVG hazır (Önizleme için cairosvg + Pillow gerekli)\n\n"
                         "pip install cairosvg Pillow",
                    justify=tk.CENTER,
                    font=("TkDefaultFont", 12),
                    tags="center_item"
                )
                return

            png = cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                output_width=450,
                output_height=450
            )
            image = Image.open(BytesIO(png)).convert("RGBA")
            self.symbol_photo = ImageTk.PhotoImage(image)

            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                w // 2, h // 2,
                image=self.symbol_photo,
                anchor=tk.CENTER,
                tags="center_item"
            )

            mode_note = (
                "2525E (30 Hane)"
                if self._last_used_sidc == full_sidc
                else f"2525D Uyumluluk ({self._last_used_sidc})"
            )
            self.render_status.set(
                f"Renderer: milsymbol [{mode_note}]"
            )
            self.meta_var.set(
                f"Symbol Set: {self.cb_ss.get()}  |  Entity: {self.cb_ent.get()}"
            )

        except Exception as exc:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                w // 2, h // 2,
                text=f"Sembol render edilemedi.\n\n{exc}",
                justify=tk.CENTER,
                font=("TkDefaultFont", 11),
                tags="center_item"
            )
            self.render_status.set("Render hatası (Link 16 teşhisi yukarıda hesaplandı)")
            self.meta_var.set("")

    def save_svg(self):
        try:
            svg = self._get_svg()
        except Exception as exc:
            messagebox.showerror("SVG Hatası", str(exc))
            return

        path = filedialog.asksaveasfilename(
            title="2525E SVG Kaydet",
            defaultextension=".svg",
            initialfile=f"{self.sidc_var.get().strip()}_{self.l16_code_var.get()}.svg",
            filetypes=[("SVG", "*.svg"), ("All files", "*.*")]
        )
        if not path:
            return

        Path(path).write_text(svg, encoding="utf-8")
        messagebox.showinfo("Kaydedildi", f"SVG dosyası kaydedildi:\n{path}")

    def save_png(self):
        if cairosvg is None:
            messagebox.showerror(
                "Eksik paket",
                "PNG dışa aktarmak için cairosvg gerekli.\n\n"
                "pip install cairosvg"
            )
            return

        try:
            svg = self._get_svg()
            path = filedialog.asksaveasfilename(
                title="2525E PNG Kaydet",
                defaultextension=".png",
                initialfile=f"{self.sidc_var.get().strip()}_{self.l16_code_var.get()}.png",
                filetypes=[("PNG", "*.png"), ("All files", "*.*")]
            )
            if not path:
                return

            cairosvg.svg2png(
                bytestring=svg.encode("utf-8"),
                write_to=path,
                output_width=1000,
                output_height=1000
            )
            messagebox.showinfo(
                "Kaydedildi", f"PNG dosyası kaydedildi:\n{path}"
            )
        except Exception as exc:
            messagebox.showerror("PNG Hatası", str(exc))


def main():
    root = tk.Tk()

    if Symbol is None:
        root.after(
            300,
            lambda: messagebox.showwarning(
                "milsymbol eksik",
                "2525E sembollerini çizmek için önce:\n\n"
                "pip install -r requirements.txt\n\n"
                "komutunu çalıştır."
            )
        )

    MilStd2525EVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()