# HMD Lab website — cloud handoff, updated 2026-10-15

Repository: https://github.com/hanmd1990/hanmd1990.github.io
Website: https://hanmd1990.github.io/
Latest website implementation before this documentation update: adbeff28d3f255e147050b3dfe6ede843154b7f5.

## Purpose of this handoff

Continue maintenance in a real Codex Cloud task bound to this GitHub repository, so work can resume from another computer. This is distinct from a general ChatGPT cloud conversation.
Check out the latest main branch rather than an older local snapshot. Do not replay old design requests: the current designs listed below have already been published and verified.
The complete original local chat history is not copied by selecting this environment. This file and the latest source are the durable handoff.

## Environment setup

Python 3.12 with lxml 5.3.0 and timezone data is sufficient for the static-site build. Node is optional for checking JavaScript syntax. No paid hosting service or new API key is required to build the website.
Install dependencies, then build a separate output folder using the same procedure as .github/workflows/publish.yml:
mkdir -p outputs/hmd-lab-site
git archive HEAD | tar -x -C outputs/hmd-lab-site --exclude='.github' --exclude='work' --exclude='tools' --exclude='.gitignore' --exclude='README.md'
python tools/build_site.py outputs/hmd-lab-site
python tools/verify_site.py outputs/hmd-lab-site
Do not mistake editable source HTML in the repository for the final rendered site: the GitHub Pages workflow runs tools/build_site.py before publishing.

For Current membership edits, change data/member-publications.json, regenerate with python tools/build_member_preview.py . --publish, then run the main builder. The member generator imports tools/member_gallery.py. The main builder imports tools/alumni_layout.py.
Build member pages before the main builder so shared citation data is injected. Avoid broad unnecessary regeneration of unrelated editable source files.

## Completed design and content — preserve

- The website and images are independent of the original platform. Do not reintroduce original-platform asset dependencies.
- DNS and migration of hmd-lab.com are deferred. Do not change the domain or its Aliyun DNS.
- HMD palette: navy #142B55, gold #A1662F, text #252A34, medium blue #547DA6, light gray #EFF1F5, pale yellow #F9DF93, white #FFFFFF, black #000000.
- Article links hover medium blue; all other links hover gold.
- No Copyright © 2021 footer or Chinese ICP footer is displayed. Current also has no group name/affiliation/check-date footer.
- Home and every Research page have no citation badges. Preserve their article links, journal information and hover colors.
- Publication and News enter at the current year; decade navigation uses 2020s/2010s. Publication year typography and top alignment are consistent. Full List automatically aggregates all year pages. Preserve Covers and Scholar profile buttons.
- Current has 21 equally weighted text member cards with no individual portraits or large role-group headings. Role is small text after the English name. English university comes next, then Chinese name/university on the next line. No school-label prefixes.
- Mengdi Han: “Principle Investigator” as explicitly requested; Peking University / 北京大学; no PI publication disclosure.
- Yujie Shang: Visiting Student, Nanjing University of Aeronautics and Astronautics / 南京航空航天大学. Other undergraduates are at Peking University.
- Xiaowen Zhang / 张晓雯 was removed from Current. Penglai Yao / 姚朋来 and Junjie Wang / 王俊洁 were appended as Peking University undergraduates.
- Current Selected Publications include only verified first/co-first-author research papers and reviews, ordered exactly as Full List. Article text is 14px. Display all source author tokens carrying ¹ before et al.; otherwise display the first author. Preserve source journal/year/volume/page or article number and Scholar badges.
- Editorial 104 is excluded from member selections only, not the global bibliography. Do not omit Yiran Wang’s 88 (Materials Today Physics) or Zhongyi Nie’s 114 (Advanced Materials review). Never infer a person from ambiguous initials. Empty member disclosures show only a hyphen.
- Current right sidebar is a compact album: one full-resolution image, caption/date, Previous/Next, and a 16-image thumbnail index with abbreviated dates (e.g. Dec. 2023). The main image uses contain and white background, not gray letterboxing. Source captions and images are recorded in data/group-photos.json. Keep the album shorter than the member list. Member styles receive a content-hash cache version in the main builder.
- Alumni has 7 expandable profiles and 12 original selected publications. Left: Education (school, previous degree, major). Center: English/Chinese name, role and years in group, Selected Publications toggle. Right: Next role. Center occupies about half the width, with 24px semi-bold English names; side columns are narrower and secondary. Do not revert to equal-width columns.
- Contact email is plain hmd[at]pku.edu.cn, no mailto link. “Mailing address” heading is removed, while the full address remains. Profiles & resources icons visually blend with the gray background using CSS mix-blend-mode: multiply. Preserve maps and all resource links.
- Join Us redesign is ONLY a preview at /preview/join-us/. Keep original recruitment content, dates and availability unchanged. Do not replace the official /join/ page without further user approval.
- Preserve the Home smooth translucent-dot carousel, hover dropdown navigation and Covers gallery.

