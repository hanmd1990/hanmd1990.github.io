"""Build archive navigation and full lists from editable year pages. No network."""
import copy,datetime,hashlib,json,re,sys,unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlparse,quote
from lxml import html

ROOT=Path(sys.argv[1]).resolve()
color_version=hashlib.sha256((ROOT/'static/hmd-color.css').read_bytes()).hexdigest()[:12]
script_version=hashlib.sha256((ROOT/'static/site.js').read_bytes()).hexdigest()[:12]
today=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).year
citations_path=ROOT/'data/scholar-citations.json'
citations=json.loads(citations_path.read_text(encoding='utf-8')) if citations_path.exists() else {'records':{},'checked_on':None}
def title_key(s):return ''.join(c for c in unicodedata.normalize('NFKC',s).casefold() if c.isalnum())
def citation_record(link):
    doi=re.search(r'10\.\d{4,9}/[^?#]+',link.get('href',''),re.I)
    if doi:
        found=citations['records'].get('doi:'+doi[0].rstrip('/').lower())
        if found:return found
    return citations['records'].get(title_key(text(link)))
def read(path):return html.document_fromstring(path.read_text(encoding='utf-8'))
def write(path,tree):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(html.tostring(tree,encoding='utf-8',doctype='<!DOCTYPE html>'))
def years(kind):
    return sorted([int(p.parent.name[len(kind):]) for p in ROOT.glob(kind+'*/index.html') if re.fullmatch(kind+r'\d{4}',p.parent.name)],reverse=True)
pub_years=years('publications');news_years=years('news')
assert pub_years and news_years,'Year pages are required'
def paper_key(href):
    doi=re.search(r'10\.\d{4,9}/[^?#]+',href,re.I)
    return 'doi:'+doi[0].rstrip('/').lower() if doi else href.split('?')[0].rstrip('/')
publication_index={}
for year in pub_years:
    for p in read(ROOT/f'publications{year}/index.html').xpath('//p'):
        if not re.match(r'^\(\d+\)',p.text_content().strip()):continue
        links=p.xpath('.//a[@href]')
        if not links:continue
        journal='';following=p.getnext()
        for _ in range(3):
            if following is None:break
            for em in following.xpath('.//em'):
                value=' '.join(em.text_content().split())
                if value and not re.fullmatch(r'et\s*al\.?|\d+',value,re.I):journal=value;break
            if journal:break
            following=following.getnext()
        publication_index[paper_key(links[0].get('href'))]={'title':' '.join(links[0].text_content().split()),'journal':journal,'year':year}
def current(ys):return today if today in ys else next((y for y in ys if y<=today),ys[0])
def text(e):return ' '.join(''.join(e.itertext()).split())
def add_class(e,name):
    classes=e.get('class','').split()
    if name not in classes:classes.append(name)
    e.set('class',' '.join(classes))
def article_link(href):
    u=urlparse(href);host=(u.hostname or '').lower();path=u.path
    if '/doi/toc/' in path:return False
    if re.search(r'/doi/(?:abs/|full/|epdf/|pdf/)?10\.\d{4,9}/',path):return True
    if host in ('doi.org','dx.doi.org') and path.startswith('/10.'):return True
    return any(host.endswith(domain) and re.search(pattern,path) for domain,pattern in [
        ('nature.com',r'^/articles/[^/]+'),('sciencedirect.com',r'/science/article/'),
        ('link.springer.com',r'/article/'),('pnas.org',r'^/content/\d+/'),
        ('ieeexplore.ieee.org',r'^/document/\d+'),('pubmed.ncbi.nlm.nih.gov',r'^/\d+'),
        ('ieeexplore.ieee.org',r'^/stamp/stamp.jsp'),('iopscience.iop.org',r'^/article/'),
        ('pubs.rsc.org',r'/content/articlelanding/'),('cambridge.org',r'/core/journals/.*/article/'),
        ('frontiersin.org',r'/articles/10\.'),('mdpi.com',r'^/\d{4}-\d{4}/\d+/\d+/\d+'),
        ('academic.oup.com',r'/article/'),('pubs.aip.org',r'/article/')])
