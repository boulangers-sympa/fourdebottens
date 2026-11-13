"""Prépare les photos ajoutées dans assets/img/photos/ pour le site.

Pour chaque photo pas encore préparée (ou qui contient encore des métadonnées) :
- la tourne dans le bon sens (orientation iPhone),
- la réduit à 1600 px maximum,
- retire toutes les métadonnées (position GPS, appareil, date),
- l'enregistre en JPEG sous le nom AAAA-MM-JJ-nom.jpg (date d'ajout),
- supprime l'original.

Lancé automatiquement par GitHub à chaque modification du site.
Nécessite : pip install pillow pillow-heif
"""
import datetime
import pathlib
import re
import sys
import unicodedata

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:  # HEIC (iPhone) non pris en charge sans pillow-heif
    pass

DOSSIER = pathlib.Path(__file__).resolve().parent.parent / "assets" / "img" / "photos"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp"}
NOM_PRET = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.jpg$")
TAILLE_MAX = 1600


def slug(texte: str) -> str:
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    texte = re.sub(r"[^a-z0-9]+", "-", texte.lower()).strip("-")
    return texte or "photo"


def a_des_metadonnees(img: Image.Image) -> bool:
    return bool(img.getexif()) or any(k in img.info for k in ("exif", "xmp", "XML:com.adobe.xmp"))


def preparer(chemin: pathlib.Path, aujourdhui: str) -> pathlib.Path | None:
    with Image.open(chemin) as img:
        if NOM_PRET.match(chemin.name) and not a_des_metadonnees(img) and max(img.size) <= TAILLE_MAX:
            return None
        img = ImageOps.exif_transpose(img)
        img.thumbnail((TAILLE_MAX, TAILLE_MAX))
        if img.mode != "RGB":
            img = img.convert("RGB")
        # Copie pixel par pixel : aucune métadonnée ne suit.
        propre = Image.new("RGB", img.size)
        propre.paste(img)

    if NOM_PRET.match(chemin.name):
        cible = chemin
    else:
        base = f"{aujourdhui}-{slug(chemin.stem)}"
        cible = chemin.with_name(base + ".jpg")
        n = 2
        while cible.exists() and cible != chemin:
            cible = chemin.with_name(f"{base}-{n}.jpg")
            n += 1
    propre.save(cible, "JPEG", quality=82, optimize=True, progressive=True)
    if cible != chemin:
        chemin.unlink()
    return cible


def main() -> int:
    aujourdhui = datetime.date.today().isoformat()
    for chemin in sorted(DOSSIER.iterdir()):
        if chemin.suffix.lower() not in EXTENSIONS:
            continue
        resultat = preparer(chemin, aujourdhui)
        if resultat:
            print(f"{chemin.name} -> {resultat.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
