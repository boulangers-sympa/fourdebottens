# Wishlist

Ideas for later. Not scheduled.

- **Histoire: new banner photo.** The current one (`assets/img/four-et-cure.jpg`, the oven with the cure) is only 616px wide and looks soft. Needs a sharper photo, at least 1600px wide.
- **Programme 2027.** Jill will send the 2027 programme in January 2027. Add it as a section at the bottom of the home page (the old Google Sites home page had a "Programme complet 2026" list). Keep it in one data file so it's easy to update each year. Next fournée after the Téléthon: May 2027.
- **Full editing guide.** README instructions (in French) for changing every piece of text on the site: home page, cards, Histoire, Contact, captions, nav.
- **Edit from Notion.** Manage the fournée (title, date, cards, text) in Notion and have Make write the fournée to GitHub (now split: `_data/fournee.yml` is the one-line switch, content lives in `_data/fournees/*.yml`) through the API, so nobody needs to edit files on github.com.
- **Contact map link.** Once Google approves the new "Four de la Cure" place, swap the coordinates link in `contact.md` for the place link so the name shows.
- **Fournée cards.** Revisit the three-card layout (deadline, pickup, pizza price) before the next non-Téléthon fournée. Already possible: each file in `_data/fournees/` has its own `cartes:` list, and the grid adapts to 2, 3 or 4 cards. Still open: what a normal fournée should show (bread list? prices?) and whether cards need more than a label and a value.
- **Phone-order form for Michel.** Today Michel types phone orders into his Sheet and works out the Total himself. A separate Tally form for phone orders would give every row a total with no formula. If it goes through 🔥 3, it must write Source « Téléphone » (🔥 4 and the Totaux page count « Tally » as site orders) and skip the confirmation email. Decided 16 Nov 2026: no Total formula in the Sheet (a formula in empty rows makes 🔥 3 append below them; one in K1 would need 🔥 3 to stop writing Tally's total).
