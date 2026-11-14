# Handoff: fournée workflow, continue at step 7

Repo: `~/Developer/boulangers-sympa` (GitHub `boulangers-sympa/fourdebottens`, branch `main`, Pages site www.fourdebottens.ch).

## Read first

- **The plan:** `docs/plans/fournee-workflow.md`. Its "Progress" section is current through step 6 and records how 🔥 2, 🔥 3 and 🔥 4 were built (they differ from the original spec). Don't re-derive them.
- **Terms:** `CONTEXT.md`. **Repo pointer:** `CLAUDE.md`.
- **Commits:** `a7cdb4e` (steps 1–3), `5dee413` (step 4), `3286ff7` (step 5), step 6 in the commit after `39ffa57`.
- **Jill's Notion rules:** Agent Operating Guide (Notion page `3fd6227653ba81c196cdf01d2ee663a6`). Notion CLI with her personal login: prefix `NOTION_HOME=~/.config/ntn-personal NOTION_KEYRING=0`. `ntn api` sometimes hangs: macOS has no `timeout`, so wrap it as `perl -e 'alarm 60; exec @ARGV' ntn api …`, and check the result before retrying a PATCH. The Notion MCP connector also works for reads and property updates.

## Where things stand (14 Nov 2026, 19:00)

- **Goal:** go live on the **Téléthon fournée** (Run ID `2026-12-04`, Notion page `41762276-53ba-817d-9798-ee27210d4892`, Status **Current**). The order link has **not** gone out; orders close **27 Nov**. Everything must be tested before Jill sends it.
- `_data/fournee.yml` still has **`manuel: oui`** (live site unchanged until step 7).
- **Steps 0–6 done:**
  - 0–3: sync script, GitHub workflow « Fournée depuis Notion », `NOTION_TOKEN`.
  - 4: Make **🔥 2 Fournée ready (Sheet + website)** (8577362, active) + Notion automation on Preparation status → Ready. Creates `<Run ID> – Commandes` in Michel's shared Drive folder with product columns, writes Orders sheet, dispatches GitHub. GitHub token lives in Make's HTTP connection « Jill's API Key connection » (expires 31 Dec 2027).
  - 5: **🔥 3 Orders** (1916845) now also adds each Tally order to Michel's Sheet by column heading and emails Jill if Tally's total ≠ Notion prices or if there's no Sheet. Tested by replay: row correct.
  - 6: **🔥 4 Daily summary to Michel** (8578340), daily 07:00, **inactive**. Tested on the TEST Sheet with two phone rows: counts and totals right (Jill checked). Recipient is fourdebottens@gmail.com for now (a privacy plugin blocks Claude from writing Jill's address into Make). The day-after GitHub dispatch route is untested.
- **Test fixtures (delete at step 7, ask Jill first):** Notion page « TEST 🔥 2 – à supprimer » (`41862276-53ba-8154-a702-cebc461611d1`, Status Planning) and Sheet `TEST-2026-12-04 – Commandes` (one Tally row, two phone rows).
- **Backup:** the pre-step-5 🔥 3 blueprint is in the repo folder as `🔥 3 Orders (Tally → email + Sheet).blueprint.json`, git-ignored (contains email addresses). Make ⋮ → Import Blueprint restores it.

## Next: step 7, switch on for the Téléthon

1. **Check 🔥 2 first:** on 14 Nov at 18:35 Make reported 🔥 2 Fournée ready as **inactive and invalid** (`isActive: false`, `isinvalid: true`), although step 4 recorded it as active. Open it in Make, find the invalid module, reactivate. Step 7 needs it.
2. Remove module 14 from 🔥 1 (Jill, in the UI).
3. Téléthon: move its `Orders sheet` URL to a note (« Permanent Sheet »), clear the field, set Preparation status to Ready again → 🔥 2 makes Michel's Sheet.
4. 🔥 4: Jill sets To = Michel, adds herself as BCC, then activate it.
5. Remove `manuel: oui`; check the home page matches today's (pizza card included).
6. Full test order (launch checklist section 3), also testing the **price-mismatch alert** and **moving two columns** in Michel's Sheet. Delete test rows from both Sheets afterwards. Only then does Jill send the order link.

Then **step 8:** rewrite the Notion Skill « Prepare Boulangers fournée » as the single runbook (Runs in = Both), Memories pointer, Automations database rows (`collection://25c0e878-1c49-40b0-a78b-e32b7ed1498f`), "only half tested" warning at the top. Also edit the **Fournée Finaliser** Notion agent's instructions (site copy without dates), and add three lines for Michel: phone orders at the bottom, no empty rows, don't rename column headings.

## Watch out

- **Replaying 🔥 3 emails Michel** (BCC). Before any replay, remove his BCC; restore it straight after. Two test emails reached him on 14 Nov.
- **Never leave two fournées Current.** To test with TEST: Téléthon → Planning, TEST → Current, test, swap back.
- **TEST shares product pages with the Téléthon.** Don't change a product price to test the alert.
- **Make API can't show module outputs** on Jill's plan (no Pro): after a test run, Jill reads the result in the inbox or Make's History.
- **Make API replaces whole blueprints.** Fetch, edit, send the whole thing. 🔥 1 (~200 KB) is edited by Jill in the UI. Make UI rejects `/"/g` regex in formulas, and `split(url; "/")` drops empty pieces.
- **Incomplete executions keep a frozen copy of the scenario**; after fixing a module, delete them rather than retrying.
- **Fournée Finaliser** (Notion custom agent) runs when a fournée moves to *Needs review* and rewrites Public site copy and the confirmation texts.

## Decided, don't revisit

- No Notion template applied by Make; the page layout does that job.
- Keep Tally's calculated fields; Make only checks the total.
- Phone orders go in Michel's Sheet; Tally has no phone question.
- Michel's Sheet inherits sharing from his Drive folder (no share step).
- Keep the Fournée Finaliser agent; fix its instructions.
- Daily summary email to Michel. The daily GitHub schedule is only a backup.

## Must keep saying

- The new procedure is **only half tested** after the Téléthon. **May 2027** is the first full run.
- Jill sends the **2027 programme in January**; it becomes a home-page section (`docs/wishlist.md`).

## Logging

At the end of each session, update the day's Four de Bottens entry in the Agent Log. Start each appended update with the local time (`HH:MM —`) (data source `ab4180b9-af2e-4ddf-ba45-6b164373faab`; 14 Nov entry is `41862276-53ba-8196-842d-ff634e0c27dd`). On a new day, create a new entry.

## Suggested skills

- `work`: continue `docs/plans/fournee-workflow.md` from step 6.
- `wizard`: for steps only Jill can do in Make, Notion or Tally.
- `senior-review`: before switching on at step 7.
- `anthropic-skills:make-documenter`: document 🔥 1–4 for the Automations rows.
- `compound`: at the end.
