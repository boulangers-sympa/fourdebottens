"""Tests for sync_fournee.py. Run: python3 -m unittest scripts/test_sync_fournee.py"""
import copy
import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import sync_fournee as s  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def load(name):
    with open(os.path.join(FIX, f"notion_{name}.json"), encoding="utf-8") as f:
        return json.load(f)["results"][0]


def rich(text):
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def with_props(page, **props):
    p = copy.deepcopy(page)
    for k, v in props.items():
        p["properties"][k.replace("_", " ")] = v
    return p


TELETHON = load("telethon")
OCTOBRE = load("octobre")
BEFORE = dt.date(2026, 11, 14)
DAY = dt.date(2026, 12, 4)
AFTER = dt.date(2026, 12, 5)
SWITCH = "actuelle: telethon\n"


class Decisions(unittest.TestCase):
    def test_ready_before_collection_writes_run_file_and_switch(self):
        files, msg, ok = s.plan([TELETHON], BEFORE, SWITCH)
        self.assertTrue(ok)
        self.assertEqual(set(files), {"_data/fournees/2026-12-04.yml", s.SWITCH_PATH})
        self.assertTrue(files[s.SWITCH_PATH].endswith("actuelle: \"2026-12-04\"\n"))

    def test_collection_day_still_shows_fournee(self):
        files, _, _ = s.plan([TELETHON], DAY, SWITCH)
        self.assertIn("_data/fournees/2026-12-04.yml", files)

    def test_after_collection_switches_to_aucune(self):
        files, _, ok = s.plan([TELETHON], AFTER, SWITCH)
        self.assertTrue(ok)
        self.assertEqual(list(files), [s.SWITCH_PATH])
        self.assertTrue(files[s.SWITCH_PATH].endswith("actuelle: aucune\n"))

    def test_no_current_switches_to_aucune(self):
        files, _, ok = s.plan([OCTOBRE], BEFORE, SWITCH)  # Octobre is Complete
        self.assertTrue(ok)
        self.assertTrue(files[s.SWITCH_PATH].endswith("actuelle: aucune\n"))

    def test_two_current_shows_aucune_and_fails(self):
        other = with_props(OCTOBRE, Status={"type": "status", "status": {"name": "Current"}})
        files, msg, ok = s.plan([TELETHON, other], BEFORE, SWITCH)
        self.assertFalse(ok)
        self.assertIn("Plusieurs", msg)
        self.assertTrue(files[s.SWITCH_PATH].endswith("actuelle: aucune\n"))

    def test_not_ready_changes_nothing(self):
        p = with_props(TELETHON, Preparation_status={"type": "select", "select": {"name": "Needs review"}})
        files, _, ok = s.plan([p], BEFORE, SWITCH)
        self.assertEqual(files, {})
        self.assertTrue(ok)

    def test_manual_override_changes_nothing(self):
        files, msg, _ = s.plan([TELETHON], BEFORE, "manuel: oui\nactuelle: telethon\n")
        self.assertEqual(files, {})
        self.assertIn("manuel", msg)

    def test_missing_deadline_is_an_error(self):
        p = with_props(TELETHON, Order_deadline={"type": "date", "date": None})
        with self.assertRaises(s.SyncError) as e:
            s.plan([p], BEFORE, SWITCH)
        self.assertIn("Order deadline", str(e.exception))

    def test_bad_run_id_is_an_error(self):
        p = with_props(TELETHON, Run_ID=rich("telethon"))
        with self.assertRaises(s.SyncError):
            s.plan([p], BEFORE, SWITCH)


class RunFile(unittest.TestCase):
    def content(self, page=TELETHON):
        return s.run_file(page)[1]

    def test_dates_and_cards_in_french(self):
        c = self.content()
        self.assertIn('date: "vendredi 4 décembre 2026"', c)
        self.assertIn('valeur: "vendredi 27 novembre"\n    rouge: oui', c)
        self.assertIn("valeur: |\n      vendredi 4 décembre\n      19h–21h30", c)

    def test_morning_times_without_minutes(self):
        self.assertIn("samedi 10 octobre\n      8h–11h", self.content(OCTOBRE))

    def test_title_falls_back_to_name_then_titre_fournee_wins(self):
        self.assertIn('titre: "Fournée du 4 décembre 2026"', self.content())
        p = with_props(TELETHON, Titre_fournée=rich("Fournée spéciale Téléthon"))
        self.assertIn('titre: "Fournée spéciale Téléthon"', self.content(p))

    def test_extra_cards(self):
        p = with_props(TELETHON, Cartes_site=rich("Pizza du four, dès 19h30 | CHF 10\n\n"))
        self.assertIn('  - libelle: "Pizza du four, dès 19h30"\n    valeur: "CHF 10"', self.content(p))

    def test_extra_card_without_bar_is_an_error(self):
        p = with_props(TELETHON, Cartes_site=rich("Pizza CHF 10"))
        with self.assertRaises(s.SyncError):
            self.content(p)

    def test_text_keeps_paragraphs(self):
        c = self.content()
        self.assertIn("texte: |\n  Fournée spéciale Téléthon 2026", c)
        self.assertIn("Bottens.\n\n  Retrait", c)

    def test_text_falls_back_to_announcement(self):
        p = with_props(TELETHON, Public_site_copy=rich(""))
        self.assertIn("texte: |\n  Fournée spéciale Téléthon 2026 au four", self.content(p))

    def test_quotes_and_colons_are_safe(self):
        p = with_props(TELETHON, Titre_fournée=rich('Le "four" : édition 2'))
        self.assertIn(r'titre: "Le \"four\" : édition 2"', self.content(p))

    def test_output_is_valid_yaml_when_pyyaml_available(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        p = with_props(TELETHON, Cartes_site=rich("Pizza | CHF 10"), Titre_fournée=rich('A "b": c'))
        data = yaml.safe_load(self.content(p))
        self.assertEqual(data["titre"], 'A "b": c')
        self.assertEqual(data["cartes"][1]["valeur"], "vendredi 4 décembre\n19h–21h30\n")
        self.assertEqual(data["cartes"][2], {"libelle": "Pizza", "valeur": "CHF 10"})
        self.assertEqual(data["cartes"][0]["rouge"], "oui")


if __name__ == "__main__":
    unittest.main()