## Scholar data and existing weekly automation

Scholar profile: https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en
data/scholar-citations.json is the shared data cache. Its profile_metrics, verified on 2026-10-14, contains total_citations 15699, h_index 64, i10_index 120. Render the actual Google Scholar All-column totals, not a sum of listed papers.
Publication statistics caption is “Citation counts: Google Scholar · automatically updated YYYY-MM-DD”. Do not advance the date after an unsuccessful check.
Citations are displayed on Publications, Full List, Current, Alumni and Covers, but never on Home or Research.
An independent Alumni article not in the PI profile is explicitly matched: “A flexible hybridized electromagnetic-triboelectric nanogenerator and its application for 3D trajectory sensing”, Nano Energy 2020, 74, 104878. Google Scholar cluster/cites ID 2204454159587458542; verified 85 citations on 2026-10-14. Keep that article’s own Scholar count/link and do not replace it with another database’s count. It is also listed in data/scholar-extra-articles.json.
An existing heartbeat automation named “每周更新 HMD Lab 论文”, id hmd-lab, is attached to the original local task and scheduled Mondays 09:00 Asia/Shanghai. Its instructions include weekly profile metrics, all-year citation counts and independent Alumni articles. New publication additions concern 2026 onward; preserve older entries and conference papers. Do not create a duplicate automation.
That existing local automation has not been migrated to a cloud environment. Its local computer availability and any future migration must be considered separately; creating a cloud coding task does not migrate the schedule.

## Remaining implementation task: private analytics

User requested a separate private login-protected dashboard with site total pageviews and visits, IP addresses, approximate country/region/city, timestamps, visited pages, per-browser visit number, trends, and export.
Cloudflare was chosen for the backend; the public website stays on GitHub. No domain/DNS migration is authorized. No paid service may be enabled without cost approval.
No Worker, database, Access application, dashboard, or tracker has been implemented or deployed yet. No historic visitor logs are available.
Prepare the backend, dashboard, tests and reviewable deployment configuration. Use real server-side authorization; a secret URL or front-end password check is not enough. Keep visitor logs and secrets out of this public repository.
IP location is approximate, not a street address; an IP may be shared or change. Use anonymous browser identifiers/session rules for repeat visits, without pretending they uniquely identify a person. Counts start when tracking is enabled.
The original local browser was logged in to Cloudflare, but its cookies and sign-ins must not be copied. Request an appropriate interactive login only if deployment needs it; never request passwords/OTP in chat.

## Authorization and reporting

User authorized necessary website edits, testing and main-branch publication. Keep each requested preview isolated where specified. Before pushing, read the latest remote head and avoid overwriting concurrent work; compare-and-swap updates are preferred.
Report results in Chinese. Verify builds, resource links, relevant browser behavior and deployment success. Do not claim an account/environment/task exists merely because a creation request was issued.
