# Les Boulangers Sympa: site du Four de Bottens

Site statique (Jekyll), publié par GitHub Pages à chaque modification
(voir l'onglet **Actions** sur github.com pour suivre la mise en ligne).

## La page d'accueil suit Notion

La fournée affichée sur la page d'accueil vient de la fournée **Current**
dans Notion (base **Fournées**). Une action GitHub, « Fournée depuis
Notion », écrit les fichiers `_data/fournees/<date>.yml` et
`_data/fournee.yml`, puis publie le site. Elle tourne :

- quand la fournée passe à **Ready** dans Notion ;
- le lendemain de la fournée (le site repasse à « aucune fournée ») ;
- chaque matin, par sécurité ;
- à la main : onglet **Actions** → « Fournée depuis Notion » → **Run workflow**.

Pour changer le titre, les cartes ou le texte : modifier la fournée dans
Notion (**Titre fournée**, **Cartes site**, **Public site copy**), puis
lancer **Run workflow** pour ne pas attendre le lendemain.

Mode d'emploi complet d'une nouvelle fournée : le skill Notion
« Prepare Boulangers fournée ».

### Reprendre la main (`manuel: oui`)

Pour écrire la page d'accueil à la main, ajouter `manuel: oui` dans
`_data/fournee.yml`. L'action ne change alors plus rien. Ensuite :

| Ligne | Page d'accueil | « Commandes » |
|---|---|---|
| `actuelle: telethon` | le fichier `_data/fournees/telethon.yml` (exemple fait à la main) | visible, formulaire ouvert |
| `actuelle: aucune` | page d'entre-deux | caché, formulaire fermé |

Le mot après `actuelle:` est le nom d'un fichier du dossier
`_data/fournees/`, sans `.yml`. Un nom mal écrit affiche la page
d'entre-deux (le site ne casse pas). Retirer `manuel: oui` pour que la
page suive à nouveau Notion.

## Modifier le texte d'entre-deux

C'est le fichier `_data/fournees/aucune.yml` : un titre, un sous-titre
et le texte.

### Règles pour les textes (`texte:`)

```yaml
texte: |
  Premier paragraphe.

  Deuxième paragraphe.
```

- Garder le `|` après `texte:`.
- Commencer chaque ligne par **2 espaces**.
- Laisser une **ligne vide** entre deux paragraphes.
- Pour mettre un mot en gras : `**pizza du four**`.
- Pour un lien : `[histoire du four](/histoire/)`.

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
