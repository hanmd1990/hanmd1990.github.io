"""Render recruitment content and dated availability from one editable data file."""
import datetime
import json
from lxml import html, etree


def rebuild_join(tree, root):
    data = json.loads((root / 'data/join-us.json').read_text(encoding='utf8'))
    content = tree.xpath('//*[@id="s-content"]')[0]
    content.clear()
    content.set('id', 's-content')
    main = etree.SubElement(content, 'main', {'class': 'lab-join-layout'})
    intro = etree.SubElement(main, 'header', {'class': 'lab-join-intro'})
    etree.SubElement(intro, 'h1').text = 'Join Us'
    etree.SubElement(intro, 'p').text = data['intro']
    email = etree.SubElement(intro, 'a', href='mailto:hmd@pku.edu.cn', attrib={'class': 'lab-join-email'})
    email.text = 'Contact Mengdi Han ↗'
    dates = etree.SubElement(intro, 'p', {'class': 'lab-join-updated'})
    dates.text = 'Page updated: '
    for key, prefix in [('updated_on', ''), ('notice_updated_on', ' · Recruitment notice: ')]:
        datetime.date.fromisoformat(data[key])
        if prefix:
            dates[-1].tail = prefix
        etree.SubElement(dates, 'time', datetime=data[key]).text = data[key]
    nav = etree.SubElement(main, 'nav', {'class': 'lab-join-nav', 'aria-label': 'Recruitment categories'})
    for index, role in enumerate(data['roles'], 1):
        link = etree.SubElement(nav, 'a', href='#'+role['id'])
        etree.SubElement(link, 'span', {'class': 'lab-join-category'}).text = role['label']
        etree.SubElement(link, 'span', {'class': 'lab-join-count'}).text = role['count']
    for index, role in enumerate(data['roles'], 1):
        section = etree.SubElement(main, 'section', {'class': 'lab-join-role', 'id': role['id'], 'aria-labelledby': role['id']+'-title'})
        header = etree.SubElement(section, 'header', {'class': 'lab-join-role-heading'})
        etree.SubElement(header, 'span', {'class': 'lab-join-number', 'aria-hidden': 'true'}).text = f'{index:02}'
        title = etree.SubElement(header, 'div')
        etree.SubElement(title, 'h2', id=role['id']+'-title').text = role['title']
        etree.SubElement(title, 'p').text = role['count']
        body = etree.SubElement(section, 'div', {'class': 'lab-join-role-body'})
        for node in html.fragments_fromstring(role['body']):
            body.append(node)
