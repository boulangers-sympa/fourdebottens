# Context

Domain terms used in this repo and its plans.

- **Fournée**: one baking day at the Four de Bottens, with its own products, order deadline and pickup time. One record in the Notion **Fournées** database.
- **Run ID**: the fournée's collection date as `YYYY-MM-DD` (e.g. `2026-12-04`). Names the Notion record, Michel's Sheet and the website file `_data/fournees/<run-id>.yml`.
- **Current fournée**: the single Notion record with `Status = Current`. Make and the website both read it.
- **Ready**: `Preparation status = Ready` on the Current fournée. Jill sets it after reviewing what Make extracted from Michel's email. It starts the automation (Michel's Sheet, website).
- **Permanent form**: the one Tally order form reused for every fournée (products not offered are hidden, never deleted).
- **Permanent Sheet**: the Google Sheet that Tally's own integration fills with every Tally order, all fournées together. A free safety net; nobody works in it.
- **Michel's Sheet**: one Google Sheet per fournée, named with the Run ID, with columns only for the products offered. Make adds each Tally order; Michel adds phone orders and rearranges freely.
- **Daily summary**: the morning email to Michel with order counts and totals per product, Tally and phone orders together.
- **Site override**: `manuel: oui` in `_data/fournee.yml`. Stops the Notion sync from changing the home page.
