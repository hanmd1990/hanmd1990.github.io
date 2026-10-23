# Literature retrieval and recovery

## Verified failure modes

On 2026-10-23 the Science ToC and RSS returned HTTP 403. Cell and ScienceDirect routes returned HTTP 200 with a 195-byte “Site Unavailable” page. IEEE responses varied between a page response and HTTP 418. These are access failures, not evidence of an empty weekly issue. Crossref and Europe PMC public APIs returned usable journal metadata without API keys or a subscription. Some Crossref requests returned 429; honor Retry-After and back off. Do not bypass authentication, CAPTCHAs, rate limits or publisher access controls.

Some deposits have only a month-level issue date and no published-online field. An online-date-only query therefore misses new records. A DOI registration/created date can discover such records but cannot establish when the article was published. Search-engine crawl dates, DOI suffix years, acceptance dates and future print issue dates are not substitutes for the first-online date.

## Workflow

1. Read the latest Journal list in Drive without editing it. Reconcile names and links with `data/literature-sources.json`. This registry covers affected journals; it does not replace the authoritative journal list or imply the other journals should be skipped. Verify any added ISSN against an official journal source. The collector rejects returned Crossref container titles that do not match the configured journal. Fix Nature Protocols to its own official source, never the accidental Nature Photonics link.
2. Try the publisher's current issue AND online-first/archive or dated article list. Validate the content, not just the status code: an “Unavailable”, sign-in, challenge or empty JavaScript shell does not count as a catalogue. Save the checked URL, time, status and limitation. Use supported web retrieval for official HTML/PDF when direct retrieval fails; do not treat search results as an exhaustive issue.
3. Use the collector as a second route. It queries Crossref by online publication, general publication and recent registration with a 21-day discovery lookback; it also queries Europe PMC by journal ISSN and FIRST_PDATE. Cursor pagination must be exhausted; incomplete pagination is reported as a failure. Crossref/Europe PMC indexing can lag. A future run must recheck the lookback and compare its candidates with the published DOI ledger, so late-indexed papers are not silently lost. Classify confirmed older omissions as a dated delayed supplement, not as newly published this week.
4. Review candidates. Only a day-resolved first-online/posted date inside the reporting window qualifies on date alone; either cutoff day still needs time verification for the 03:30 Asia/Shanghai half-open window. Unknown/month-only dates and conflicting dates stay pending. `reported_date`, Crossref created/issued dates and Europe PMC dateOfCreation are discovery/context only. Europe PMC electronicPublicationDate and publisher HTML/PDF can verify an online date. Check whether an earlier online-first version exists before treating a print appearance as new.
5. Author metadata is preserved in full order, including collective authors. The collector does not expand initials. Prefer full given names from Crossref or the structured Europe PMC author list, and verify gaps against the publisher. Never replace complete names with initials. Abstracts in the intermediate file are for editorial review only: write original concise summaries, do not publish raw abstracts. Apply the existing relevance policy; do not silently replace the complete report with a keyword Top 10.
6. Science editor credits: Crossref/NLM metadata often lacks handling editors. Check official article HTML or PDF, including the editorial summary where available. Missing editor metadata does not mean the editor was not Marc Lavine. If credits remain inaccessible, report that this special inclusion rule could not be fully verified; do not claim every Marc Lavine article was found. Keep editor names off the public article cards and chat recommendations, as requested.
7. Research Square has a usable Crossref prefix endpoint. Use posted-date filters and cursor pagination, deduplicate DOI/version relations, and mark all candidates as preprints, not peer reviewed. Prefix 10.21203 covers Research Square generally, NOT just Nature Portfolio. Its broad recovery candidates need independent Nature Portfolio submission/category evidence before claiming that filter. Never infer acceptance, peer review or portfolio membership from the platform name.
8. Update the public edition only after relevance/content/date review and DOI deduplication. Recovered metadata can change a source from unavailable to partial, but does not justify complete. The health report distinguishes records recovered from date-verified candidates. Zero recovered records remains unverified coverage, not “no new papers”. Keep original coverage qualifications until actually resolved.

## Commands

Run from the repository root, with the scheduled cutoff days:

```bash
python tools/collect_literature_metadata.py --start 2026-10-16 --end 2026-10-23 --output /tmp/literature-candidates.json --health-output /tmp/literature-health.json
python tools/test_literature_metadata.py
```

Repeat `--journal 'Device'` to select sources. Dates above are examples, not a fixed run window. Output candidates are intermediate files that may contain full abstracts; keep them out of the public repository and website. A reviewed source-health report with counts, public source URLs and limitations may be committed. Do not publish private interest feedback or unpublished comparisons.

## Public API references

- Crossref REST filters: https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/
- Crossref pagination and date queries: https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/
- Europe PMC REST API: https://europepmc.org/RestfulWebService
- PubMed date fields and API limits: https://www.ncbi.nlm.nih.gov/books/NBK25499/

This is a public-metadata fallback, not a subscription full-text downloader. No new paid service, user login or private report API is needed.

## Reading-count audit and source overrides — 2026-10-23

The registry now covers the monitored journal sources plus Research Square; arXiv and bioRxiv use their own public APIs. Small is excluded by owner instruction, even if still present in the read-only Drive sheet. The journal selector shows reads and selected entries separately. Use `weekly_read_counts` on deduplicated recovery candidates. Count only retrieved records with a day-resolved publication field in the edition window; retain online/first-publication versus reported issue-date evidence and do not turn a count into permission to publish an unverified first-online date. Day-only cutoff records and month-only records remain pending. Existing verified selected entries establish a lower bound, not a complete survey. Preserve per-source read-count evidence and update counters every run.

arXiv API queries use the precise converted UTC cutoff and verify every entry's published timestamp. bioRxiv's `details/biorxiv/START/END/CURSOR/json?category=bioengineering` endpoint was tested with category verification and pagination (30 records per page in this response). Filter version 1 and deduplicate DOI; exclude uncertain cutoff-day records or retain an explicit lower bound. Category totals include updated versions, so do not treat `total` as a new-paper count. Nature Protocols is 1750-2799 online (1754-2189 print); its monitored official path is `/nprot/`, not `/nphoton/`.

The Research Square Nature Portfolio filtered URL returned HTTP 403 on 2026-10-23; the connected-browser attempt timed out. Platform Crossref records remain usable for discovery, but the filtered count is unverified and must be shown as —. Do not claim the filtered browse page was read successfully.
