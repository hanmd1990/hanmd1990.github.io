import copy,re
from lxml import html

def rebuild_alumni(tree):
    old=tree.xpath('//details[contains(concat(" ",normalize-space(@class)," ")," lab-disclosure ")]')
    if not old:return
    main=html.Element('main',{'class':'lab-alumni-layout'})
    heading=html.Element('h1');heading.text='Alumni';main.append(heading)
    for member in old:
        values=[' '.join(p.text_content().split()) for p in member.xpath('./summary//p') if p.text_content().strip()]
        if not values:continue
        match=re.match(r'(.+?)\s*\(([^)]+)\),\s*(.+)',values[0])
        if not match:continue
        name,zh,role=match.groups()
        fields={}
        for value in values[1:]:
            key,sep,text=value.partition(':')
            if sep:fields[' '.join(key.lower().split())]=text.strip()
        details=html.Element('details',{'class':'alumni-member','data-member':name})
        summary=html.Element('summary');profile=html.Element('div',{'class':'alumni-profile'})
        prior=html.Element('div',{'class':'alumni-prior'});label=html.Element('h2');label.text='Education';prior.append(label)
        for key,value in fields.items():
            if key.endswith('school'):
                degree='Ph.D.' if key.startswith('ph.d.') else 'Undergraduate'
                tag=html.Element('p',{'class':'alumni-degree'});tag.text=degree;prior.append(tag)
                school=html.Element('p');school.text=value;prior.append(school)
            elif key.endswith('major'):
                major=html.Element('p',{'class':'alumni-major'});major.text=value;prior.append(major)
        profile.append(prior)
        identity=html.Element('div',{'class':'alumni-identity'});title=html.Element('h3');title.text=name;identity.append(title)
        chinese=html.Element('p',{'class':'alumni-chinese'});chinese.text=zh;identity.append(chinese)
        tenure=html.Element('div',{'class':'alumni-tenure'});identity.append(tenure)
        position=html.Element('p',{'class':'alumni-role'});position.text=role;tenure.append(position)
        years=html.Element('p',{'class':'alumni-years'});years.text=fields.get('years in group','');tenure.append(years);profile.append(identity)
        next_position=html.Element('div',{'class':'alumni-next'});label=html.Element('h2');label.text='Next role';next_position.append(label)
        destination=html.Element('p');destination.text=fields.get('next position','');next_position.append(destination);profile.append(next_position)
        summary.append(profile)
        paragraphs=member.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," lab-disclosure-content ")]//p')
        content=html.Element('div',{'class':'alumni-publications'})
        count=0
        for paragraph in paragraphs:
            if not paragraph.text_content().strip() or 'Selected Publications:'==paragraph.text_content().strip():continue
            clone=copy.deepcopy(paragraph)
            title_link=clone.xpath('.//a[contains(@class,"lab-publication-link")]')
            for node in clone.iter():
                node.attrib.pop('style',None)
                classes=[value for value in node.get('class','').split() if value.startswith('lab-')]
                if classes:node.set('class',' '.join(classes))
                else:node.attrib.pop('class',None)
            clone.set('class','alumni-paper-title' if title_link else 'alumni-paper-meta')
            if title_link:
                link=copy.deepcopy(title_link[0])
                title=link.text_content().strip()
                for child in list(link):link.remove(child)
                link.text=title;link.tail=None
                clone.clear();clone.set('class','alumni-paper-title');clone.append(link)
                count+=1
            else:
                for strong in clone.xpath('.//strong'):strong.drop_tag()
            content.append(clone)
        if not count:
            empty=html.Element('p',{'class':'alumni-paper-meta'});empty.text='No selected publications listed.';content.append(empty)
        toggle=html.Element('div',{'class':'alumni-publications-toggle'});toggle.text='Selected Publications'+(' ('+str(count)+')' if count else '');identity.append(toggle)
        details.append(summary);details.append(content);main.append(details)
    target=tree.xpath('//*[@id="s-content"]')[0]
    for child in list(target):target.remove(child)
    target.append(main)
