# Plan: Fournée preparation workflow

Terms are defined in [CONTEXT.md](../../CONTEXT.md).

## Problem

Preparing a fournée today means:

1. Asking a Notion AI agent for the procedure. It loads the **Prepare Boulangers fournée** skill, an out-of-date SOP that only describes steps.
2. Forwarding Michel's email to the 🔥 1 Prepare fournée Make mailhook (this works well).
3. Duplicating and editing a Tally form by hand, including prices in calculated fields and conditional logic (prices also live in Notion; the St-Nicolas rule broke in Nov 2026).
4. Creating a Google Sheet, connecting Tally to it, sharing it with Michel.
5. Updating the website by hand (`_data/fournees/*.yml`, `_data/fournee.yml`), although Notion already holds the same facts. The SOPs still describe Google Sites, which is gone.

Three procedures disagree with each other: the Notion AI skill, the **New fournée** template body and the **Fournée launch checklist**.

Goal: Jill forwards the email, reviews Notion, adjusts Tally visibility, sets Ready, runs one test order. Everything else is automatic, idempotent and observable.

## Testing status (read this first)

This procedure is **only half tested**. It goes live on the Téléthon fournée (4 Dec 2026), which exercises the order path, Michel's Sheet, the daily summary and the website sync. It does **not** exercise the very start of the cycle on a normal fournée: forwarding a new email from Michel → 🔥 1 Prepare fournée → review → Ready, with a different product list and no special cards. The next fournée is **May 2027**, so treat that one as the first full test: allow extra time, follow the runbook step by step and watch every automated step happen.

The runbook (step 8) and the Agent Log must both say this.

## Decisions settled with the user

- **Keep** the email forward → 🔥 1 Prepare fournée (mailhook → Claude extraction → Notion fournée + products).
- **One permanent Tally form** (currently `Z9EgM5`, the Téléthon form). Per fournée, Jill only shows/hides products and updates the closing date and texts. No more duplicating, renaming or reconnecting webhooks.
- **Keep Tally's calculated fields and conditional logic**: they show the customer the total at the end of the form. Make adds a **check**: it computes Σ qty × Notion price and emails Jill if it differs from Tally's `prix_total`.
- **Keep Tally's own Google Sheets integration**, pointed once at the **Permanent Sheet** (free, safety net if Make fails).
- **Michel's Sheet per fournée**, columns only for products offered. Michel checks it while orders are open and adds **phone orders** himself. No two-tab design.
- **Make writes each Tally order into Michel's Sheet** as it arrives (~2 Make operations per order).
- **Daily summary email to Michel** while orders are open: counts and per-product totals, Tally + phone.
- **No website embed parameter** (`?fournee=`): phone orders bypass the website, so the fournée is identified from the Current Notion record instead.
- **Website follows Notion**: a GitHub Action writes the website files from the Current fournée.
- **One runbook**: the New fournée template body. The Notion AI skill becomes a pointer to it (or is deleted).
- **Extraction model**: Jill updates 🔥 1 Prepare fournée's Claude module by hand (the API needs the whole 200 KB blueprint): `claude-opus-5-5`, temperature cleared, thinking not "disabled", effort `low` if offered, max tokens 16000.

### Engineering decisions (made in planning)

