# -*- coding: utf-8 -*-
"""Link16Ed9Extractor birim testleri:  python3 -m unittest discover -s tests"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from link16_ed9 import Link16Ed9Extractor as L  # noqa: E402
from milstd2525e_sidc import MilStd2525EApp  # noqa: E402


def sidc(ctx="0", ident="3", ss="01", entity="110000", m1="00", m2="00"):
    return f"13{ctx}{ident}{ss}0000{entity}{m1}{m2}0000000000"


def code(*args, **kw):
    return L.extract(sidc(*args, **kw))["code_5char"]


def sidc_menu_tables():
    """milstd2525e_sidc.py menü tablolarını GUI açmadan yükler."""
    app = MilStd2525EApp.__new__(MilStd2525EApp)
    app.init_data()
    return app.db


class ConsistencyTests(unittest.TestCase):
    """Link 16 tablolarındaki her kod SIDC menü tablosunda bulunmalı."""

    def test_all_link16_codes_exist_in_sidc_table(self):
        db = sidc_menu_tables()
        checks = [
            ("01", "e", L.AIR_ENTITY_MAP), ("01", "s1", L.AIR_MOD1_MAP), ("01", "s2", L.AIR_MOD2_MAP),
            ("30", "e", L.SURFACE_ENTITY_MAP), ("35", "e", L.SUBSURFACE_ENTITY_MAP),
            ("10", "e", L.LAND_UNIT_MAP), ("15", "e", L.LAND_EQUIPMENT_MAP),
        ]
        for ss, kind, table in checks:
            known = set(db[ss][kind].values())
            for key in table:
                with self.subTest(symbol_set=ss, table=kind, code=key):
                    self.assertIn(key, known)
        for ss, by_mod2 in L.MOD2_OVERRIDES.items():
            for m2, rows in by_mod2.items():
                with self.subTest(symbol_set=ss, mod2=m2):
                    self.assertIn(m2, set(db[ss]["s2"].values()))
                    for ent in rows:
                        self.assertIn(ent, set(db[ss]["e"].values()))

    def test_every_reverse_sidc_is_fully_in_sidc_table(self):
        db = sidc_menu_tables()
        for (plat, act), (ss, ent, m1, m2, _) in L._reverse_index().items():
            with self.subTest(code=plat + act):
                self.assertIn(ent, set(db[ss]["e"].values()))
                self.assertIn(m1, set(db[ss]["s1"].values()))
                self.assertIn(m2, set(db[ss]["s2"].values()))


class ExtractTests(unittest.TestCase):
    def test_air_entities_follow_2525e_numbering(self):
        self.assertEqual(code(entity="110104"), "FFTCP")   # Fighter
        self.assertEqual(code(entity="110109"), "FTKTK")   # Tanker
        self.assertEqual(code(entity="110116"), "FAEAE")   # AEW
        self.assertEqual(code(entity="110102"), "FATAT")   # Attack/Strike
        self.assertEqual(code(entity="110101"), "FFWNS")   # MEDEVAC -> Fixed Wing'e düşer

    def test_air_generic_with_mod1_takes_platform_from_modifier(self):
        self.assertEqual(code(entity="110100", m1="02"), "FBMBM")
        self.assertEqual(code(entity="110100", m1="16"), "FEWEW")

    def test_air_specific_entity_keeps_platform_but_takes_activity(self):
        res = L.extract(sidc(entity="110103", m1="04"))
        self.assertEqual(res["code_5char"], "FBMCP")
        self.assertIn("Görev: Fighter / CAP", res["details"])

    def test_mod2_appends_description(self):
        self.assertIn("(Heavy)", L.extract(sidc(entity="110103", m2="01"))["details"])

    def test_faker_and_joker(self):
        self.assertEqual(code(ctx="1", ident="6", entity="110104"), "KFTCP")
        self.assertEqual(code(ctx="1", ident="5", entity="110104"), "JFTCP")

    def test_exercise_variants_of_context_are_exercise(self):
        for ctx in ("5", "6"):
            self.assertEqual(code(ctx=ctx, ident="6")[0], "K")
        self.assertEqual(code(ctx="3", ident="6")[0], "H")

    def test_lookup_falls_back_to_parent_entity(self):
        self.assertEqual(code(ss="30", entity="120206"), "FSCSU")  # Littoral -> Surface Combatant
        self.assertEqual(code(ss="30", entity="140102"), "FMVMR")  # Container -> Merchant

    def test_surface_and_subsurface_mod2_overrides(self):
        self.assertEqual(code(ss="30", entity="120500", m2="09"), "FFPPT")
        self.assertEqual(code(ss="30", entity="120500"), "FPTPT")
        self.assertEqual(code(ss="35", entity="110100", m2="06"), "FNGPT")
        self.assertEqual(code(ss="35", entity="110101", m2="02"), "FDGPT")  # Surfaced + dizel

    def test_land_sets_are_separate(self):
        # 120200: set 10'da Air Traffic Services, set 15'te Tank
        self.assertEqual(code(ss="15", entity="120200"), "FTKAT")
        self.assertEqual(code(ss="10", entity="120200"), "FNSNS")
        self.assertEqual(code(ss="15", entity="220300"), "FRSSV")
        self.assertEqual(code(ss="10", entity="140700"), "FENSP")

    def test_domains(self):
        self.assertEqual(code(ss="02"), "FMSAT")
        self.assertEqual(code(ss="05"), "FSVOR")
        self.assertEqual(code(ss="36"), "FMNMW")
        self.assertEqual(code(ss="25"), "FRPNS")
        self.assertEqual(code(ss="40"), "FNSNS")

    def test_short_sidc(self):
        self.assertEqual(L.extract("123")["code_5char"], "-----")
        self.assertEqual(L.extract(None)["code_5char"], "-----")


class ReverseTests(unittest.TestCase):
    def test_fighter(self):
        r = L.reverse("fftcp")
        self.assertTrue(r["success"])
        self.assertEqual(r["suggested_sidc"], sidc(entity="110104"))

    def test_faker_sets_exercise_context(self):
        r = L.reverse("KFTCP")
        self.assertEqual((r["context"], r["identity"]), ("1", "6"))

    def test_air_modifier_only_code(self):
        r = L.reverse("FININ")
        self.assertEqual((r["entity"], r["mod1"]), ("110100", "05"))

    def test_domains(self):
        self.assertEqual(L.reverse("HDDSU")["symbol_set"], "30")
        self.assertEqual(L.reverse("HSAAD")["symbol_set"], "10")
        self.assertEqual(L.reverse("HTKAT")["symbol_set"], "15")
        self.assertEqual(L.reverse("HMNMW")["symbol_set"], "36")
        r = L.reverse("HNGPT")
        self.assertEqual((r["symbol_set"], r["entity"], r["mod2"]), ("35", "110100", "06"))

    def test_reverse_only_codes(self):
        self.assertEqual(L.reverse("FMPPT")["entity"], "110110")
        self.assertEqual(L.reverse("FLSRC")["entity"], "110111")

    def test_reference_point(self):
        self.assertEqual(L.reverse("FRPXX")["symbol_set"], "25")

    def test_unknown_platform_defaults_to_fixed_wing(self):
        r = L.reverse("FZZZZ")
        self.assertTrue(r["success"])
        self.assertEqual((r["symbol_set"], r["entity"]), ("01", "110100"))

    def test_invalid_inputs(self):
        self.assertFalse(L.reverse("ABC")["success"])
        self.assertFalse(L.reverse("ZFTCP")["success"])

    def test_round_trip_is_stable(self):
        """reverse -> extract aynı kodu vermeli (yalnızca-ters kodlar hariç)."""
        for (plat, act) in L._reverse_index():
            if (plat, act) in L.REVERSE_ONLY:
                continue
            c = f"F{plat}{act}"
            with self.subTest(code=c):
                self.assertEqual(L.extract(L.reverse(c)["suggested_sidc"])["code_5char"], c)



class CsvExportTests(unittest.TestCase):
    """tools/export_link16_csv.py çıktısı dönüştürücüyle birebir tutarlı olmalı."""

    def test_every_row_matches_converter(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
        from export_link16_csv import collect_rows

        rows = collect_rows()
        self.assertTrue(rows)
        for r in rows:
            c, s, yon = r["Ornek_Teshis_Dost"], r["Ornek_SIDC_Dost"], r["Yon"]
            with self.subTest(code=c, sidc=s):
                self.assertTrue(r["Entity_Adi"])
                if yon != "Yalnızca Link16 → SIDC":
                    self.assertEqual(L.extract(s)["code_5char"], c)
                if yon != "Yalnızca SIDC → Link16":
                    self.assertEqual(L.reverse(c)["suggested_sidc"], s)


if __name__ == "__main__":
    unittest.main()