def paper_id(e):
    m=re.match(r'^\((\d+)\)',text(e));return int(m[1]) if m else None
def paper_wrapper(tree):
    candidates=[e for e in tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," s-rich-text-wrapper ")]') if any(paper_id(c) for c in e)]
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
        if citations.get('checked_on'):
            note=html.Element('p',{'class':'lab-citation-updated'});note.text='Citation counts: Google Scholar · updated '+citations['checked_on'];nav.append(note)
    return nav

for path in ROOT.rglob('index.html'):
    if any(p in path.relative_to(ROOT).parts for p in ('tools','work','outputs','.git','.github')):continue
    tree=read(path);route=path.parent.relative_to(ROOT).as_posix()
    for old in tree.xpath('//*[contains(concat(" ",@class," ")," lab-citation-badge ")]'):old.getparent().remove(old)
    page_class={'.':'lab-home-page','current':'lab-current-page','alumni':'lab-alumni-page','bio':'lab-bio-page','contact':'lab-contact-page','join':'lab-join-page'}.get(route)
    if page_class:add_class(tree.find('body'),page_class)
    for link in tree.xpath('//a[@href]'):
        link.set('class',' '.join(c for c in link.get('class','').split() if c!='lab-publication-link'))
        if not route.startswith('news') and route!='covers' and text(link).lower() not in ('cover','covers') and (link.get('data-link-kind')=='article' or article_link(link.get('href'))):add_class(link,'lab-publication-link')
    if re.fullmatch(r'publications\d{4}',route) or route in ('publications','all'):
        content=paper_wrapper(tree);add_class(content,'lab-publication-body')
        while len(content) and not text(content[0]) and not content[0].xpath('.//img'):content.remove(content[0])
        for year in content.xpath('./p|./h4|./h5|./h6'):
            if re.fullmatch(r'\d{4}',text(year)):
                year.tag='h2';year.attrib.pop('style',None);add_class(year,'lab-content-year')
                following=year.getnext()
                if following is not None and not text(following) and not following.xpath('.//img'):content.remove(following)
        for paragraph in tree.xpath('//*[@id="s-content"]//p'):
            links=paragraph.xpath('.//a[@href]')
            if paper_id(paragraph) and links:add_class(links[0],'lab-publication-link')
    for em in tree.xpath('//*[@id="s-content"]//p//em'):
        if re.fullmatch(r'et\s*al\.?',text(em),re.I):add_class(em,'lab-author-note')
        if re.fullmatch(r'\d+(?:[.\-–]\d+)?',text(em)):
            em.set('class',(em.get('class','')+' lab-volume').strip())
    if route=='.':
        for heading in tree.xpath('//h1|//h2|//h3|//h4|//h5|//h6'):
            if text(heading).lower() in ('our mission','open positions','recent highlights'):add_class(heading,'lab-section-accent')
        for subtitle in tree.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," s-item-subtitle ")]'):add_class(subtitle,'lab-home-citation')
        for em in tree.xpath('//*[contains(concat(" ",@class," ")," lab-home-citation ")]//em'):add_class(em,'lab-home-journal')
    if route=='current':
        for strong in tree.xpath('//*[@id="s-content"]//strong'):
            if re.fullmatch(r'(?:Princip(?:al|le) Investigator|Postdoctoral Fellows?|Undergrads? & Visiting Students|Ph\.D\. Students?|Master Students?|Research Assistants?|课题组长|博士后研究员|本科生 & 访问学生|博士研究生)',text(strong),re.I):
                element=next((a for a in strong.iterancestors() if a.tag in ('p','h1','h2','h3','h4','h5','h6')),strong);add_class(element,'lab-section-accent')
    if route in ('alumni','join'):
        for item in list(tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," s-kit-collapse-item ")]')):
            headers=item.xpath('./div[contains(concat(" ",@class," ")," s-kit-collapse-header ")]');contents=item.xpath('./div[contains(concat(" ",@class," ")," s-kit-collapse-content ")]')
            if not headers or not contents:continue
            details=html.Element('details',{'class':'lab-disclosure'});summary=html.Element('summary')
            header=headers[0]
            for attr in ('role','tabindex','aria-expanded','aria-disabled'):header.attrib.pop(attr,None)
            for icon in header.xpath('.//div[contains(@class,"s-kit-collapse-expand-icon")]'):icon.getparent().remove(icon)
            summary.append(header);details.append(summary)
            content=contents[0];content.set('class','lab-disclosure-content');content.attrib.pop('style',None);details.append(content)
            item.getparent().replace(item,details)
        if route=='join':
            for heading in tree.xpath('//details[@class="lab-disclosure"]/summary//h4'):
                add_class(heading,'lab-position-title')
        if route=='alumni':
            for strong in tree.xpath('//details[@class="lab-disclosure"]/summary//strong'):add_class(strong,'lab-alumni-name')
            for strong in tree.xpath('//details[@class="lab-disclosure"]//strong'):
                if text(strong).lower().rstrip(':')=='selected publications':add_class(strong,'lab-alumni-label')
    for carousel in tree.xpath('//div[contains(concat(" ",@class," ")," lab-carousel ")]'):
        for controls in carousel.xpath('./div[contains(@class,"lab-carousel-controls") or contains(@class,"lab-carousel-dots")]'):carousel.remove(controls)
        slides_list=carousel.xpath('./figure');dots=html.Element('div',{'class':'lab-carousel-dots','role':'group','aria-label':'Choose research highlight'})
        for image in carousel.xpath('./figure//img'):image.set('loading','eager')
        for index in range(len(slides_list)):
            dots.append(html.Element('button',{'class':'lab-carousel-dot','type':'button','data-slide':str(index),'aria-label':f'Show slide {index+1} of {len(slides_list)}','aria-pressed':'true' if index==0 else 'false'}))
        carousel.append(dots)
    if route=='contact':
        contact=tree.xpath('//*[@id="s-content"]')[0]
        profile_names=['Curriculum Vitae','Biography','PKU Profile','Google Scholar','ResearcherID','ORCID','X (Twitter)','LinkedIn','ResearchGate']
        profile_links={text(a):a.get('href') for a in contact.xpath('.//a[@href]') if text(a) in profile_names}
        contact.clear();contact.set('id','s-content')
        layout=html.fragment_fromstring('''<main class="lab-contact-layout">
          <header class="lab-contact-intro"><p class="lab-contact-eyebrow">Mengdi Han Research Group</p><h1>Contact</h1><p>Department of Biomedical Engineering · Peking University</p></header>
          <div class="lab-contact-grid">
            <section class="lab-contact-profile" aria-labelledby="contact-name"><div class="lab-contact-person"><div class="lab-contact-portrait"><img src="/images/people/mengdi-han/contact.jpg" alt="Mengdi Han"></div><div><h2 id="contact-name">Mengdi Han</h2><p>College of Future Technology<br>Peking University</p></div></div><div class="lab-contact-email"><span>Email</span><a href="mailto:hmd@pku.edu.cn">hmd[at]pku.edu.cn</a></div><h3>Profiles &amp; resources</h3><nav class="lab-contact-profiles" aria-label="Profiles and resources"></nav><div class="lab-contact-address"><h3>Mailing address</h3><p>Department of Biomedical Engineering<br>College of Future Technology<br>Peking University<br>Beijing 100871, China</p></div></section>
            <section class="lab-contact-visit" aria-labelledby="contact-visit"><h2 id="contact-visit">Visit our lab</h2><figure class="lab-contact-map"><a href="/images/people/mengdi-han/contact-02.jpg" data-lightbox="true" aria-label="Enlarge laboratory location map"><img src="/images/people/mengdi-han/contact-02.jpg" alt="Peking University campus map and laboratory location"></a><figcaption>Campus map · Click to enlarge</figcaption></figure><nav class="lab-contact-map-links" aria-label="Map services"><a href="https://maps.app.goo.gl/XG2o6uWEqPignxYM8" target="_blank" rel="noopener noreferrer">Google Map ↗</a><a href="https://j.map.baidu.com/86/7Spi" target="_blank" rel="noopener noreferrer">百度地图 ↗</a><a href="https://surl.amap.com/4fO0iYusb3Nn" target="_blank" rel="noopener noreferrer">高德地图 ↗</a></nav><div class="lab-contact-travel"><section><h3>② Metro · ~350 m</h3><p>East Gate of Peking University, Exit B<br>北京大学东门站，B出口</p></section><section><h3>③ Bus · ~350 m</h3><p>Zhongguanyuan North<br>中关园北站</p></section><section class="lab-contact-driving"><h3>① Lab location / ④ Driving &amp; taxi</h3><p>No. 116 Zhongguancun North Street<br>中关村北大街116号，北京大学新奥工学大楼</p></section></div></section>
          </div></main>''')
        profile_nav=layout.xpath('.//nav[@class="lab-contact-profiles"]')[0]
        profile_icons=['contact-02.png','contact-03.png','contact.png','contact-06.png','contact-04.png','contact-05.png','contact-07.png','contact-08.png','contact-09.png']
        for name,icon in zip(profile_names,profile_icons):
            if name in profile_links:
                link=html.Element('a',href=profile_links[name]);link.append(html.Element('img',src='/images/people/mengdi-han/'+icon,alt='',attrib={'aria-hidden':'true','width':'18','height':'18'}));label=html.Element('span');label.text=name;link.append(label);profile_nav.append(link)
        layout.append(html.fragment_fromstring('<footer class="lab-contact-footer">Copyright © 2021 Mengdi Han Research Group - All Rights Reserved<br><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">京ICP备2021005752号-1</a></footer>'))
        contact.append(layout)
        # The platform snapshot nests the right column inside the left column.
        for right in tree.xpath('//div[contains(concat(" ",@class," ")," col-7 ")]'):
            rows=right.xpath('ancestor::div[contains(concat(" ",@class," ")," s-row-content ")]')
            if rows:rows[-1].append(right)
        for spacer in tree.xpath('//div[contains(concat(" ",@class," ")," s-element-spacer ")]'):
            spacer.getparent().remove(spacer)
        for image in tree.xpath('//img[@src]'):
            if image.get('src')=='/images/people/mengdi-han/contact-02.jpg':
                image.set('alt','Peking University campus map and laboratory location');image.set('loading','eager')
                if image.getparent().tag!='a':
                    parent=image.getparent();link=html.Element('a',href=image.get('src'),attrib={'data-lightbox':'true','aria-label':'Enlarge laboratory location map'});parent.replace(image,link);link.append(image)
    if route=='covers':
        content=tree.xpath('//*[@id="s-content"]')[0]
        existing_cards=content.xpath('.//article[@class="lab-cover-card"]')
        covers=[(card.xpath('.//img')[0].get('src'),card.xpath('.//a[@class="lab-cover-article"]')[0].get('href')) for card in existing_cards] if existing_cards else [(image.get('src'),image.getparent().get('href')) for image in content.xpath('.//img') if image.getparent().tag=='a']
        content.clear();content.set('id','s-content')
        gallery=html.fragment_fromstring('<main class="lab-covers-layout"><header><h1>Journal covers</h1><p>Explore the covers featuring our research.</p></header><div class="lab-covers-grid"></div></main>')
        grid=gallery.xpath('.//div')[0]
        def cover_info(href):
            info=publication_index.get(paper_key(href),{}).copy()
            record=citations['records'].get(title_key(info.get('title','')))
            if record and record.get('year'):info['year']=record['year']
            return info
        covers.sort(key=lambda item:cover_info(item[1]).get('year',0),reverse=True)
        for src,href in covers:
            info=cover_info(href)
            card=html.Element('article',{'class':'lab-cover-card'})
            image_link=html.Element('a',href=src,attrib={'data-lightbox':'true','class':'lab-cover-image','aria-label':'Enlarge '+info.get('journal','journal')+' cover'});image_link.append(html.Element('img',src=src,alt=info.get('journal','Journal')+' cover',loading='lazy'));card.append(image_link)
            caption=html.Element('div',{'class':'lab-cover-caption'})
            heading=html.Element('h2');heading.text=info.get('journal') or 'Journal cover';caption.append(heading)
            if info.get('year'):
                year=html.Element('p',{'class':'lab-cover-year'});year.text='Publication · '+str(info['year']);caption.append(year)
            if info.get('title'):
                title=html.Element('p',{'class':'lab-cover-title'});title.text=info['title'];caption.append(title)
            article=html.Element('a',href=href,attrib={'target':'_blank','rel':'noopener noreferrer','class':'lab-cover-article'});article.text='View article ↗';caption.append(article);card.append(caption);grid.append(card)
        gallery.append(html.fragment_fromstring('<footer class="lab-contact-footer">Copyright © 2021 Mengdi Han Research Group - All Rights Reserved<br><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">京ICP备2021005752号-1</a></footer>'))
        content.append(gallery)
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
        for element in tree.xpath('//*[@id="s-content"]//h1|//*[@id="s-content"]//h2|//*[@id="s-content"]//h3|//*[@id="s-content"]//h4|//*[@id="s-content"]//h5|//*[@id="s-content"]//h6|//*[@id="s-content"]//p'):
            if re.fullmatch(r'\d{4}',text(element)):add_class(element,'lab-content-year')
    if not route.startswith('news') and route!='covers':
        for link in tree.xpath('//a[contains(concat(" ",@class," ")," lab-publication-link ")]'):
            if not text(link):continue
            paragraph=next((a for a in link.iterancestors() if a.tag=='p'),None)
            if paragraph is None:continue
            if (route in ('all','publications') or re.fullmatch(r'publications\d{4}',route)) and (not paper_id(paragraph) or paragraph.xpath('.//a[@href]')[0] is not link):continue
            record=citation_record(link);count=record.get('count') if record else None
            url=(record.get('cited_by') or record.get('scholar_article')) if record else 'https://scholar.google.com/scholar?hl=en&q='+quote('"'+text(link)+'"')
            target=paragraph;next_element=paragraph.getnext()
            for _ in range(3):
                if next_element is None or paper_id(next_element):break
                if next_element.tag=='p' and next_element.xpath('.//em[not(contains(@class,"lab-author-note"))]'):target=next_element
                next_element=next_element.getnext()
            if target.xpath('./span[contains(@class,"lab-citation-badge")]'):continue
            badge=html.Element('span',{'class':'lab-citation-badge'})
            anchor=html.Element('a',href=url,attrib={'class':'lab-citation-link','target':'_blank','rel':'noopener noreferrer','data-link-kind':'citation','title':('Google Scholar · checked '+record['checked_on'] if record else 'Not yet matched in Google Scholar; search by article title')})
            anchor.text='Citations ('+(str(count)+('*' if record.get('estimated') else '') if count is not None else '—')+')';badge.append(anchor);target.append(badge)
    for stylesheet in tree.xpath('//link[starts-with(@href,"/static/hmd-color.css")]'):
        stylesheet.getparent().remove(stylesheet)
    tree.find('head').append(html.Element('link',rel='stylesheet',href='/static/hmd-color.css?v='+color_version))
    for script in tree.xpath('//script[starts-with(@src,"/static/site.js")]'):script.set('src','/static/site.js?v='+script_version)
    write(path,tree)

report={'current_year':today,'publications_entry_year':current(pub_years),'news_entry_year':current(news_years),'publication_years':pub_years,'news_years':news_years,'publication_counts':counts,'total_publications':len(paper_ids)}
(ROOT/'archive-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
