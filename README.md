# Les Boulangers Sympa: site du Four de Bottens

Site statique (Jekyll), publié par GitHub Pages.

## Préparer une nouvelle fournée

1. Ouvrir `_data/fournee.yml` sur github.com
2. Cliquer sur le crayon ✏️ (Edit)
3. Changer le titre, la date, les cartes et le texte
4. Cliquer sur **Commit changes**

Le site se met à jour 1 à 2 minutes plus tard.

## Aperçu local

```
jekyll serve
```
puis ouvrir http://localhost:4000

## Photos

Toujours retirer les métadonnées (position GPS des iPhone) avant d'ajouter une photo :

```
python3 scripts/strip_jpeg_metadata.py photo.jpg assets/img/photo.jpg
```
