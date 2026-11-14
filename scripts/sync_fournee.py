"""Write the website's fournée files from the Current fournée in Notion.

Reads the Notion Fournées data source, picks the record with Status = Current
and decides what the home page shows:

- `manuel: oui` in _data/fournee.yml  -> change nothing (manual override)
- no Current fournée                   -> actuelle: aucune
- several Current fournées             -> actuelle: aucune, exit 1 (fix Notion)
- Current but not Ready                -> change nothing (still in review)
- Ready, collection date not passed    -> write _data/fournees/<run-id>.yml
                                          and actuelle: <run-id>
- Ready, collection date passed        -> actuelle: aucune

No dependencies (stdlib only). Only writes files whose content changes.

Usage:
  python3 scripts/sync_fournee.py --verifier   (lit Notion, ignore manuel: oui, n'écrit rien)
  NOTION_TOKEN=... python3 scripts/sync_fournee.py [--dry-run] [--today YYYY-MM-DD]
  python3 scripts/sync_fournee.py --from-file notion.json --dry-run
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

ZURICH = ZoneInfo("Europe/Zurich")
FOURNEES_DS = "a8371f42-bc05-443e-9548-77f29e0387a4"
NOTION_VERSION = "2025-09-03"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWITCH_PATH = "_data/fournee.yml"

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]

SWITCH_HEADER = """\
# ============================================================
#  QUELLE FOURNÉE AFFICHER ?
#  Ce fichier est mis à jour automatiquement depuis Notion
#  (la fournée « Current » dont la préparation est « Ready »).
#  Après la date de retrait, il revient à « aucune ».
#
#  Pour reprendre la main à la main, ajouter la ligne
#      manuel: oui
#  puis choisir « actuelle: » soi-même :
#  actuelle: telethon  → la fournée du fichier _data/fournees/telethon.yml
#  actuelle: aucune    → page d'accueil d'entre-deux
#                        (texte dans _data/fournees/aucune.yml)
# ============================================================

"""

RUN_HEADER = """\
# ============================================================
#  Fichier écrit automatiquement depuis Notion : ne pas le modifier ici,
#  il serait remplacé. Modifier la fournée dans Notion.
# ============================================================

