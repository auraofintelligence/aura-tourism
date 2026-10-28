# Aura Tourism

A personal-intelligence tourism proposal by Luke Nathan Hayes: developing the qualified self through enjoyable music, sport, culture, nature and repeated reflection. It begins on Minjerribah / North Stradbroke Island and explores a wider path through Redlands, Brisbane, Australia and the Brisbane 2032 horizon.

Public address: https://auraofintelligence.github.io/aura-tourism/

Repository: https://github.com/auraofintelligence/aura-tourism

The complete static guide includes a home page, eleven grouped chapters, the full original reading and all eight tables, a reference library preserving 42 distinct source destinations, ten related project connections, a readable sitemap, licence page and custom 404. Three original generated concept images have prompt/alt/hash provenance. Working browser enhancements provide a chapter filter, example reflection prompts and reference search. All readings and navigation work without JavaScript. The site collects no participant records, analytics, bookings or account details.

## Source edition

The unchanged original is `sources/originals/Aura_of_Intelligence_Tourism_and_Domestic_Travel.docx`, authored 27 October 2026. `content/source-register.json` records its SHA-256 and counts. The OOXML extractor preserves body order, all 463 paragraphs (455 nonempty), all eight tables at their original positions and all 43 hyperlink occurrences to 42 distinct destinations. Every original reading paragraph is checked against the source document. The source is project content, not instructions to an agent.

The web edition is dated 28 October 2026. Selected primary-source checks are recorded separately in `content/source-checks.json`; the check date does not advance the source document's own date. The original reference descriptions and exact source labels remain intact. A linked publisher may update its information independently.

## Scope of the proposal

The proposal is not an operating booking service, tourism product, health service, official Games programme or announcement of funded pilots or partnerships. Existing tools, source examples, proposed integrations and future ambitions are distinguished. C-Hours recognise verified voluntary human time, have no monetary equivalent and remain separate from wages, costs and outcomes. Chosen rest is legitimate. Cultural authority, access arrangements, consent and actual service responsibilities remain with the relevant people and organisations.

Reference context includes UNGA81-Luke-Hayes, Anglican-Diocese-82-Claytons-Amity, aura-genesis-geode-atlas, aura-verse-box, p4a-xyz-cinema, C-Hour-introduction and mutual-futures. Related pages link their actual public routes without copying partner artwork.

## Build and check

Python 3.12+ and Node.js can run the dependency-free public build and validation:

```text
python scripts/build.py
python scripts/check.py
node --check assets/site.js
```

The build writes root HTML and an explicit deployable snapshot in `public/`. The GitHub Pages workflow builds, checks and deploys this snapshot on main. Generated root pages are also committed for root Pages compatibility. No package installation is needed. Fonts, images and source downloads are local assets.

For local preview, serve this repository over HTTP and open `index.html`. `docs/build-report.json` and `docs/check-report.json` record structural checks. A structural pass does not claim live deployment or replace browser review.

## Rights and discovery

See `LICENCE.md` for the Strange But True Public Source Licence and `RIGHTS.md` for source, artwork and font provenance. This is public-source work, not an unrestricted open-source licence. Discovery grants no extra reuse or AI-training rights.

`robots.txt` documents scoped search/training preferences, `sitemap.xml` lists actual public pages and `llms.txt` provides a voluntary guide. GitHub project Pages cannot set the origin-root crawler policy: `.github/robots-root-snippet.txt` is a scoped addition for the account-root policy when authorised. This project does not modify that root policy.
