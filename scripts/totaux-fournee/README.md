# Totaux fournée (page privée)

Petite page web pour Jill et Michel : les totaux des commandes de la fournée **Current**, en direct. Pas de noms, pas d'emails : seulement le nombre de commandes (site / téléphone), la quantité par produit et la date limite. Pas de total en CHF (Jill, 15 nov.).

## Comment ça marche

- C'est un **Google Apps Script** (projet « Totaux fournée (Four de Bottens) » sur script.google.com, compte de Jill), publié comme application web.
- À chaque ouverture, la page :
  1. demande à Notion la fournée `Status = Current` (jeton `NOTION_TOKEN` dans les *Propriétés du script*, jamais dans ce dépôt) ;
  2. lit le tableau de Michel (`Orders sheet`), lignes à partir de la 3 ;
  3. compte avec les mêmes règles que 🔥 4 : Source « tally » = site, le reste = téléphone ; une case produit compte seulement si c'est un nombre ; colonnes A–P seulement ; produits = les en-têtes de colonnes du tableau (hors Date, Source, Nom, Prénom, Email, Téléphone, Total, Remarques), dans l'ordre du tableau. Notion sert seulement à trouver la fournée Current, son tableau, sa date et sa date limite.
- Elle compare aussi ses chiffres à la ligne TOTAL (ligne 2) et affiche un avertissement s'ils diffèrent.
- **Aucun coût Make.** Rien n'est enregistré ailleurs.

## Confidentialité

- L'adresse de la page (`script.google.com/macros/s/…/exec`) est longue et aléatoire. Elle n'est **pas** dans ce dépôt public. Ne pas la coller dans un site, ni dans Messages/Notes (aperçus de lien).
- Accès : « Tout le monde » (pas de connexion Google nécessaire). Qui a l'adresse voit les totaux, rien d'autre.
- Pour couper l'accès : script.google.com → le projet → *Déployer* → *Gérer les déploiements* → archiver. Un nouveau déploiement donne une nouvelle adresse.

## Mettre à jour le code

Depuis ce dossier, avec `clasp` (connecté au compte de Jill) :

```bash
npx -y @google/clasp@2.4.2 push -f
```

Puis mettre à jour le déploiement existant (même adresse) :

```bash
npx -y @google/clasp@2.4.2 deploy -i <ID du déploiement> -d "description"
```

L'ID du déploiement : `npx -y @google/clasp@2.4.2 deployments`. `.clasp.json` (l'ID du projet) n'est pas versionné.

## Test

`computeTotals` est une fonction pure. Dans l'éditeur Apps Script, *testTotals* affiche les totaux dans le journal.
