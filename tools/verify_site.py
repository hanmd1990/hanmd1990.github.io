"""Fail on missing assets or unapproved third-party runtime dependencies."""
import json,re,sys
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from lxml import html
ROOT=Path(sys.argv[1]).resolve()
errors=[]; count=0
urls=re.compile(r'url\(\s*([\"\']?)(.*?)\1\s*\)',re.I)
def check(raw,file,kind='asset'):
    if not raw or raw.startswith(('data:','#','mailto:','tel:')):return
    u=urlparse(urljoin('https://hanmd1990.github.io/'+file.relative_to(ROOT).as_posix(),raw))
    if re.search(r'(?:sxlcdn|strikingly|sxl\.cn|sxldns|hmd-lab\.com)',u.netloc,re.I):
        errors.append(f'{file.relative_to(ROOT)}: legacy platform link {raw}')
    if u.netloc!='hanmd1990.github.io':
        if kind=='asset':errors.append(f'{file.relative_to(ROOT)}: external resource {raw}')
        return
    p=ROOT/unquote(u.path.lstrip('/'))
    if p.is_dir():p=p/'index.html'
    if not p.is_file():errors.append(f'{file.relative_to(ROOT)}: missing {raw}')
for f in ROOT.rglob('*'):
    if any(x in f.relative_to(ROOT).parts for x in ('.git','.github','work','outputs','tools','analytics')):continue
    if f.suffix=='.html':
        count+=1;t=html.document_fromstring(f.read_bytes())
        for e in t.iter():
            if not isinstance(e.tag,str):continue
            for a in ('src','poster','data','background'):
                if e.get(a):check(e.get(a),f)
            if e.get('srcset'):errors.append(f'{f}: srcset needs explicit verification')
            if e.tag=='link' and e.get('rel')!='canonical':check(e.get('href'),f)
            if e.tag=='a':check(e.get('href'),f,'link')
            if e.tag=='form':errors.append(f'{f}: form requires an independent backend')
            s=e.get('style','')+((e.text or '') if e.tag=='style' else '')
            for m in urls.finditer(s):check(m[2],f)
            if e.tag=='script' and not e.get('src') and re.search(r'fetch\s*\(|XMLHttpRequest|https?://',e.text or ''):errors.append(f'{f}: external inline script')
        if re.search(r'(?:https?:)?//[^\s"<>]*(?:sxlcdn|strikingly|sxl\.cn|sxldns)',f.read_text(encoding='utf-8')):errors.append(f'{f}: legacy platform URL')
    elif f.suffix=='.css':
        s=f.read_text(encoding='utf-8')
        for m in urls.finditer(s):check(m[2],f)
        if re.search(r'@import',s):errors.append(f'{f}: CSS import requires verification')
    elif f.suffix=='.js':
        script=f.read_text(encoding='utf-8')
        # Requested Apple Maps enhancement; an explicitly approved remote SDK.
        # The empty-token and failure paths retain the local campus map.
        if f.relative_to(ROOT).as_posix()=='static/contact-map.js':
            script=script.replace('https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js','')
        # Owner-authorized GA4 and Baidu tags; production host only, opt-outs respected.
        if f.relative_to(ROOT).as_posix()=='static/analytics.js':
            for approved in ('https://www.googletagmanager.com/gtag/js?id=',
                             'https://policies.google.com/technologies/partner-sites',
                             'https://hm.baidu.com/hm.js?e387d8beff78853986f3b7b31860f890'):
                script=script.replace(approved,'')
        # Owner-requested account login and private sync; official version-pinned SDK.
        if f.relative_to(ROOT).as_posix()=='static/literature-account.js':
            script=script.replace('https://www.gstatic.com/firebasejs/13.1.0/','')
        if re.search(r'fetch\s*\(|XMLHttpRequest|https?://',script):errors.append(f'{f}: remote script dependency')
report={'checked_html_pages':count,'errors':sorted(set(errors))}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
