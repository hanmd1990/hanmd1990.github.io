"""Build the public English literature archive from an explicit publication export."""
import copy,hashlib,json,re,datetime
from zoneinfo import ZoneInfo
from html import escape as esc
from pathlib import Path
from lxml import html

def rebuild_literature(root):
    folder=root/'data/literature'
    if not (folder/'index.json').exists():return
    index=json.loads((folder/'index.json').read_text())
    editions=[json.loads((folder/(key+'.json')).read_text()) for key in index['editions']]
    assert len({e['id'] for e in editions})==len(editions)
    for e in editions:
        assert len({a['id'] for a in e['articles']})==len(e['articles'])
        for a in e['articles']:
            assert a['url'].startswith('https://') and a['summary'] and a['topics']
            assert not re.search('[\u4e00-\u9fff]',json.dumps(a,ensure_ascii=False)),a['id']
    latest=next(e for e in editions if e['id']==index['latest'])
    header=copy.deepcopy(html.document_fromstring((root/'publications/index.html').read_bytes()).xpath('//header[contains(@class,"lab-header")]')[0])
    tree=html.document_fromstring('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DeepBioelectronics Beta — Mengdi Han Research Group</title><meta name="description" content="Weekly literature on wireless implants, magnetic systems, wearable devices, bioelectronics and micromechanical sensing."></head><body class="lab-literature-page"></body></html>')
    head=tree.find('head');body=tree.find('body');body.append(header)
    head.append(html.Element('link',rel='canonical',href='https://hanmd1990.github.io/literature/'))
    head.append(html.Element('link',rel='icon',href='/images/brand/site-icon.png'))
    for name in ('site.css','hmd-color.css','literature.css'):
        v=hashlib.sha256((root/'static'/name).read_bytes()).hexdigest()[:12]
        head.append(html.Element('link',rel='stylesheet',href='/static/'+name+'?v='+v))
    for name in ('site.js','literature.js','analytics.js'):
        v=hashlib.sha256((root/'static'/name).read_bytes()).hexdigest()[:12]
        head.append(html.Element('script',src='/static/'+name+'?v='+v,defer='defer'))
    main=html.fragment_fromstring('''<main class="literature-layout" id="literature-main"><header class="literature-intro"><h1>DeepBioelectronics <span class="lit-beta">Beta</span></h1><p>Recent research in wireless implants, magnetic systems, wearables and bioelectronics.</p><div class="lit-schedule"><strong>Automatic weekly updates</strong><p id="lit-schedule-times"></p><small>New York and London times adjust automatically for daylight saving time.</small></div></header><div class="literature-tools"><label class="lit-search">Search literature<input id="lit-search" type="search" placeholder="Title, author, journal or keyword" autocomplete="off"></label><label>Edition<select id="lit-edition"></select></label><div class="lit-journal-control"><span>Journals included</span><button type="button" id="lit-journals-open" aria-haspopup="dialog">All journals</button></div><label>Sort by<select id="lit-sort"><option value="relevance">Relevance</option><option value="date">Newest first</option><option value="journal">Journal</option></select></label><button id="lit-reset" type="button">Reset filters</button></div><p class="lit-topics-note">Topics are generated from recent reader preferences and refreshed with each weekly update.</p><div class="lit-topics" role="group" aria-label="Filter by topic"></div><div class="lit-status"><p id="lit-count" role="status" aria-live="polite"></p><p id="lit-window"></p></div><section id="lit-results" aria-label="Literature list"></section><p id="lit-empty" hidden>No articles match these filters. Try another keyword or reset the filters.</p><details class="lit-coverage"><summary>Sources and coverage</summary><p>The survey includes the journals and preprint sources listed below. Coverage varies by source and edition. Preprints have not been peer reviewed. Links open the original source.</p><p id="lit-note"></p><div id="lit-coverage-list"></div></details></main>''')
    body.append(main)
    # Server-render the upcoming schedule; the browser refreshes it in local DST rules.
    now=datetime.datetime.now(ZoneInfo('Asia/Shanghai'))
    friday=now.replace(hour=3,minute=30,second=0,microsecond=0)+datetime.timedelta(days=(4-now.weekday())%7)
    if friday<=now:friday+=datetime.timedelta(days=7)
    main.get_element_by_id('lit-schedule-times').text=' / '.join(friday.astimezone(ZoneInfo(z)).strftime('%A %H:%M')+' '+name for z,name in [('Asia/Shanghai','Beijing'),('America/New_York','New York'),('Europe/London','London')])
    dialog=html.fragment_fromstring('''<dialog id="lit-journals-dialog" aria-labelledby="lit-journals-title"><div class="lit-dialog-heading"><div><h2 id="lit-journals-title">Journals included</h2><p>Select one or more journals and preprint sources.</p></div><button id="lit-journals-close" type="button" aria-label="Close journal selection">×</button></div><label class="lit-journal-search">Find a journal<input type="search" id="lit-journals-search" placeholder="Search journal names"></label><div class="lit-dialog-actions"><button type="button" id="lit-journals-all">Select all</button><button type="button" id="lit-journals-none">Clear all</button><span id="lit-journals-selection" role="status" aria-live="polite"></span></div><div id="lit-journals-options"></div><div class="lit-dialog-footer"><button type="button" id="lit-journals-cancel">Cancel</button><button type="button" id="lit-journals-apply">Apply selection</button></div></dialog>''')
    body.append(dialog)
    select=main.get_element_by_id('lit-edition')
    for e in editions:
        opt=html.Element('option',value=e['id']);opt.text=e['id']
        if e==latest:opt.set('selected','selected')
        select.append(opt)
    def article(a):
        card=html.Element('article',{'class':'lit-paper','data-id':a['id']})
        meta=html.Element('p',{'class':'lit-meta'});j=html.Element('span',{'class':'lit-journal'});j.text=a['journal'];meta.append(j)
        date=html.Element('time',datetime=a['date']);date.text=a['date'];meta.append(date)
        card.append(meta)
        h=html.Element('h2');link=html.Element('a',href=a['url'],target='_blank',rel='noopener noreferrer');link.text=a['title'];h.append(link);card.append(h)
        summ=html.Element('p',{'class':'lit-summary'});summ.text=a['summary'];card.append(summ)
        bottom=html.Element('div',{'class':'lit-paper-bottom'})
        tags=html.Element('p',{'class':'lit-tags'});tags.text=' / '.join(a['topics']);bottom.append(tags)
        authors=html.Element('details',{'class':'lit-authors'});s=html.Element('summary');s.text='Authors and DOI';authors.append(s)
        p=html.Element('p');p.text='; '.join(a['authors']) if a['authors'] else 'Author list unavailable.'
        if not a.get('authorsComplete'):p.text+=' (Complete author list not verified.)'
        authors.append(p)
        if a.get('doi'):
            p=html.Element('p');p.text='DOI: '+a['doi'];authors.append(p)
        bottom.append(authors);card.append(bottom);return card
    listing=main.get_element_by_id('lit-results')
    for a in sorted(latest['articles'],key=lambda a:(-a['relevance'],a['journal'],a['title'])):listing.append(article(a))
    main.get_element_by_id('lit-count').text=f"{len(latest['articles'])} selected articles"
    main.get_element_by_id('lit-window').text=latest['start']+' – '+latest['end']+' (Beijing time)'
    main.get_element_by_id('lit-note').text=latest['note']
    coverage=main.get_element_by_id('lit-coverage-list')
    for c in latest['coverage']:
        p=html.Element('p');p.text=c['journal']+': '+c['status'];coverage.append(p)
    payload=html.Element('template',id='lit-data')
    payload.text=json.dumps({'latest':index['latest'],'editions':editions},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    body.append(payload)
    path=root/'literature/index.html';path.parent.mkdir(exist_ok=True);path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!doctype html>'))
    # Add the public page to shared navigation after all other generators finish.
    for path in root.rglob('index.html'):
        if any(p in path.relative_to(root).parts for p in ('tools','work','outputs','.git','.github')):continue
        t=html.document_fromstring(path.read_bytes())
        for nav in t.xpath('//header[contains(@class,"lab-header")]//nav[@id="lab-navigation"]'):
            for old in nav.xpath('./a[@href="/literature/"]'):nav.remove(old)
        for h in t.xpath('//header[contains(@class,"lab-header")]'):
            brand=h.xpath('.//a[contains(concat(" ",normalize-space(@class)," ")," lab-brand ")]')
            if not brand:continue
            for old in h.xpath('.//a[contains(concat(" ",normalize-space(@class)," ")," lab-radar-link ")]'):old.getparent().remove(old)
            b=brand[0]
            if b.getparent().get('class')=='lab-title-row':row=b.getparent()
            else:
                row=html.Element('div',{'class':'lab-title-row'});b.getparent().replace(b,row);row.append(b)
            a=html.Element('a',href='/literature/',attrib={'class':'lab-radar-link','aria-label':'DeepBioelectronics Beta — weekly literature'})
            a.text='DeepBioelectronics ';beta=html.Element('span');beta.text='Beta';a.append(beta)
            if path.parent.name=='literature':a.set('aria-current','page')
            row.append(a)
        path.write_bytes(html.tostring(t,encoding='utf-8',doctype='<!doctype html>'))
    print('Literature archive:',len(editions),'edition(s),',len(latest['articles']),'selected articles')