- **Trigger = Notion automation on `Preparation status` → Ready**, sending a webhook to a new Make scenario 🔥 2 Fournée ready. Instant, and costs no polling operations. The GitHub Action also runs every hour as a backstop, so a missed webhook only delays the site.
- **Michel's Sheet is created at Ready, not at email forward**: the product list can still change during review.
- **Rows are written by header name, not column position.** Make reads row 1, then builds the row in that order. Michel can reorder columns; he must not rename the headers.
- **The confirmation email keeps showing Tally's `prix_total`** (what the customer saw on the form). A mismatch only alerts Jill.
- **Website files**: the Action writes `_data/fournees/<run-id>.yml` (kept in git as history) and sets `actuelle: <run-id>` in `_data/fournee.yml`. After the collection date it sets `actuelle: aucune`.
- **Site override**: if `_data/fournee.yml` has `manuel: oui`, the Action changes nothing. This replaces hand-editing as the way to take control (e.g. the Téléthon special cards).
- **Sync code is Python stdlib only** (`urllib`, `json`), like the existing `scripts/`. No new dependencies.
- **Commits by the Action do not trigger `publier.yml`** (GitHub ignores push events made with `GITHUB_TOKEN`). The sync workflow therefore runs `gh workflow run publier.yml` after committing; `workflow_dispatch` is exempt from that rule.
- **Go live with the Téléthon fournée (Run ID `2026-12-04`).** It is still in pre-testing; the order link has not gone out. Everything must be live and tested before the link goes out, and orders close on 27 Nov.
- **The existing Téléthon Sheet (`1eeEAIm…`, already connected to Tally `Z9EgM5`) becomes the Permanent Sheet.** Its URL moves out of the fournée's `Orders sheet` field, so 🔥 2 Fournée ready creates a fresh Michel's Sheet for the Téléthon.

## Module changes

### Repo (`boulangers-sympa`)

