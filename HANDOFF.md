# Handoff: fournée workflow, continue at step 8

Repo: `~/Developer/boulangers-sympa` (GitHub `boulangers-sympa/fourdebottens`, branch `main`, Pages site www.fourdebottens.ch).

## Read first

- **The plan:** `docs/plans/fournee-workflow.md`. Its "Progress" section is current through step 7 and records how 🔥 2, 🔥 3 and 🔥 4 were built and what step 7 found. Don't re-derive them.
- **Terms:** `CONTEXT.md`. **Repo pointer:** `CLAUDE.md`.
- **Jill's Notion rules:** Agent Operating Guide (Notion page `3fd6227653ba81c196cdf01d2ee663a6`). Notion CLI with her personal login: prefix `NOTION_HOME=~/.config/ntn-personal NOTION_KEYRING=0`. `ntn api` sometimes hangs: wrap it as `perl -e 'alarm 60; exec @ARGV' ntn api …`. The Notion MCP connector works for reads, property updates and trashing pages.

## Where things stand (14 Nov 2026, 20:30)

- **The Téléthon fournée is live on the new workflow** (Run ID `2026-12-04`, Notion page `41762276-53ba-817d-9798-ee27210d4892`, Current, Ready). Orders close **27 Nov**. Jill sends the order link herself.
- Home page follows Notion (`manuel: oui` removed); `_data/fournees/2026-12-04.yml` is generated.
- Michel's Sheet: `2026-12-04 – Commandes` (`1rR_ZHQh2zFR1ockE7ip3ed_OKwPQMJbbN6AhO3NXFMs`), header row only. Old Tally Sheet URL is in the fournée's Notes.
- Make: 🔥 1 (module 14 removed), 🔥 2 (8577362), 🔥 3 Orders (1916845), 🔥 4 Daily summary (8578340, active from 15 Nov 07:00, To = Michel + Jill) all **active**.
- Test fixtures are gone (TEST Notion page, TEST Sheet, test rows).

## Check first next session

- Did 🔥 4 send anything at 07:00 on 15 Nov? With no orders it probably sends nothing; the first summary comes the morning after the first real order. Check its first real email against the Sheet.
- Jill to confirm the Tally form shows on /commandes in a normal browser (it was blank in Claude's in-app browser).
- **Not tested:** the price-mismatch alert (Jill's call) and 🔥 4's day-after GitHub route (fires 5 Dec).

## Next: step 8, the runbook

Rewrite the Notion Skill « Prepare Boulangers fournée » as the single runbook (Runs in = Both), Memories pointer, Automations database rows (`collection://25c0e878-1c49-40b0-a78b-e32b7ed1498f`), "only half tested" callout at the top. Full list in the plan's step 8. It must say:

- On a new fournée, **Orders sheet stays empty** until 🔥 2 fills it.
- **Never relink products to a test fournée**: a product belongs to one fournée only. Copy the rows instead.
- Go from Processing to Ready directly; *Needs review* starts the Fournée Finaliser.
- If Make switches a scenario off after an error: fix it, then **Save in the editor** and switch on (the API can't clear "invalid").

Also edit the **Fournée Finaliser** Notion agent's instructions: site copy without dates, and **fill a field only if it is empty**, otherwise leave it (Jill, 14 Nov). Add three lines for Michel: phone orders at the bottom, no empty rows, don't rename column headings.

## Watch out

- **Replaying 🔥 3 emails Michel** (BCC). Remove his BCC first, restore straight after.
- **Never leave two fournées Current.**
- **Make API can't show module outputs** on Jill's plan; read results in the inbox (Gmail connector works), the Sheet (Drive connector) or Make's History.
- **Make API replaces whole blueprints.** 🔥 1 (~200 KB) is edited by Jill in the UI.
- Claude can't move Drive files to trash (blocked); Jill does that.

## Decided, don't revisit

- No Notion template applied by Make; the page layout does that job.
- Keep Tally's calculated fields; Make only checks the total. Price-mismatch alert stays untested.
- Phone orders go in Michel's Sheet; Tally has no phone question.
- Michel's Sheet inherits sharing from his Drive folder.
- Keep the Fournée Finaliser agent; fix its instructions.
- Daily summary email to Michel. The daily GitHub schedule is only a backup.

## Must keep saying

- The new procedure is **only half tested** after the Téléthon. **May 2027** is the first full run.
- Jill sends the **2027 programme in January**; it becomes a home-page section (`docs/wishlist.md`).

## Logging

Update the day's Four de Bottens entry in the Agent Log, each appended update starting with local time (`HH:MM —`) (data source `ab4180b9-af2e-4ddf-ba45-6b164373faab`; 14 Nov entry `41862276-53ba-8196-842d-ff634e0c27dd`). New day → new entry.

## Suggested skills

- `wizard`: for steps only Jill can do in Notion.
- `anthropic-skills:make-documenter`: document 🔥 1–4 for the Automations rows.
- `compound`: at the end.
