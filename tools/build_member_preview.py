from pathlib import Path
from lxml import html
from member_gallery import build_gallery
import ast,copy,json,re,sys,unicodedata
root=Path(sys.argv[1] if len(sys.argv)>1 else 'work/design-preview')
publish='--publish' in sys.argv
roster=json.loads((root/'data/member-publications.json').read_text(encoding='utf8'))
source=html.document_fromstring((root/'current/index.html').read_text(encoding='utf8'))
papers={}
for path in root.glob('publications*/index.html'):
    if not re.fullmatch(r'publications\d{4}',path.parent.name):continue
    year=int(path.parent.name[-4:])
    for p in html.document_fromstring(path.read_text(encoding='utf8')).xpath('//p'):
        m=re.match(r'^\((\d+)\)',p.text_content().strip());anchors=p.xpath('.//a[@href]')
        if not m or not anchors:continue
        journal='';following=p.getnext()
        for _ in range(3):
            if following is None:break
            for em in following.xpath('.//em'):
                value=' '.join(em.text_content().split())
                if value and not re.fullmatch(r'et\s*al\.?|\d+(?:\.\d+)?',value,re.I):journal=value;break
            if journal:break
            following=following.getnext()
        metadata=copy.deepcopy(following) if journal and following is not None else html.Element('p')
        for badge in metadata.xpath('.//*[contains(@class,"lab-citation-badge")]'):badge.getparent().remove(badge)
        for node in metadata.iter():
            node.attrib.pop('style',None);node.attrib.pop('class',None)
        papers[int(m[1])]={'metadata':metadata,'title':' '.join(anchors[0].text_content().split()),'url':anchors[0].get('href'),'journal':journal,'year':year,'authors':[a.strip() for a in p.getnext().text_content().split(',')]}
def name_key(s):return ''.join(c for c in unicodedata.normalize('NFKC',s).casefold() if c.isalnum())
def is_first_author(name,pid):
    evidence=roster['evidence'].get(str(pid),{})
    full=evidence.get('full_authors',[]);tokens=papers[pid]['authors']
    confirmation=roster.get('confirmed_author_positions',{}).get(str(pid),{}).get(name)
    if confirmation:
        index=confirmation['author_index'];words=name.split();initials=''.join(w[0] for w in words[:-1])+' '+words[-1]
        if index<len(tokens) and name_key(tokens[index].replace('¹','').replace('*',''))==name_key(initials):
            return index==0 or '¹' in tokens[index]
    for index,author in enumerate(full):
        if name_key(author)!=name_key(name) or index>=len(tokens):continue
        words=name.split();initials=''.join(w[0] for w in words[:-1])+' '+words[-1]
        token=tokens[index]
        if name_key(token.replace('¹','').replace('*',''))!=name_key(initials):continue
        if index==0 or '¹' in token:return True
    return False
page=html.document_fromstring('<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Current Members — Design Preview</title><link rel="stylesheet" href="/static/site.css"><link rel="stylesheet" href="/static/hmd-color.css"><link rel="stylesheet" href="/static/member-preview.css?v=20261014-gallery-v2"><script src="/static/site.js" defer></script><script src="/static/member-gallery.js?v=20261014-gallery-v2" defer></script></head><body class="lab-member-preview"><div id="s-content"></div></body></html>')
page.find('body').insert(0,copy.deepcopy(source.xpath('//header[contains(@class,"lab-header")]')[0]))
main=html.fragment_fromstring('''<main class="members-layout"><header class="members-intro"><h1>Current Members</h1><p>Our team brings together electrical engineering, biomedical engineering, mechanical engineering, materials science, life science and medicine.</p><p class="members-preview-note">Layout preview. <a href="/current/">View the current page</a></p></header></main>''')
full_order={}
for paragraph in html.document_fromstring((root/'all/index.html').read_text(encoding='utf8')).xpath('//p'):
    match=re.match(r'^\((\d+)\)',paragraph.text_content().strip())
    if match:full_order.setdefault(int(match[1]),len(full_order))
groups=roster['groups']
grid=html.Element('div',{'class':'members-grid'})
body_layout=html.Element('div',{'class':'members-body'})
body_layout.append(grid);main.append(body_layout)
for section_id,label,chinese,people in groups:
    for name,zh,school in people:
        card=html.Element('article',{'class':'member-card','data-member':name})
        title=html.Element('h3');title.text=name+' ';role=html.Element('span',{'class':'member-role'});role.text=roster['member_roles'][name];title.append(role);card.append(title)
        if name==people[0][0]:card.set('id',section_id)
        if name=='Mengdi Han':school='Peking University / 北京大学'
        english_school,_,chinese_school=school.partition(' / ')
        education=html.Element('p',{'class':'member-school'});education.text=english_school;card.append(education)
        chinese_name=html.Element('p',{'class':'member-chinese'});chinese_name.text=zh+(' · '+chinese_school if chinese_school else '');card.append(chinese_name)
        if name=='Mengdi Han':grid.append(card);continue
        ids=[pid for pid in roster['member_paper_ids'].get(name,[]) if pid in papers and str(pid) not in roster.get('excluded_representative_paper_ids',{}) and is_first_author(name,pid)]
        ids.sort(key=lambda pid:full_order.get(pid,len(full_order)+126-pid))
        details=html.Element('details',{'class':'member-publications'})
        summary=html.Element('summary');summary.text='Selected Publications'+(' ('+str(len(ids))+')' if ids else '');details.append(summary)
        if ids:
            listing=html.Element('ol',{'class':'member-paper-list'})
            for pid in ids:
                paper=papers.get(pid)
                if not paper:continue
                item=html.Element('li',{'data-paper-id':str(pid)})
                p=html.Element('p',{'class':'member-paper-title'});link=html.Element('a',href=paper['url'],attrib={'target':'_blank','rel':'noopener noreferrer','data-link-kind':'article'});link.text=paper['title'];p.append(link);item.append(p)
                metadata=html.Element('p',{'class':'member-paper-meta'})
                authors=paper['authors'];cofirst=[a for a in authors if '¹' in a]
                selected=cofirst or authors[:1]
                metadata.text=', '.join(selected)+', '
                etal=html.Element('em',{'class':'lab-author-note'});etal.text='et al.';etal.tail=', ';metadata.append(etal)
                original=copy.deepcopy(paper['metadata'])
                etal.tail+=original.text or ''
                for child in list(original):metadata.append(child)
                item.append(metadata);listing.append(item)
            details.append(listing)
        else:
            empty=html.Element('p',{'class':'member-paper-pending'});empty.text='-';details.append(empty)
        card.append(details);grid.append(card)
photo_data=json.loads((root/'data/group-photos.json').read_text(encoding='utf8'))
photos=build_gallery(photo_data)
body_layout.append(photos)
page.xpath('//*[@id="s-content"]')[0].append(main)
out=root/'preview/current-members/index.html';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(html.tostring(page,encoding='utf8',doctype='<!DOCTYPE html>'))
if publish:
    formal=copy.deepcopy(page)
    formal.find('head/title').text='CURRENT - Mengdi Han Research Group'
    for node in formal.xpath('//meta[@name="robots"] | //*[@class="members-preview-note"]'):node.getparent().remove(node)
    (root/'current/index.html').write_bytes(html.tostring(formal,encoding='utf8',doctype='<!DOCTYPE html>'))
print('Generated compact bilingual member cards, full publication metadata and '+str(len(photo_data))+' group photographs')
