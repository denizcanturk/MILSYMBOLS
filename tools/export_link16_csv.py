# -*- coding: utf-8 -*-
"""
Link 16 teşhis kodu <-> MIL-STD-2525E SIDC eşleme tablosunu CSV olarak dışa aktarır.

Veri kaynağı uygulamanın kendi tablolarıdır (link16_ed9.py + milstd2525e_sidc.py),
bu yüzden tablolar değiştiğinde bu betiği yeniden çalıştırmak yeterlidir:

    python3 tools/export_link16_csv.py            # proje köküne yazar
    python3 tools/export_link16_csv.py çıktı_klasörü

Üretilen dosyalar:
    link16_sidc_eslesme.csv          Platform/Activity <-> Symbol Set/Entity/Mod1/Mod2
    link16_kimlik.csv                1. harf (kimlik) <-> SIDC Context/Identity
    link16_sidc_tum_kimlikler.csv    İkisinin birleşimi: her eşleme × her kimlik,
                                     hazır 5 harfli teşhis kodu ve hazır 30 haneli SIDC
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from link16_ed9 import Link16Ed9Extractor as L  # noqa: E402
from milstd2525e_sidc import MilStd2525EApp  # noqa: E402

ENV_BY_SET = {
    "01": "Air", "02": "Air", "05": "Space", "06": "Space",
    "10": "Gnd", "11": "Gnd", "15": "Gnd", "20": "Gnd",
    "30": "Surf", "35": "Subsurf", "36": "Subsurf", "25": "Reference",
}
ENV_ORDER = ["Air", "Surf", "Subsurf", "Gnd", "Space", "Reference"]

COLUMNS = [
    "Ortam", "Link16_Platform", "Link16_Activity", "Ornek_Teshis_Dost",
    "Symbol_Set", "Symbol_Set_Adi", "Entity", "Entity_Adi",
    "Mod1", "Mod1_Adi", "Mod2", "Mod2_Adi",
    "Ornek_SIDC_Dost", "Link16_Mesaj", "Yon", "Aciklama",
]


def _menu():
    app = MilStd2525EApp.__new__(MilStd2525EApp)
    app.init_data()
    return app


def _name(table, code):
    """Menü tablosunda koda karşılık gelen adı ('110104 - X' -> 'X') döndürür."""
    for label, value in table.items():
        if value == code:
            return label.split(" - ", 1)[1] if " - " in label else label
    return ""


def _sidc(ss, ent, m1, m2, ctx="0", ident="3"):
    return f"13{ctx}{ident}{ss}0000{ent}{m1}{m2}0000000000"


def collect_rows():
    app = _menu()
    rev = L._reverse_index()
    rows = []

    def add(ss, ent, m1, m2, plat, act, desc, direction=None):
        db = app.db.get(ss, app.db["00"])
        sidc = _sidc(ss, ent, m1, m2)
        if direction is None:
            hit = rev.get((plat, act))
            direction = ("İki yönlü" if hit and hit[:4] == (ss, ent, m1, m2)
                         else "Yalnızca SIDC → Link16")
        rows.append({
            "Ortam": ENV_BY_SET.get(ss, "?"),
            "Link16_Platform": plat,
            "Link16_Activity": act,
            "Ornek_Teshis_Dost": f"F{plat}{act}",
            "Symbol_Set": ss,
            "Symbol_Set_Adi": _name(app.symbol_sets, ss),
            "Entity": ent,
            "Entity_Adi": _name(db["e"], ent),
            "Mod1": m1,
            "Mod1_Adi": _name(db["s1"], m1),
            "Mod2": m2,
            "Mod2_Adi": _name(db["s2"], m2),
            "Ornek_SIDC_Dost": sidc,
            "Link16_Mesaj": L._platform(ss, ent, m1, m2)[0],
            "Yon": direction,
            "Aciklama": desc,
        })

    for ent, (p, a, d) in L.AIR_ENTITY_MAP.items():
        add("01", ent, "00", "00", p, a, d)
    for m1, (p, a, d) in L.AIR_MOD1_MAP.items():
        add("01", "110100", m1, "00", p, a, f"Fixed Wing + Sector 1: {d}")
    add("02", "110000", "00", "00", "MS", "AT", "Missile")
    for ent, (p, a, d) in L.SURFACE_ENTITY_MAP.items():
        add("30", ent, "00", "00", p, a, d)
    for ent, (p, a, d) in L.SUBSURFACE_ENTITY_MAP.items():
        add("35", ent, "00", "00", p, a, d)
    for ss, by_mod2 in L.MOD2_OVERRIDES.items():
        for m2, entries in by_mod2.items():
            for ent, (p, a, d) in entries.items():
                add(ss, ent, "00", m2, p, a, f"{d} (Sector 2 modifier ile)")
    add("36", "110000", "00", "00", "MN", "MW", "Sea Mine (Set 36'daki tüm entity'ler)")
    for ent, (p, a, d) in L.LAND_UNIT_MAP.items():
        add("10", ent, "00", "00", p, a, d)
    for ent, (p, a, d) in L.LAND_EQUIPMENT_MAP.items():
        add("15", ent, "00", "00", p, a, d)
    add("05", "110000", "00", "00", "SV", "OR", "Space Vehicle (Set 05/06'daki tüm entity'ler)")
    add("25", "110000", "00", "00", "RP", "NS",
        "Reference Point / Control Measure (Link16→SIDC: Platform=RP, Activity herhangi)",
        direction="İki yönlü")
    for (p, a), (ss, ent, m1, m2, msg) in L.REVERSE_ONLY.items():
        add(ss, ent, m1, m2, p, a, msg.split(": ", 1)[-1], direction="Yalnızca Link16 → SIDC")

    rows.sort(key=lambda r: ENV_ORDER.index(r["Ortam"]))  # sort kararlıdır: tablo sırası korunur
    return rows


def identity_rows():
    app = _menu()
    rows = []
    for ident, (c1, bits, desc) in L.ID_CHAR.items():
        rows.append({"Link16_Kimlik_Harfi": c1, "SIDC_Context": "0 (Reality)",
                     "SIDC_Identity": f"{ident} - {_name(app.identities, ident)}",
                     "Bitler": bits, "Aciklama": desc})
    exercise = ", ".join(sorted(L.EXERCISE_CONTEXTS))
    rows.append({"Link16_Kimlik_Harfi": "K", "SIDC_Context": f"{exercise} (Exercise)",
                 "SIDC_Identity": "6 - Hostile/Faker", "Bitler": "110",
                 "Aciklama": "FAKER (Tatbikat düşmanı)"})
    rows.append({"Link16_Kimlik_Harfi": "J", "SIDC_Context": f"{exercise} (Exercise)",
                 "SIDC_Identity": "5 - Suspect/Joker", "Bitler": "101",
                 "Aciklama": "JOKER (Tatbikat şüphelisi)"})
    return rows


# Genişletilmiş tablo için kimlikler: (harf, SIDC context, SIDC identity, ad)
IDENTITIES = [
    ("P", "0", "0", "Pending"),
    ("U", "0", "1", "Unknown"),
    ("A", "0", "2", "Assumed Friend"),
    ("F", "0", "3", "Friend"),
    ("N", "0", "4", "Neutral"),
    ("S", "0", "5", "Suspect"),
    ("H", "0", "6", "Hostile"),
    ("K", "1", "6", "Faker (Tatbikat Düşmanı)"),
    ("J", "1", "5", "Joker (Tatbikat Şüphelisi)"),
]

EXPANDED_COLUMNS = [
    "Ortam", "Kimlik_Harfi", "Kimlik", "Teshis_Kodu", "SIDC",
    "SIDC_Context", "SIDC_Identity",
    "Link16_Platform", "Link16_Activity",
    "Symbol_Set", "Symbol_Set_Adi", "Entity", "Entity_Adi",
    "Mod1", "Mod1_Adi", "Mod2", "Mod2_Adi",
    "Link16_Mesaj", "Yon", "Aciklama",
]


def expanded_rows(rows=None):
    """Her eşleme satırını 9 kimlikle çoğaltır (sıra: eşleme, sonra kimlik)."""
    out = []
    for r in rows or collect_rows():
        for c1, ctx, ident, id_name in IDENTITIES:
            e = {k: r[k] for k in EXPANDED_COLUMNS if k in r}
            e.update({
                "Kimlik_Harfi": c1,
                "Kimlik": id_name,
                "Teshis_Kodu": f"{c1}{r['Link16_Platform']}{r['Link16_Activity']}",
                "SIDC": _sidc(r["Symbol_Set"], r["Entity"], r["Mod1"], r["Mod2"], ctx, ident),
                "SIDC_Context": ctx,
                "SIDC_Identity": ident,
            })
            out.append({k: e[k] for k in EXPANDED_COLUMNS})
    return out


def write_csv(path, rows):
    # utf-8-sig: Türkçe karakterlerin Excel'de doğru görünmesi için BOM ekler
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    out.mkdir(parents=True, exist_ok=True)
    rows = collect_rows()
    write_csv(out / "link16_sidc_eslesme.csv", rows)
    write_csv(out / "link16_kimlik.csv", identity_rows())
    expanded = expanded_rows(rows)
    write_csv(out / "link16_sidc_tum_kimlikler.csv", expanded)
    print(f"{len(rows)} eşleme satırı      -> {out / 'link16_sidc_eslesme.csv'}")
    print(f"Kimlik tablosu             -> {out / 'link16_kimlik.csv'}")
    print(f"{len(expanded)} satır (tüm kimlikler) -> {out / 'link16_sidc_tum_kimlikler.csv'}")


if __name__ == "__main__":
    main()
