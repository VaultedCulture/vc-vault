# TCG Vault

A separate, working Pokémon collection tracker inspired by the PopVault reference and PokeScreener workflows. This version runs on your own computer; it is not a publicly hosted website or a PokeScreener integration.

## Open it

Double-click **Start TCG Vault.cmd**, then use http://127.0.0.1:8765. The launcher uses the bundled Python already on this computer, or Python from PATH on another computer. Alternatively run `python server.py` from this folder with Python 3.10 or newer. No Python packages are required.

## Collect

1. Open **Explore sets** and choose a set. English physical TCG sets are shown; data comes from TCGdex.
2. Tick several cards (or choose **Select displayed cards**). Your selection survives search/filter changes within the current view.
3. Choose **Review & add**, set print variants, quantities and condition, then save the batch.
4. Use **Track this whole set** to create a checklist. Choose one of each numbered card, or standard catalogue-listed prints.
5. **Missing** reveals gaps. On a standard-print checklist, a card can appear here even when one of its other prints is already owned. The print badges explain which you still need.
6. Use **Missing list** to export the checklist as CSV. **Master sets** shows progress for every set being tracked.

Click a card name to adjust existing quantities. Wishlist hearts, collection statistics and undo are also available. Duplicate copies never increase checklist completion. Removing the last owned copy makes that card/print missing again.

## Saved collection

The app stores ownership, checklist goals and wishlist in `collection.sqlite3` beside the server. It survives reloads and restarts and does not rely on browser storage. Keep this file when moving the app. **Export backup** downloads a readable JSON snapshot; restoring JSON is not yet a UI feature. For a full restorable backup, close the server and copy the app folder, including `collection.sqlite3`. Do not delete this database when updating the app.

The collection starts empty. Your existing PokeScreener records were inspected as a design reference, not imported or modified. User accounts, cloud sync, a camera scanner and automated price-history tracking are not included in this first version.

## Catalogue and prices

Real card information and remote artwork are supplied by [TCGdex](https://tcgdex.dev/). 151, 30th Celebration and Prismatic Evolutions metadata are cached with this release. Other sets download on first opening and may take a little longer. Images and uncached sets need internet access. The catalogue index and downloaded details are cached on disk; automatic refresh is not implemented. Cached price dates are visible in card details. Prices are USD TCGplayer market references where available, not adjusted for your card condition. Missing prices are omitted from the reference total.

The standard-print master checklist uses the catalogue's regular/holo/reverse/first-edition/W-promo flags. Special stamped releases, foil patterns, and promotional exceptions are not exhaustive. Unknown print metadata is labelled unspecified rather than guessed. Pokémon intellectual property belongs to its respective owners; this app is unofficial.

## Technical notes

Python standard-library HTTP server, SQLite storage, vanilla HTML/CSS/JavaScript. The server is intentionally bound only to `127.0.0.1`, checks Host/Origin, and requires a session token for writes. Do not expose this development server to the internet. A hosted version would need production hosting, authentication, backup management and per-user storage.

Run the included data-integrity tests with `python -m unittest test_server.py`. Tests use temporary databases, never your collection.
