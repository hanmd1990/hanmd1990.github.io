(() => {
  'use strict';
  const payload=document.getElementById('lit-data');
  if(!payload)return;
  const data=JSON.parse(payload.content.textContent);
  const byId=id=>document.getElementById(id);
  const search=byId('lit-search'),edition=byId('lit-edition'),journal=byId('lit-journal'),sort=byId('lit-sort'),results=byId('lit-results');
  let topic='';
  const node=(tag,cls,value)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(value!==undefined)el.textContent=value;return el;};
  const selected=()=>data.editions.find(e=>e.id===edition.value);
  function row(a){
    const card=node('article','lit-paper');card.dataset.id=a.id;
    const meta=node('p','lit-meta');meta.append(node('span','lit-journal',a.journal));
    const date=node('time','',a.date);date.dateTime=a.date;meta.append(date,node('span','lit-type',a.type));
    const heading=node('h2'),link=node('a','',a.title);link.href=a.url;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
    const bottom=node('div','lit-paper-bottom');bottom.append(node('p','lit-tags',a.topics.join(' / ')));
    const authors=node('details','lit-authors');authors.append(node('summary','','Authors and DOI'),node('p','',(a.authors.length?a.authors.join('; '):'Author list unavailable.')+(a.authorsComplete?'':' (Complete author list not verified.)')));
    if(a.doi)authors.append(node('p','','DOI: '+a.doi));bottom.append(authors);
    card.append(meta,heading,node('p','lit-summary',a.summary),bottom);return card;
  }
  function render(){
    const e=selected(),q=search.value.trim().toLocaleLowerCase();
    const items=e.articles.filter(a=>(!topic||a.topics.includes(topic))&&(!journal.value||a.journal===journal.value)&&(!q||[a.title,a.journal,a.summary,a.doi,...a.authors,...a.topics].join(' ').toLocaleLowerCase().includes(q)));
    items.sort((a,b)=>sort.value==='date'?b.date.localeCompare(a.date)||a.title.localeCompare(b.title):sort.value==='journal'?a.journal.localeCompare(b.journal)||b.date.localeCompare(a.date):b.relevance-a.relevance||a.journal.localeCompare(b.journal)||a.title.localeCompare(b.title));
    results.replaceChildren(...items.map(row));
    byId('lit-count').textContent=items.length+' of '+e.articles.length+' selected articles';
    byId('lit-empty').hidden=items.length!==0;
    byId('lit-window').textContent=e.start+' – '+e.end+' (Beijing time)';
    byId('lit-note').textContent=e.note;
    byId('lit-coverage-list').replaceChildren(...e.coverage.map(c=>node('p','',c.journal+': '+c.status)));
    document.querySelectorAll('.lit-topics button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
  }
  function setup(){
    const e=selected();journal.replaceChildren(new Option('All journals',''),...[...new Set(e.articles.map(a=>a.journal))].sort().map(j=>new Option(j,j)));
    topic='';const topics=['',...[...new Set(e.articles.flatMap(a=>a.topics))].sort()];
    document.querySelector('.lit-topics').replaceChildren(...topics.map(t=>{const b=node('button','',t||'All topics');b.type='button';b.dataset.topic=t;b.setAttribute('aria-pressed',String(!t));b.addEventListener('click',()=>{topic=t;render();});return b;}));render();
  }
  search.addEventListener('input',render);journal.addEventListener('change',render);sort.addEventListener('change',render);edition.addEventListener('change',setup);
  byId('lit-reset').addEventListener('click',()=>{search.value='';sort.value='relevance';setup();search.focus();});setup();
})();
