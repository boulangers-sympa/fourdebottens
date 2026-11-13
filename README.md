# Les Boulangers Sympa: site du Four de Bottens

Site statique (Jekyll), publié par GitHub Pages à chaque modification
(voir l'onglet **Actions** sur github.com pour suivre la mise en ligne).

## Préparer une nouvelle fournée

1. Ouvrir `_data/fournee.yml` sur github.com
2. Cliquer sur le crayon ✏️ (Edit)
3. Changer le titre, la date, les cartes et le texte
4. Cliquer sur **Commit changes**

Le site se met à jour 1 à 2 minutes plus tard.

### Modifier le texte sous le bouton « Je commande »

C'est la partie `texte:` à la fin de `_data/fournee.yml` :

```yaml
texte: |
  Premier paragraphe.

  Deuxième paragraphe.
```

- Garder le `|` après `texte:`.
- Commencer chaque ligne par **2 espaces**.
- Laisser une **ligne vide** entre deux paragraphes.
- Pour mettre un mot en gras : `**pizza du four**`.

Si le site ne se met pas à jour, ouvrir l'onglet **Actions** : une croix
rouge ❌ signale en général un espace manquant au début d'une ligne.

## Aperçu local

```
jekyll serve
```
puis ouvrir http://localhost:4000

## Ajouter des photos à la Galerie

1. Ouvrir le dossier `assets/img/photos` sur github.com
2. Cliquer sur **Add file** puis **Upload files**
3. Glisser les photos (JPG, PNG ou HEIC d'iPhone, n'importe quelle taille)
4. Cliquer sur **Commit changes**

Après 2 à 3 minutes, les photos sont en ligne. GitHub les prépare tout seul :
il les tourne dans le bon sens, les réduit et retire la position GPS. Il les
renomme aussi avec la date du jour (par ex. `2026-11-13-img-1234.jpg`).
Les plus récentes s'affichent en premier.

**Légende (facultatif) :** ajouter une ligne dans `_data/legendes.yml`,
par exemple `2026-11-13-img-1234.jpg: Pizzas du Téléthon`.

**Retirer une photo :** l'ouvrir dans `assets/img/photos`, cliquer sur les
trois points **…** puis **Delete file**, puis **Commit changes**.

⚠️ La photo d'origine (avec sa position GPS) reste dans l'historique de
GitHub, qui est public. Les photos prises au four ne posent pas de
problème (l'adresse du four est publique). Pour une photo prise ailleurs,
désactiver la position avant de l'envoyer (iPhone : bouton **Options** en
haut de l'écran de partage, puis désactiver **Lieu**).

## Photos fixes (bannières, accueil, Histoire)

Dans `assets/img/`. Toujours retirer les métadonnées avant de les ajouter :

```
python3 scripts/strip_jpeg_metadata.py photo.jpg assets/img/photo.jpg
```