"""


class SyncError(Exception):
    """A problem Jill must fix in Notion. The message is in French."""


# ---------- Notion ----------

def fetch_current(token, data_source=FOURNEES_DS):
    """Return the Notion pages whose Status is Current."""
    body = json.dumps({"filter": {"property": "Status", "status": {"equals": "Current"}}}).encode()
    req = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{data_source}/query",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)["results"]
    except urllib.error.HTTPError as e:
        raise SyncError(f"Notion a répondu {e.code} : {e.read().decode(errors='replace')[:300]}")
    except urllib.error.URLError as e:
        raise SyncError(f"Notion injoignable : {e.reason}")


def prop_text(page, name):
    """Plain text of a title / rich_text / select / status property, or ''."""
    p = page["properties"].get(name)
    if not p:
        return ""
    kind = p["type"]
    if kind in ("title", "rich_text"):
        return "".join(t["plain_text"] for t in p[kind]).strip()
    if kind in ("select", "status"):
        return (p[kind] or {}).get("name", "")
    return ""


def prop_date(page, name):
    """(start, end) strings of a date property, or (None, None)."""
    p = page["properties"].get(name)
    d = p.get("date") if p else None
    if not d:
        return None, None
    return d.get("start"), d.get("end")


# ---------- French formatting ----------

def to_zurich(value):
    """Parse a Notion date or datetime string into a Zurich-local datetime."""
    if len(value) == 10:
        return dt.datetime.fromisoformat(value).replace(tzinfo=ZURICH)
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(ZURICH)


def jour_mois(d):
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]}"


def heure(t):
    return f"{t.hour}h{t.minute:02d}" if t.minute else f"{t.hour}h"


# ---------- YAML (written by hand, always safe) ----------

def yaml_quoted(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_block(s, indent):
    pad = " " * indent
    lines = s.strip("\n").split("\n")
    return "|\n" + "\n".join((pad + line) if line.strip() else "" for line in lines)


# ---------- What to show ----------

def run_file(page):
    """Return (run_id, yaml text) for a Ready fournée. Raises SyncError if a field is missing."""
    run_id = prop_text(page, "Run ID")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", run_id):
        raise SyncError(f"« Run ID » manquant ou mal écrit ({run_id!r}), attendu AAAA-MM-JJ")
    start, end = prop_date(page, "Collection date")
    if not start:
        raise SyncError("« Collection date » est vide")
    deadline, _ = prop_date(page, "Order deadline")
    if not deadline:
        raise SyncError("« Order deadline » est vide")

    debut = to_zurich(start)
    if end and len(start) > 10:
        horaire = f"{heure(debut)}–{heure(to_zurich(end))}"
    else:
        horaire = prop_text(page, "heure_fournée")
    retrait = jour_mois(debut) + (f"\n{horaire}" if horaire else "")

    titre = prop_text(page, "Titre fournée") or prop_text(page, "Name")
    texte = prop_text(page, "Public site copy") or prop_text(page, "Announcement")

    cartes = [
        ("Dernier délai pour commander", jour_mois(to_zurich(deadline)), True),
        ("Retrait des commandes, au four", retrait, False),
    ]
    for line in prop_text(page, "Cartes site").splitlines():
        if not line.strip():
            continue
        if "|" not in line:
            raise SyncError(f"« Cartes site » : la ligne {line!r} doit être « Libellé | Valeur »")
        libelle, valeur = (x.strip() for x in line.split("|", 1))
        cartes.append((libelle, valeur, False))

    out = [RUN_HEADER.rstrip("\n"), ""]
    out.append(f"titre: {yaml_quoted(titre)}")
    out.append(f"date: {yaml_quoted(f'{jour_mois(debut)} {debut.year}')}")
    out.append("")
    out.append("cartes:")
    for libelle, valeur, rouge in cartes:
        out.append(f"  - libelle: {yaml_quoted(libelle)}")
        if "\n" in valeur:
            out.append(f"    valeur: {yaml_block(valeur, 6)}")
        else:
            out.append(f"    valeur: {yaml_quoted(valeur)}")
        if rouge:
            out.append("    rouge: oui")
    out.append("")
    out.append(f"texte: {yaml_block(texte, 2)}" if texte else 'texte: ""')
    return run_id, "\n".join(out) + "\n"


def collection_day(page):
    start, _ = prop_date(page, "Collection date")
    if not start:
        raise SyncError("« Collection date » est vide")
    return to_zurich(start).date()


def plan(pages, today, switch_text):
    """Decide the files to write.

    Returns (files, message, ok): files maps repo-relative path -> content
    (only the ones to write), ok is False when the run should show red.
    """
    if re.search(r"^manuel:\s*(oui|true|yes)\s*$", switch_text, re.M | re.I):
        return {}, "manuel: oui dans _data/fournee.yml : rien n'est changé.", True

    current = [p for p in pages if prop_text(p, "Status") == "Current"]
    if len(current) > 1:
        names = ", ".join(prop_text(p, "Name") for p in current)
        return ({SWITCH_PATH: SWITCH_HEADER + "actuelle: aucune\n"},
                f"Plusieurs fournées « Current » dans Notion ({names}) : page d'entre-deux affichée.",
                False)
    if not current:
        return ({SWITCH_PATH: SWITCH_HEADER + "actuelle: aucune\n"},
                "Aucune fournée « Current » : page d'entre-deux.", True)

    page = current[0]
    name = prop_text(page, "Name")
    if prop_text(page, "Preparation status") != "Ready":
        return {}, f"{name} n'est pas encore « Ready » : rien n'est changé.", True
    if today > collection_day(page):
        return ({SWITCH_PATH: SWITCH_HEADER + "actuelle: aucune\n"},
                f"{name} est passée : page d'entre-deux.", True)

    run_id, content = run_file(page)
    return ({f"_data/fournees/{run_id}.yml": content,
             SWITCH_PATH: SWITCH_HEADER + f"actuelle: \"{run_id}\"\n"},
            f"{name} affichée (actuelle: {run_id}).", True)


def read(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="afficher sans écrire")
    ap.add_argument("--today", help="date du jour AAAA-MM-JJ (tests)")
    ap.add_argument("--from-file", help="réponse Notion enregistrée (JSON) au lieu de l'API")
    ap.add_argument("--verifier", action="store_true",
                    help="lire Notion et montrer ce qui serait écrit, même avec manuel: oui ; n'écrit rien")
    args = ap.parse_args(argv)

    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(ZURICH).date()
    try:
        if args.from_file:
            with open(args.from_file, encoding="utf-8") as f:
                pages = json.load(f)["results"]
        else:
            token = os.environ.get("NOTION_TOKEN")
            if not token:
                raise SyncError("NOTION_TOKEN n'est pas défini")
            pages = fetch_current(token, os.environ.get("NOTION_FOURNEES_DS", FOURNEES_DS))
        switch_text = read(SWITCH_PATH)
        if args.verifier:
            args.dry_run = True
            switch_text = re.sub(r"^manuel:.*$", "", switch_text, flags=re.M)
            print(f"Vérification : {len(pages)} fournée(s) « Current » lue(s) dans Notion. Rien ne sera écrit.")
        files, message, ok = plan(pages, today, switch_text)
    except SyncError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    print(message)
    for path, content in files.items():
        if read(path) == content:
            print(f"  {path} : inchangé")
            continue
        if args.dry_run:
            print(f"\n----- {path} -----\n{content}")
        else:
            with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  {path} : écrit")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
