# Handoff: fournée workflow, continue at step 5

Repo: `~/Developer/boulangers-sympa` (GitHub `boulangers-sympa/fourdebottens`, branch `main`, Pages site www.fourdebottens.ch).

## Read first

- **The plan:** `docs/plans/fournee-workflow.md`. Its "Progress" section is current through step 3. It holds the decisions, module changes, steps 4–8, tests, inputs and open questions. Don't re-derive them.
- **Terms:** `CONTEXT.md`. **Repo pointer:** `CLAUDE.md`.
- **Commits:** `a7cdb4e` (steps 1–3), `826c2d2` (plan progress).
- **Jill's rules for Notion:** her Agent Operating Guide (Notion page `3fd6227653ba81c196cdf01d2ee663a6`), including logging and skills. Use the Notion CLI with her personal login: prefix with `NOTION_HOME=~/.config/ntn-personal NOTION_KEYRING=0`. `ntn api … -X PATCH` sometimes hangs. Run it with a 60 s timeout and retry once.

## Where things stand (14 Nov 2026, evening)

- **Goal:** go live on the **Téléthon fournée** (Run ID `2026-12-04`, Notion page `41762276-53ba-817d-9798-ee27210d4892`). It is still in pre-testing: the order link has **not** gone out, and orders close **27 Nov**. Everything must be tested before Jill sends the link.
- **Done:**
  - **Steps 0–3:** sync script, GitHub workflow « Fournée depuis Notion » with a « Vérifier seulement » option, and the `NOTION_TOKEN` secret (an internal Notion connection called "Four de Bottens", connected to Fournées and Fournée products). Both test runs were green.
  - `_data/fournee.yml` has **`manuel: oui`**, so the live site is unchanged. It is removed only at step 7.
- **Notion:**
  - New fields **Titre fournée** and **Cartes site**, filled in for the Téléthon. Its Public site copy now equals the site text.
  - **Page layout:** Status and Preparation status pinned; then sections « À vérifier », « Liens et notes », and « Lu par Make » (hidden).
- **Make** (org 66035, team 42323):
  - Renamed `🔥 1 Prepare fournée (email → Notion)` (6947556) and `🔥 3 Orders (Tally → email + Sheet)` (1916845).
  - Jill updated 🔥 1's model to `claude-opus-5-5` and cleared the incomplete executions.
- **Decided, don't revisit:**
  - No Notion template is applied by Make; the layout does that job.
  - Keep Tally's calculated fields; Make only checks the total.
  - Phone orders go in Michel's Sheet.
  - Daily summary email to Michel.
  - The daily GitHub schedule is only a backup.

## Next: step 5, 🔥 3 Orders (total check + row writer)

Step 4 is done and tested (see plan → Progress, 14 Nov). 🔥 2 Fournée ready is active; the Notion automation sends its webhook when Preparation status becomes Ready.

- Test on the Notion page « TEST 🔥 2 – à supprimer » and its Sheet `TEST-2026-12-04 – Commandes` (in Michel's folder). Delete both after step 6.
- 🔥 3 is ~5 modules and small enough to update through the Make API, but it is **live** (Tally orders): Jill should save a copy first, or do it in the UI.
- Fix found today for step 8: the Notion custom agent **Fournée Finaliser** writes Public site copy and the confirmation texts at *Needs review*. Keep it; edit its instructions (no dates in site copy).
- Watch out: the Make API replaces whole blueprints. 🔥 1 (~200 KB) is edited by Jill in the UI. At step 7 the Téléthon's `Orders sheet` URL moves out so 🔥 2 creates Michel's Sheet.

Then steps 5–8 as in the plan. Step 8 = rewrite the Notion Skill « Prepare Boulangers fournée » as the single runbook (Runs in = Both), add a Memories pointer and rows in the Automations database (`collection://25c0e878-1c49-40b0-a78b-e32b7ed1498f`), and put the "only half tested" warning at the top.

## Must keep saying

- The new procedure is **only half tested** after the Téléthon. **May 2027** (the next fournée) is the first full run. This is in the plan, the Agent Log and memory.
- Jill sends the **2027 programme in January**; it becomes a home-page section (`docs/wishlist.md`).

## Logging

At the end of each session, update today's Four de Bottens entry in the Agent Log (data source `ab4180b9-af2e-4ddf-ba45-6b164373faab`; today's entry is `41862276-53ba-8196-842d-ff634e0c27dd`). On a new day, create a new entry.

## Suggested skills

- `work`: execute `docs/plans/fournee-workflow.md` from step 4, one verified slice at a time.
- `notion-cli`: Agent Log updates and Notion API checks with `ntn`.
- `anthropic-skills:make-documenter`: document 🔥 1–4 once built (useful for the Automations rows).
- `wizard`: for steps only Jill can do (GitHub token, Notion automation, sharing the Drive folder).
- `senior-review`: before switching on at step 7.
- `compound`: at the end, to capture lessons.

Out of scope here: the proposed session "Make Notion the home of all personal skills" (a separate card).
