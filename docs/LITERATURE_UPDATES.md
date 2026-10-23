# Public literature updates

The owner authorized an all-English public literature page on 2026-10-23. URL: https://hanmd1990.github.io/literature/ . This is a native GitHub Pages page with the shared lab header, fonts and HMD palette. `tools/literature_layout.py` builds it after the other page generators and adds LITERATURE before CONTACT in all shared navigation menus.

## Weekly publication

The existing literature task still runs on Fridays at 03:30 Asia/Shanghai. Keep the private Chinese full journal report, its full collection rules and its feedback private. In addition, export **all relevant articles** (relevance 1–3) to this public English page. Do not publish personal feedback, interest scores, private notes, credentials, unpublished research plans, private Drive links or site authentication data. Do not make the original private report public.

1. Read the latest main and this file. Check the existing archive and weekly DOI/ID deduplication.
2. Add `data/literature/YYYY-MM-DD.json`; preserve prior public editions. Fields: `id`, `start`, `end` (Beijing time), `updated`, `note`, `articles`, `coverage`. Each article: `id`, optional `doi`, `title` (original English), `journal`, `date`, full `authors` array as verified, `authorsComplete`, HTTPS `url`, `relevance` (1–3), `summary` (concise original English), `topics` (English array), `type` (English, explicitly label corrections and preprints; retain section-unverified status if applicable). Coverage: journal and complete/partial/unavailable status; `note` must explain meaningful coverage limitations in English.
3. Translate summaries for a public research audience. Remove private comparisons to unpublished lab work and personal feedback. Preserve quantities and evidence limits; distinguish demonstrated results from possible applications. Never invent missing author names or results. Preprints must be explicitly identified as not peer reviewed. No copied full abstracts, full-text PDFs or unlicensed figures.
4. Update `data/literature/index.json`: `latest` is the new edition ID; `editions` lists every public edition, newest first. Only mark delivered content as published after successful deployment.
5. Build in an isolated output copy; never run the main builder against editable sources. Run `python tools/build_site.py OUTPUT`, `python tools/verify_site.py OUTPUT`, `node tools/check_archive_ui.cjs OUTPUT`, and `node --check static/literature.js`. Check English-only public data, DOI uniqueness, all relevant entries retained, working filters/sorting/edition selection and original-source links. Generated HTML includes full article content even without JavaScript.
6. Commit only public data and intended source changes through the GitHub connector to latest main with expected_sha; do not overwrite concurrent edits. Verify Pages deployment before reporting the new public edition live. If publication fails, preserve the previous public edition and accurately report the blocker.

The first public edition is 2026-10-23: 43 related entries (41 direct/method-transferable plus 2 adjacent). Figures remain at their publisher links. No external data connection, private API or iframe is needed for visitors. Feedback from the private report is not exposed or collected by this public page.

## Portal design revision — 2026-10-23

The portal is now **DeepBioE Beta**. Put its prominent navy badge beside the Mengdi Han Research Group identity on every shared page; remove LITERATURE from the existing menu. Keep the `/literature/` URL.

Journals included opens an accessible modal with searchable checkboxes for every surveyed journal and preprint source, including those with no selected papers this edition. Support multiple choices, Select all/Clear all, Apply and Cancel. Topic categories should be generated during each weekly editorial update from recent actual reader preferences/feedback and selected literature; do not claim feedback exists when none was recorded. The public taxonomy is shared; per-account recommendations are not yet implemented.

Show the automatic weekly update schedule at the top in Beijing, New York and London time. The authoritative schedule is Friday 03:30 Asia/Shanghai. Compute upcoming corresponding weekday/time using IANA zones America/New_York and Europe/London so daylight saving is handled; do not hardcode a year-round offset. Article metadata rows display only journal and date. Keep type metadata internally and preserve correction/preprint context in the summary, but do not render Article or section-unverified badges. The latter meant the publisher's precise section/type was unconfirmed, not that peer review failed.

The public portal currently has no shared feedback or sign-in service. Do not create nonfunctional voting/login buttons or claim public feedback is being saved. The owner is considering account-based Useful / More like this / Not relevant feedback; authentication and backend selection remain a separate decision.

2026-10-23 naming refinement: use DeepBioE Beta in the shared header badge, page title and portal heading. Remove the visible daylight-saving explanatory sentence, while preserving IANA-zone time conversion.

2026-10-23 journal-selector grouping: group the checkbox list by Nature Portfolio, Science journals, Cell Press, Wiley, ACS, Elsevier, IOP Publishing, IEEE, PNAS and Preprints. Nature/npj/Microsystems belong to Nature Portfolio; Cell/Neuron/Matter/Device belong to Cell Press rather than the separate Elsevier group. Biosensors and Bioelectronics and Sensors and Actuators A/B belong to Elsevier. Use the correct spellings IOP and Elsevier. Each group has a checkbox to select its entire family, including an indeterminate state; retain individual choices, global select/clear, publisher or journal search and Apply/Cancel. Keep all monitored sources listed, even with no papers in the current edition. Extend the mapping for newly monitored journals rather than silently assigning an incorrect publisher.

2026-10-23 author visibility: display the entire verified author list directly below each linked article title, without truncation or a disclosure control. Do not render a DOI line; retain DOI internally for matching/deduplication and the title's original-source link. Both server and browser renderers must agree. Preserve missing-author qualifications where necessary.
