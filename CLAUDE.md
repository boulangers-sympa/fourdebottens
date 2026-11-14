# Four de Bottens site

- **Setting up a new fournée** ("let's set up a new fournée", "nouvelle fournée", "I've forgotten how"): use the Notion skill **Prepare Boulangers fournée** (Jill's Notion Skills database). Until it is rewritten, the plan is [docs/plans/fournee-workflow.md](docs/plans/fournee-workflow.md). The next fournée after the Téléthon 2026 (May 2027) is the first full run of the new workflow: go step by step and check each automatic step.
- Terms: [CONTEXT.md](CONTEXT.md). How to edit the site (in French, for non-developers): [README.md](README.md).
- The home page follows the Current fournée in Notion through `scripts/sync_fournee.py` and the « Fournée depuis Notion » GitHub Action. `manuel: oui` in `_data/fournee.yml` stops that.
