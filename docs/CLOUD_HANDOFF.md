# Website maintenance handoff — 2026-10-14

Repository: https://github.com/hanmd1990/hanmd1990.github.io
Live website: https://hanmd1990.github.io/
Last website change before this handoff: 307509d925f85ab82904efde8df870d19cf38ac7.

## Build and source

This repository is the independent static website, with local images and assets. Do not reintroduce dependencies on the original platform. Do not change DNS or the hmd-lab.com domain; domain migration is deferred.
The root is the editable site. Install Python lxml and tzdata if necessary.
- tools/build_site.py rebuilds archive navigation, full publication lists, shared citations, and other pages. Run python tools/build_site.py .
- tools/build_member_preview.py reads data/member-publications.json and publication year pages. Run python tools/build_member_preview.py . --publish to regenerate both preview/current-members/index.html and the official current/index.html; then run the main builder.
- tools/verify_site.py checks local resource paths and internal links. Run python tools/verify_site.py .
- static/hmd-color.css is the global palette; static/member-preview.css styles both the official and preview member page.
- data/scholar-citations.json holds Scholar counts and links. Unknown citations must remain unknown, never fake zero.
- data/member-publications.json contains verified full-name author identities and member roles.
- data/group-photos.json preserves original photo captions, dates, thumbnail paths, and full-resolution paths. All files already exist locally in images/people/current/.

## Latest requested change — not yet implemented

Update the official /current/ page directly; publishing is authorized.
1. Remove “Undergraduate school:” and “Ph.D. school:” prefixes. Preserve university names and the English-first, Chinese-next-line format.
2. Improve right-side Group Photos layout and typography. Current page uses 300x300 thumbnails. Use the full-resolution image paths in data/group-photos.json (approximately 1700–1920 pixels wide), retain their native proportions, restore each original caption and date, and allow clicking for a large image. There are 16 photos.
3. Harmonize page typography with Publications and News (their main body is roughly 15.5px), keeping reasonable compactness and readable names/roles. The current 11–12px secondary text is too small.
4. Verify desktop/mobile layout, image quality, all local resources, paper disclosures, and deploy. Preserve everyone’s equal visual weight and no individual portraits.

## Member constraints to preserve

20 members in one uniform list, no large PI/Postdoc/PhD category headings; role appears as smaller text next to the English name.
Mengdi Han role is “Principle Investigator” as explicitly requested, affiliation Peking University / 北京大学; no PI publication list.
Yujie Shang is Visiting Student, Nanjing University of Aeronautics and Astronautics / 南京航空航天大学. Other five undergraduates are Peking University.
Article disclosures read “Selected Publications”. Include only verified first/co-first-author research papers and reviews. Paper 104 is editorial and excluded from member selections, but remains in the global bibliography.
Preserve Yiran Wang’s paper 88 (Materials Today Physics) and Zhongyi Nie’s paper 114 (Advanced Materials review). Existing identity confirmation is stored in data.
Display all source author tokens carrying ¹ before “et al.” (otherwise the first author), journal/year/volume/page or article number from the original bibliography, and Scholar citation badges.
Do not infer identities from ambiguous initials. Do not invent issue numbers or silently change historical publication years.

## Private analytics task — not yet implemented or deployed

User requests a separate private, login-protected dashboard with pageviews/total visits, IPs, approximate location, per-visitor visit number, timestamps, visited pages, trends, and export.
User has chosen Cloudflare for the backend; main website stays on GitHub. No tracker, database, Worker, dashboard, or Access application has been created.
A Cloudflare login was completed on the original local computer, but that browser session cannot be assumed available in a cloud task or on another computer. Do not copy credentials/cookies.
Build and review the service before requesting unavoidable login/setup steps. Use an appropriate Cloudflare backend/database and real server-side authorization; a hidden URL or front-end password is insufficient. Keep visitor logs and secrets out of this public repository.
Count browser visits using an anonymous identifier and session rules; IPs can be shared or change and are not exact identities. Location is approximate, not a street address. Counts begin at deployment, not retroactively.
Do not start paid services without explicit cost authorization.

## Other established design and behavior

HMD palette: navy #142B55, gold #A1662F, text #252A34, medium blue #547DA6, light gray #EFF1F5, pale yellow #F9DF93, white #FFFFFF, black #000000.
Only publication/article links hover medium blue; other links hover gold. Keep navigation colors consistent.
Publication/News entry opens current year. Decade navigation labels 2020s, 2010s, consistent size/top alignment; Full List automatically aggregates all year pages. Publications includes Covers and Scholar profile actions.
Full site currently has 42 HTML pages, 126 listed publications, shared Scholar citation data, independently hosted local assets.
Preserve existing Alumni/Join disclosures, Contact layout/icons/map, Covers gallery, smooth Home carousel dots, and hover dropdown navigation.
A weekly Scholar update was configured on the original host. Do not create a duplicate schedule without checking existing automation. Article additions concern years after 2025; older conference entries should not be imported. Citation counts may refresh across all years.
