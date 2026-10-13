"""Build archive navigation and full lists from editable year pages. No network."""
import copy,datetime,hashlib,json,re,sys
from pathlib import Path
from zoneinfo import ZoneInfo
from lxml import html

ROOT=Path(sys.argv[1]).resolve()
color_version=hashlib.sha256((ROOT/'static/hmd-color.css').read_bytes()).hexdigest()[:12]
today=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).year
def read(path):return html.document_fromstring(path.read_bytes())
def write(path,tree):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!DOCTYPE html>'))
def years(kind):
    return sorted([int(p.parent.name[len(kind):]) for p in ROOT.glob(kind+'*/index.html') if re.fullmatch(kind+r'\d{4}',p.parent.name)],reverse=True)
pub_years=years('publications');news_years=years('news')
assert pub_years and news_years,'Year pages are required'
def current(ys):return today if today in ys else next((y for y in ys if y<=today),ys[0])
def text(e):return ' '.join(''.join(e.itertext()).split())
def paper_id(e):
    m=re.match(r'^\((\d+)\)',text(e));return int(m[1]) if m else None
def paper_wrapper(tree):
    candidates=[e for e in tree.xpath('//div[@class="s-rich-text-wrapper"]') if any(paper_id(c) for c in e)]
    assert len(candidates)==1,'Expected one publication content block'
    return candidates[0]
def slides(tree):
    return tree.xpath('//ul[contains(concat(" ",normalize-space(@class)," ")," slides ")]')[0]

# Publication year pages are the sole source of the full list.
pub=read(ROOT/f'publications{pub_years[0]}/index.html')
destination=paper_wrapper(pub);destination.clear();destination.set('class','s-rich-text-wrapper');destination.set('style','display:block')
legend=html.Element('p',{'class':'lab-publication-legend'});legend.text='*Corresponding authors; ¹Authors contributed equally';destination.append(legend)
paper_ids=[];counts={}
for year in pub_years:
    source=paper_wrapper(read(ROOT/f'publications{year}/index.html'))
    elements=list(source);start=next(i for i,e in enumerate(elements) if paper_id(e))
    heading=html.Element('h2',id='year-'+str(year),attrib={'class':'lab-year-heading'});heading.text=str(year);destination.append(heading)
    n=0;previous_blank=False
    # Preserve titles, authors, journal details, notes, links and images together.
    for element in elements[start:]:
        pid=paper_id(element)
        if pid:paper_ids.append(pid);n+=1
        blank=not text(element) and not element.xpath('.//img')
        if blank and previous_blank:continue
        destination.append(copy.deepcopy(element));previous_blank=blank
    while len(destination) and not text(destination[-1]) and not destination[-1].xpath('.//img'):destination.remove(destination[-1])
    counts[str(year)]=n
assert len(paper_ids)==len(set(paper_ids)),'Duplicate publication numbers across year pages'
write(ROOT/'all/index.html',pub)

# News full list preserves complete sections, including their photographs.
news=read(ROOT/f'news{news_years[0]}/index.html');target=slides(news)
for child in list(target):target.remove(child)
style_texts={e.text for e in news.xpath('//style')}
for year in news_years:
    source=read(ROOT/f'news{year}/index.html')
    for style in source.xpath('//style'):
        if style.text not in style_texts:news.find('head').append(copy.deepcopy(style));style_texts.add(style.text)
    for section in slides(source):
        section=copy.deepcopy(section)
        for element in section.iter():
            if element.get('id'):element.set('id','news-'+str(year)+'-'+element.get('id'))
        section.set('id','year-'+str(year));target.append(section)
write(ROOT/'news-all/index.html',news)

# Stable entry links open the current calendar year when available.
for kind,ys in [('publications',pub_years),('news',news_years)]:
    write(ROOT/kind/'index.html',read(ROOT/f'{kind}{current(ys)}/index.html'))