**New `scripts/sync_fournee.py`**
- Input: env `NOTION_TOKEN`, `NOTION_FOURNEES_DS` (`a8371f42-bc05-443e-9548-77f29e0387a4`). Flags: `--dry-run` (print the files, don't write), `--today YYYY-MM-DD` (for tests).
- Queries the Fournées data source (`POST /v1/data_sources/{id}/query`, `Notion-Version: 2025-09-03`) for `Status = Current`.
- Decides the desired state:
  - `manuel: oui` in `_data/fournee.yml` → exit 0, no change.
  - No Current record, or more than one → `actuelle: aucune`; with more than one, also exit 1 so the run shows red (Jill gets GitHub's failure email).
  - Current but `Preparation status ≠ Ready` → leave the site as it is.
  - Current + Ready + today ≤ collection date (Europe/Zurich) → write `_data/fournees/<run-id>.yml` and `actuelle: <run-id>`.
  - Current + Ready + today > collection date → `actuelle: aucune`.
- Generated file shape (matches what `index.html` reads now):
  ```yaml
  # Fichier écrit automatiquement depuis Notion — ne pas modifier ici.
  titre: <Name>
  date: <date_fournée>
  cartes:
    - libelle: Dernier délai pour commander
      valeur: <Order deadline, French long form, e.g. "vendredi 27 novembre">
      rouge: oui
    - libelle: Retrait des commandes, au four
      valeur: |
        <date_fournée without the year>
        <heure_fournée>
    # then one card per line of the Notion property "Cartes site" (format: Libellé | Valeur)
  texte: |
    <Public site copy, else Announcement>
  ```
- Writes only when the content changes (byte compare), so hourly runs don't create commits.
- Errors: Notion HTTP error or a missing required field (`Run ID`, `date_fournée`, `heure_fournée`, `Order deadline`) → exit 1 with the field name in French, no files written.
- YAML is written by hand (no PyYAML). Values are always emitted as block scalars (`|`) or quoted, so colons and accents are safe.

**New `.github/workflows/fournee.yml`** ("Fournée depuis Notion")
- Triggers: `repository_dispatch` (type `fournee`, sent by Make at Ready and by 🔥 4 Daily summary on the first day after the collection date), `workflow_dispatch`, and `schedule` once a day (`17 4 * * *`) as a backstop. A run with nothing to change takes about 15 seconds and makes no commit. GitHub turns off schedules after 60 days without repo activity; the Make dispatches don't depend on it.
- Permissions: `contents: write`, `actions: write`.
- Steps: checkout → `python scripts/sync_fournee.py` → if `git status --porcelain _data` shows changes, commit as `github-actions[bot]` ("Fournée : mise à jour depuis Notion"), push, `gh workflow run publier.yml`.
- `concurrency: fournee` so two runs never commit at once.

**`_data/fournee.yml`**: comment block updated to explain that Notion drives it and `manuel: oui` stops that.

**`README.md`**: the French "Préparer la fournée" section is rewritten: the site follows Notion; how to use `manuel: oui`; telethon.yml stays as a hand-made example.

**`commandes.html`**: unchanged (the permanent Tally embed stays).

### Notion

- **Fournées**: add text property **Cartes site** (optional extra cards, one per line `Libellé | Valeur`, e.g. `Pizza du four, dès 19h30 | CHF 10`).
- **Fournées**: add text property **Titre fournée** (optional heading under « Prochaine fournée » on the home page, e.g. `Fournée spéciale Téléthon`; empty → `Name`). The big page title « Bienvenue au Four de Bottens » never changes.
- **Fournées**: `Orders sheet` keeps holding the URL of Michel's Sheet; add **Sheet ID** (text) for Make. The existing `Spreadsheet ID` formula can replace this if it already extracts the ID from `Orders sheet`; check its formula first and use it if so.
- **Database automation**: when `Preparation status` is set to `Ready` → Send webhook to 🔥 2 Fournée ready (body: page ID).
- **Page layout of Fournées** (done 14 Nov 2026, applies to every fournée page however it was created): Status and Preparation status pinned under the title; section **À vérifier** (Collection date, Order deadline, Products offered, Titre fournée, Public site copy, Cartes site, Confirmation intro HTML, Confirmation footer HTML, Additional details); section **Liens et notes** (Orders sheet, Run ID, Notes); section **Lu par Make (ne pas modifier)** with Make-only fields hidden (date_fournée, heure_fournée, Email product list, Email lines, Spreadsheet ID, Announcement, Tally form). No template is applied by Make (decided 14 Nov 2026): the layout does the job, and the runbook lives in the New fournée template for pages created by hand.
- **New fournée template body**: replaced by the single runbook (below), short enough to fit on one screen under the properties.
- **Prepare Boulangers fournée** skill: replaced by "Follow the runbook in the New fournée template" plus a link; or deleted.
- **Fournée launch checklist**: Tally sections cut down to visibility, closing date and texts; test-order section kept; it becomes part of the runbook.

### Make

**Scenario names** (numbered so they read as one set, renamed 14 Nov 2026):
1. `🔥 1 Prepare fournée (email → Notion)` (6947556)
2. `🔥 2 Fournée ready (Sheet + website)` (new)
3. `🔥 3 Orders (Tally → email + Sheet)` (1916845, formerly Fournée master)
4. `🔥 4 Daily summary to Michel` (new)


**🔥 1 Prepare fournée** (6947556)
- Remove module 14 (copy Sheet template). Michel's Sheet moves to Fournée ready.
- Claude module: the model update above (manual).

**New 🔥 2 Fournée ready** (custom webhook from Notion)
1. Get the fournée page. Stop unless `Status = Current` and `Sheet ID` is empty (idempotent: a second webhook does nothing).
2. Get its Fournée products, sorted by `Display order`.
3. Create spreadsheet named `<Run ID> – Commandes` in the Boulangers Drive folder.
4. Write header row: `Date | Source | Nom | Prénom | Email | Téléphone | <product 1> | … | Total | Remarques`. Product header = `Form label override`, else `Product name`.
5. Share with Michel (editor).
6. Write `Orders sheet` (URL) and `Sheet ID` to the fournée.
7. HTTP: `POST https://api.github.com/repos/<owner>/boulangers-sympa/dispatches` with `{"event_type":"fournee"}` and a fine-grained token (this repo only, Contents: read and write).

**🔥 3 Orders** (1916845), after "Get Current fournée":
- **Total check**: a Numeric aggregator over the existing product feeder, Σ qty × price. A router branch: if it ≠ `prix_total` (tolerance 0.01) → email Jill "Total Tally ≠ Notion" with both figures and the order name. The customer email is unchanged.
- **Row to Michel's Sheet**: Google Sheets "Get range values" `A1:1` (headers) → build the row by mapping each header to its value (meta fields from the webhook; product headers from the feeder's name→qty; `Source = Tally`; `Total = prix_total`) → "Make an API call" `values:append` with `valueInputOption=USER_ENTERED`, `insertDataOption=INSERT_ROWS`.
- If `Sheet ID` is empty: skip the row and email Jill (the order is still in the Permanent Sheet).
- The email module's error handler is unchanged.

**New 🔥 4 Daily summary** (scheduled 07:00 Europe/Zurich)
1. Get the Current fournée. Stop if none, if `Sheet ID` is empty, or if today > collection date.
2. Get all values from Michel's Sheet.
3. For each product column (headers matching Fournée products): sum the numbers. Count rows, split by Source.
4. Email Michel (BCC Jill): subject `Commandes au <date> | Fournée <date_fournée>`; body: number of orders (Tally / téléphone), one line per product with its total, link to the Sheet.
5. Stop sending after the collection date. On the first day after it, send the GitHub `fournee` dispatch instead, so the site switches to `aucune` that morning.

### Tally (one-off)

- Make `Z9EgM5` the permanent form: unhide all established products, then hide what the next fournée doesn't offer.
- Google Sheets integration → the Permanent Sheet (one-off).
- Webhook → the existing Make hook (already set).

## Implementation steps

Each step ends in something checkable. All steps run now, in order, on the Téléthon fournée; no real customer orders exist yet, so test orders are safe (delete them from both Sheets afterwards).

0. ~~Clear the 3 incomplete executions in 🔥 3 Orders; update the Claude model in 🔥 1 Prepare fournée.~~ Done by Jill, 14 Nov 2026.
1. **`sync_fournee.py` + tests** (`--dry-run` against the real Notion). Check: dry run on the Téléthon record prints a file equivalent to `telethon.yml` (except the pizza card, which comes from Cartes site).
2. **Add `Cartes site` in Notion** and fill it for the Téléthon record. Check: the dry run now prints the pizza card.
3. **`fournee.yml` workflow** with `manuel: oui` set in `_data/fournee.yml` (so it changes nothing live). Add secrets. Check: a manual run goes green and changes nothing.
4. **🔥 2 Fournée ready** scenario + Notion automation, tested on a copy fournée with `Status = Planning` (temporarily remove the Current check in step 1 of the scenario, or test with a duplicate data source). Check: Sheet created with the right columns, shared, URL in Notion, dispatch received by GitHub.
5. **🔥 3 Orders**: total check + row writer. Test via Make "Run once" with a replayed Tally payload against a test Sheet. Check: row lands in the right columns after reordering two columns; a forced price mismatch sends the alert.
6. **🔥 4 Daily summary**: run once by hand against the test Sheet with two phone rows added. Check: totals correct, Tally/téléphone split correct.
7. **Switch on for the Téléthon**: remove module 14 from 🔥 1 Prepare fournée; move the Téléthon `Orders sheet` URL to a note ("Permanent Sheet"), clear it, then set `Preparation status` to Ready again so 🔥 2 Fournée ready creates Michel's Sheet; remove `manuel: oui`; check the generated home page matches today's (pizza card included); run the full test order (launch checklist section 3). Only then send the order link.
8. **Runbook = the existing Notion Skill « Prepare Boulangers fournée »**, rewritten (Skills database; Jill's Agent Operating Guide says reusable procedures live in Notion Skills, and it's what Jill already asks her Notion agent for). One page that both Jill and the agent read. Link it from the Fournées database description; the New fournée template body becomes a one-line link to it. Post the change comment on the skill page (guide rule).
   - **Two ways in, one skill.** Next May Jill will start either in Claude Code in this repo ("hi, let's set up a new fournée") or in Notion AI ("how do we set up a new fournée, I've forgotten"). Set the skill's **Runs in = Both** so the existing Notion→Claude Code skill sync installs it in Claude Code too. Its description must trigger on plain phrases: "new fournée", "set up / prepare a fournée", "nouvelle fournée", "I've forgotten how".
   - The skill tells the agent what it can do itself and what only Jill can do: check Make 🔥 1 ran, read the Current fournée and list empty « À vérifier » fields, check Michel's Sheet exists after Ready, check the site switched (and in Claude Code, run the GitHub workflow / dry-run the sync). Jill alone: forward the email, edit copy, Tally visibility, Ready, test order.
   - **Memory pointer**: one entry in Jill's Memories database (Type Work, Source Claude Code): "Setting up a fournée: follow the Notion skill « Prepare Boulangers fournée »; next fournée May 2027 is the first full run of the new workflow." So a Notion agent that doesn't match the skill still finds it.
   - **Repo `CLAUDE.md`**: one line pointing Claude Code at the skill (already added 14 Nov 2026). **Automations database**: one row per moving part (🔥 1–4 Make scenarios, the GitHub Action « Fournée depuis Notion »), Status Active, URL to each, Notes pointing to the skill. Then: shrink the launch checklist into it, replace the Notion AI skill; update README. The runbook's review step says: check **Titre fournée**, **Cartes site** and **Public site copy** (the paragraph under the cards: no dates, the cards show those) while the fournée is *Needs review*; after Ready, Notion edits reach the site at the next daily run, or straight away with Actions → « Fournée depuis Notion » → Run workflow. Also change the instructions of the Notion custom agent **Fournée Finaliser** (it writes `Public site copy`, `Confirmation intro HTML` and `Confirmation footer HTML` when a fournée moves to *Needs review*; found 14 Nov 2026) so `Public site copy` is written that way (short, no deadline/pickup dates, no price list). Keep the agent: nothing else writes the confirmation texts. **Fill only empty fields** (Jill, 14 Nov 2026): for each field it writes, the agent first checks whether the field already has text; if it does, it leaves it unchanged. So moving a fournée back to *Needs review* never overwrites copy Jill has edited. Add it to the Automations database as a moving part. The runbook opens with a callout: "First used for the Téléthon 2026; the start of the cycle (new email → Ready on a normal fournée) is untested until May 2027. Allow extra time and check each automatic step."

### Progress

- 14 Nov 2026: step 0 done (Jill). Step 1 done: `scripts/sync_fournee.py` + 18 unit tests pass; a local Jekyll build with the generated Téléthon files shows the right title, dates, cards and text. `actuelle:` is written quoted (`"2026-12-04"`) so YAML keeps it as text, not a date.
- 14 Nov 2026: step 2 done. Notion Fournées has **Titre fournée** and **Cartes site**; the Téléthon has `Fournée spéciale Téléthon` and `Pizza du four, dès 19h30 | CHF 10`. Dry run against live Notion: title, date and all three cards match `telethon.yml`; only the body text differs (Notion `Public site copy` is longer and repeats the cards). Jill chose to copy the site text into Notion; regenerated output is now identical to `telethon.yml` (quotes aside).
- 14 Nov 2026: step 3 done. Workflow pushed (a7cdb4e) with `manuel: oui`. `NOTION_TOKEN` = internal connection « Four de Bottens » (read-only, Fournées + Fournée products). Manual run with « Vérifier seulement » read the Téléthon from Notion on GitHub (green); a normal run said « rien n'est changé » (green); « Publier le site » green. `--verifier` / the « Vérifier seulement » tick box checks Notion without writing, even with `manuel: oui`.
- 14 Nov 2026: step 4 done. Make scenario **🔥 2 Fournée ready (Sheet + website)** (8577362, active), webhook `🔥 2 Fournée ready (from Notion)` (4106010). Notion database automation « 🔥 2 Fournée ready »: Preparation status set to Ready → Send webhook. Built differently from the spec above:
  - **No share step.** The Sheet is created (Drive API, connection « Make Google ») in Michel's Drive folder `1BIxshbveYJrpnCvWwbouKGdH-Mvi80pa`, which is already shared with him; the Sheet inherits that.
  - **No Sheet ID field.** Idempotency = the scenario stops if `Orders sheet` is already filled (the existing `Spreadsheet ID` formula reads it). Guard: Preparation status = Ready, Status ≠ Complete (not "= Current", so a Planning copy can be tested), Orders sheet empty.
  - Product headers come from `Email product list` (3rd field, `name`), sorted like 🔥 3. That `sort()` is alphabetical: fine up to 9 products, wrong order from 10.
  - GitHub dispatch uses the HTTP v4 connection « Jill's API Key connection » (header `Authorization: Bearer <fine-grained token>`, allowed origin `https://api.github.com`; token expires 31 Dec 2027). Make shows a stored key as `masked-api-key`; the first save had a bad key and GitHub answered 401.
  - Tested on the Notion page « TEST 🔥 2 – à supprimer » (Run ID `TEST-2026-12-04`, Status Planning): Sheet `TEST-2026-12-04 – Commandes` created in the folder with the right 12 headers, its URL written to Orders sheet, GitHub run `repository_dispatch` green (« manuel: oui … rien n'est changé »). Keep the TEST page and Sheet for steps 5–6, then delete both.
- 14 Nov 2026: step 5 mostly done. 🔥 3 Orders now has a router: route 1 = the unchanged confirmation email; route 2 = products again → JSON items (name, qty, qty × Notion price) → (a) email Jill if Σ ≠ Tally `prix_total` (> 0.01), (b) read row 1 of Michel's Sheet (Get range values A1:Z1, sheet `Sheet1`) and **Add a row** where each of the first 16 columns is filled by its header name (Date, Source = Tally, Nom, Prénom, Email, Téléphone empty, products by name, Total, Remarques = « 4. Communications ? »), only if the headers contain "Source" (so the Permanent Sheet is never written to); (c) email Jill if the Current fournée has no Orders sheet. Sheet ID = the part of `Orders sheet` after `/d/` (splitting on `/` failed: Make drops empty pieces). Sheet errors go to Retry (3×), never block the email. Backup of the old blueprint: `*.blueprint.json` in the repo folder, git-ignored. Built by `build_fire3.py` (scratchpad, not kept).
  - Tested by replaying this afternoon's test order with the TEST fournée temporarily Current and Michel's BCC temporarily removed (both restored): row landed correctly (St-Nicolas 4, Total 16); no total alert. Two earlier replays, before the fixes, BCC'd Michel.
  - **Still to test:** a forced price mismatch alert (don't change a product price: the TEST fournée shares product pages with the Téléthon) and moving two columns in Michel's Sheet. Do both in the step 7 test order.
  - Tally has no phone question; Téléphone is for Michel's phone orders.
- 14 Nov 2026: step 6 done. Make scenario **🔥 4 Daily summary to Michel** (8578340), daily 07:00, **inactive** until step 7. Built as specced, with these details:
  - Router: route 1 runs while today ≤ Collection date and `Orders sheet` is set: reads row 1 (headers) and rows A2:Z1000 of `Sheet1`, skips empty rows, and turns each cell into a number under its header (the fixed columns Date…Remarques count as 0). Products and their order come from `Email product list`, like 🔥 2 and 🔥 3. Source « Tally » (any case) = par le site; anything else = par téléphone.
  - Route 2 sends the GitHub `fournee` dispatch only on the day after the Collection date (same HTTP connection as 🔥 2). **Not tested** (it needs that date).
  - Email recipient is **fourdebottens@gmail.com** for now: a privacy plugin stops Claude from writing Jill's address into Make. At step 7 Jill sets To = Michel and adds herself as BCC in the Make UI.
  - Tested with the TEST fournée temporarily Current: TEST Sheet with the Tally row (St-Nicolas 4) and two phone rows (gdv 1 + St-Nicolas 2; grande tresse 3). Email: 3 commandes (1 site, 2 téléphone), St-Nicolas 6, gdv 1, grande tresse 3. Jill confirmed. Notion swapped back afterwards.
  - Seen while building: Make reports **🔥 2 Fournée ready as inactive and invalid** (it was recorded as active). Check before step 7.
- 14 Nov 2026: **step 7 done. The Téléthon is live on the new workflow.**
  - 🔥 2 had been switched off and marked invalid by Make after its 17:37 GitHub 401. The key was fixed by 17:47, but `scenarios_activate` cannot clear the invalid flag: Jill had to **Save in the editor**, then switch it on. Applies to any scenario Make switches off after an error.
  - 🔥 1: module 14 removed. Module 7 (Notion « Create a Data Source Item ») used to fill `Orders sheet` from it; that field is now empty. **Orders sheet must stay empty on a new fournée**, or 🔥 2 skips it.
  - **The Fournée products relation allows one fournée per product.** Linking the four Téléthon products to the TEST page at step 4 had moved them off the Téléthon, so 🔥 2's first run made a Sheet with no product columns. Products were relinked and 🔥 2 rerun: `2026-12-04 – Commandes` has 12 headers. To test with a copy fournée, make **copies** of the product rows, never relink them.
  - Old Tally Sheet URL moved to the Téléthon's Notes (« Permanent Sheet »). Preparation status changed empty → Ready, never via *Needs review* (that starts the Fournée Finaliser).
  - `manuel: oui` removed; the sync wrote `_data/fournees/2026-12-04.yml`, identical to `telethon.yml`; site published and checked (title, three cards including the pizza card, text).
  - Test order 1 (1/2/3/4, CHF 41.50) and order 2 (after moving Grande tresse to the right of St-Nicolas: St-Nicolas 1, Grande tresse 2) both landed in the right columns; emails right; Michel got BCC copies. **Price-mismatch alert not tested**: Jill decided it isn't worth it (prices rarely change).
  - Test rows deleted (Michel's Sheet, Tally), TEST page and TEST Sheet removed. 🔥 4 To = Michel + Jill, **active** from 15 Nov 07:00. With no orders it probably sends nothing (empty sheet → no bundles); unverified.
  - The Tally embed on /commandes stayed blank in Claude's in-app browser; the form itself loads on tally.so. Jill confirmed the form shows on the site in a normal browser.
- 14–15 Nov 2026 (evening): **total row in Michel's Sheet, 🔥 2 hardened.**
  - **Row 2 of Michel's Sheet is a TOTAL row**: `TOTAL` in Nom, and `=SUM(INDEX(A3:Z,0,COLUMN()))` under each product (same formula in every cell: it sums its own column from row 3 down, and moves with the column). Rows 1–2 frozen and bold. Orders start at row 3; 🔥 3's Add a row still appends at the bottom.
  - 🔥 4 « Read order rows » now reads **A3:Z1000** (otherwise it would count the total row as a phone order and double every total). Jill changed it in the UI.
  - 🔥 2 now writes the total row (modules 10–12: products again → formulas → PUT A2, USER_ENTERED) and freezes and bolds rows 1–2 (module 13, batchUpdate, sheetId 0). **Not tested yet**: first run on the next fournée. Check the new Sheet has the TOTAL row.
  - The Téléthon Sheet got its total row by hand (product columns only; the Total CHF column K2 is empty).
  - **🔥 2 was switched off again** at 20:03 on 14 Nov: its webhook received an **empty call** (`{}`, no Notion page), module 2 asked Notion for `/v1/pages/` and got 400; with *sequential* on, Make stops the scenario. An earlier empty call caused the 18:53 failure. **Source found**: Make's webhook log shows a GET from Jill's own home IP with the Apple link-preview user agent (`… Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0`): the webhook URL had been pasted into an app that builds link previews (Messages, Notes, Mail…). Harmless, but don't paste webhook URLs into such apps. Fix: a filter « Has a Notion page » on module 2, so empty calls stop quietly. Jill saved 🔥 2 in the editor and switched it on.
  - Phone orders are counted by 🔥 4 (it reads the Sheet, not Tally): Source « tally » = site, anything else = phone. Product cells must hold a number only (« 2 pains » counts as 0). Only columns A–P are read.
- 15 Nov 2026: **Totaux fournée page** (live order totals for Jill and Michel, no names). Code: `scripts/totaux-fournee/` (README in French).
  - Notion custom blocks were ruled out: a block can only read a Notion database bound to it (no network), guests can't see them, private alpha; Michel isn't in Notion.
  - Built as a **Google Apps Script web app** (project « Totaux fournée (Four de Bottens) », Jill's Google account, deployed with `clasp`; `.clasp.json` git-ignored). Each view asks Notion for the Current fournée (`Orders sheet`, `date_fournée`, `Order deadline`), reads Michel's Sheet from row 3 and counts like 🔥 4: Source « tally » = site, anything else = phone; product cells count only if numeric; columns A–P. **Product names = the Sheet's column headings** (Jill's choice), not `Email product list`. No CHF total (Jill). Warns if its totals differ from the TOTAL row (row 2) or if two fournées are Current. No Make operations.
  - Notion token: the read-only « Four de Bottens » connection, stored in the script's *Script properties* as `NOTION_TOKEN` (never in the repo). That connection can't read **Bakery products**, so `Email product list` comes back as `01|||4.5` (names missing); hence names from the Sheet.
  - Execute as Jill, access « Anyone » (no Google login). The URL is long and random and is **not in the repo**; Jill keeps it and sends it to Michel herself. Updating the code keeps the same URL (`clasp deploy -i <deployment id>`).
  - Checked live on 15 Nov with no orders yet: title, deadline 27.11.2026, four products from the Sheet, all 0 = TOTAL row. **Still to check:** the first real orders against the TOTAL row.

## Test approach

- **Unit (repo)**: `scripts/test_sync_fournee.py` (stdlib `unittest`), fixtures = saved Notion API JSON for the Téléthon and October records. Covers: each desired-state branch, `--today` before/on/after collection date, `manuel: oui`, two Current records, missing field, colon/accents/newlines in texts, no write when content is unchanged.
- **Workflow**: manual `workflow_dispatch` with `manuel: oui` (no-op), then on a test branch without it.
- **Make**: each scenario tested with "Run once" on recorded payloads before activation; 🔥 3 Orders tested end-to-end with one live test order (launch checklist section 3), including a column reorder in Michel's Sheet.
- **First real fournée**: watch the first 3 orders land in both Sheets; check the first daily summary against a hand count.

## Inputs needed

- **Notion integration token** (internal integration, Jill's personal workspace) with read access to Fournées and Fournée products → GitHub secret `NOTION_TOKEN`. Never in chat.
- **GitHub fine-grained token** for Make (this repo only, Contents: read and write) → stored in Make's HTTP connection.
- **Michel's Google account email** for sharing (the Make share step).
- **Drive folder** for Michel's Sheets (existing Boulangers folder ID).
- **Date the order link goes out** for the Téléthon (sets the deadline for steps 1–7).
- **Notion plan check**: database automations with "Send webhook" need a paid Notion plan. If not available, fallback: a Notion button that opens the Make webhook URL, or Make polling every 15 min (~100 ops/day; avoid).

## Open questions

- Should the daily summary skip days with no new orders? (Default: send anyway, so Michel knows it's working.)
- Should phone orders get a confirmation email? (Default: no; Michel handles them.)
- What should the third card be for a normal fournée (bread list? prices)? This plan only supports free cards via Cartes site; see the "Fournée cards" wishlist item.

## Out of scope

- Per-product oven capacity in Notion and capacity warnings in the daily summary (good follow-up).
- Closing Tally automatically or hiding products through the Tally API.
- Programme 2027 / full-year list on the website.
- Moving 🔥 3 Orders's Notion lookups or email to another tool.