def archive_nav(kind,active):
    ys=pub_years if kind=='publications' else news_years
    nav=html.Element('nav',{'class':'lab-archive-nav','aria-label':kind.capitalize()+' years'})
    year_rows=html.Element('div',{'class':'lab-archive-years'})
    for decade in sorted({year//10*10 for year in ys},reverse=True):
        group=[year for year in ys if year//10*10==decade]
        row=html.Element('div',{'class':'lab-decade-row','data-decade':str(decade),'aria-label':f'{decade}s'})
        row.set('style',f'--year-count:{len(group)}')
        label=html.Element('span',{'class':'lab-decade-label'});label.text=f'{decade}s';row.append(label)
        for year in group:
            a=html.Element('a',href=f'/{kind}{year}/');a.text=str(year)
            if active==str(year):a.set('aria-current','page')
            row.append(a)
        year_rows.append(row)
    nav.append(year_rows)
    actions=html.Element('div',{'class':'lab-archive-actions'})
    primary=html.Element('div',{'class':'lab-archive-action-row'})
    for label,route in [('Full List','all' if kind=='publications' else 'news-all')]+([('Covers','covers')] if kind=='publications' else []):
        a=html.Element('a',href='/'+route+'/',attrib={'class':'lab-archive-feature'});a.text=label
        if active==route:a.set('aria-current','page')
        primary.append(a)
    actions.append(primary)
    if kind=='publications':
        secondary=html.Element('div',{'class':'lab-archive-action-row'})
        scholar=html.Element('a',href='https://scholar.google.com/citations?user=rjC8MUQAAAAJ&hl=en',target='_blank',rel='noopener noreferrer',attrib={'class':'lab-archive-feature lab-scholar-link'});scholar.text='Google Scholar Profile';secondary.append(scholar);actions.append(secondary)
    nav.append(actions)
    if kind=='publications' and active!='covers':
        note=html.Element('p',{'class':'lab-publication-legend'});note.text='* Corresponding authors; ¹ Authors contributed equally';nav.append(note)
    return nav

for path in ROOT.rglob('index.html'):
    if any(p in path.relative_to(ROOT).parts for p in ('tools','work','outputs','.git','.github')):continue
    tree=read(path);route=path.parent.relative_to(ROOT).as_posix()
    for em in tree.xpath('//*[@id="s-content"]//p//em'):
        if re.fullmatch(r'\d+(?:[.\-–]\d+)?',text(em)):
            em.set('class',(em.get('class','')+' lab-volume').strip())
    for heading in tree.xpath('//h1|//h2|//h3|//h4|//h5|//h6'):
        if 'representative publication' in text(heading).lower():
            wrapper=next((a for a in heading.iterancestors() if a.tag=='div' and a.get('class')=='s-rich-text-wrapper'),None)
            if wrapper is not None:
                for link in wrapper.xpath('.//a[@href]'):link.set('class',(link.get('class','')+' lab-publication-link').strip())
    for menu in tree.xpath('//header[contains(@class,"lab-header")]//details'):
        label=text(menu.find('summary')).replace('⌄','').strip().upper()
        if label not in ('PUBLICATIONS','NEWS'):continue
        a=html.Element('a',href='/'+label.lower()+'/');a.text=label;menu.getparent().replace(menu,a)
    kind=None;active=None
    if re.fullmatch(r'publications\d{4}',route):kind='publications';active=route[len(kind):]
    elif re.fullmatch(r'news\d{4}',route):kind='news';active=route[4:]
    elif route in ('publications','news'):kind=route;active=str(current(pub_years if kind=='publications' else news_years))
    elif route in ('all','covers'):kind='publications';active=route
    elif route=='news-all':kind='news';active=route
    if kind:
        body=tree.find('body');body.set('class',(body.get('class','')+' lab-archive-page '+('lab-news-page' if kind=='news' else 'lab-publications-page')).strip())
        for old in tree.xpath('//nav[contains(@class,"lab-archive-nav")]'):old.getparent().remove(old)
        header=tree.xpath('//header[contains(@class,"lab-header")]')[0]
        header.addnext(archive_nav(kind,active))
        title=tree.find('head/title')
        if title is not None:title.text=('Publications' if kind=='publications' else 'News')+' — '+('Full List' if active in ('all','news-all') else 'Covers' if active=='covers' else active)+' — Mengdi Han Research Group'
        for meta in tree.xpath('//meta[@property="og:url"]'):meta.set('content','https://hanmd1990.github.io/'+route+'/')
        for canonical in tree.xpath('//link[@rel="canonical"]'):canonical.set('href','https://hanmd1990.github.io/'+route+'/')
        # Avoid a duplicate Covers link left from the old archive layout.
        for heading in tree.xpath('//h5[.//a[contains(@href,"scholar.google.com")]]'):
            heading.getparent().remove(heading)
        for note in tree.xpath('//*[@id="s-content"]//h5|//*[@id="s-content"]//p'):
            if 'Corresponding authors' in text(note) and 'Authors contributed equally' in text(note):note.getparent().remove(note)
    for stylesheet in tree.xpath('//link[starts-with(@href,"/static/hmd-color.css")]'):
        stylesheet.getparent().remove(stylesheet)
    tree.find('head').append(html.Element('link',rel='stylesheet',href='/static/hmd-color.css?v='+color_version))
    write(path,tree)

report={'current_year':today,'publications_entry_year':current(pub_years),'news_entry_year':current(news_years),'publication_years':pub_years,'news_years':news_years,'publication_counts':counts,'total_publications':len(paper_ids)}
(ROOT/'archive-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))

