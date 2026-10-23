(() => {
  'use strict';
  const payload=document.getElementById('lit-data');
  if(!payload)return;
  const data=JSON.parse(payload.content.textContent);
  const byId=id=>document.getElementById(id);
  const search=byId('lit-search'),edition=byId('lit-edition'),sort=byId('lit-sort'),results=byId('lit-results');
  const dialog=byId('lit-journals-dialog'),journalOpen=byId('lit-journals-open'),journalSearch=byId('lit-journals-search');
  let topic='',journals=new Set(),draft=new Set(),sources=[];
  const node=(tag,cls,value)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(value!==undefined)el.textContent=value;return el;};
  const selected=()=>data.editions.find(e=>e.id===edition.value);
  const sourceName=s=>s.replace('bioRxiv - Bioengineering','bioRxiv · Bioengineering').replace('Arxiv - Applied Physics','arXiv · Applied Physics');
  function row(a){
    const card=node('article','lit-paper');card.dataset.id=a.id;
    const meta=node('p','lit-meta');meta.append(node('span','lit-journal',a.journal));
    const date=node('time','',a.date);date.dateTime=a.date;meta.append(date);
    const heading=node('h2'),link=node('a','',a.title);link.href=a.url;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
    const bottom=node('div','lit-paper-bottom');bottom.append(node('p','lit-tags',a.topics.join(' / ')));
    const authors=node('details','lit-authors');authors.append(node('summary','','Authors and DOI'),node('p','',(a.authors.length?a.authors.join('; '):'Author list unavailable.')+(a.authorsComplete?'':' (Complete author list not verified.)')));
    if(a.doi)authors.append(node('p','','DOI: '+a.doi));bottom.append(authors);
    card.append(meta,heading,node('p','lit-summary',a.summary),bottom);return card;
  }
  function render(){
    const e=selected(),q=search.value.trim().toLocaleLowerCase();
    const items=e.articles.filter(a=>(!topic||a.topics.includes(topic))&&journals.has(sourceName(a.journal))&&(!q||[a.title,a.journal,a.summary,a.doi,...a.authors,...a.topics].join(' ').toLocaleLowerCase().includes(q)));
    items.sort((a,b)=>sort.value==='date'?b.date.localeCompare(a.date)||a.title.localeCompare(b.title):sort.value==='journal'?a.journal.localeCompare(b.journal)||b.date.localeCompare(a.date):b.relevance-a.relevance||a.journal.localeCompare(b.journal)||a.title.localeCompare(b.title));
    results.replaceChildren(...items.map(row));
    byId('lit-count').textContent=items.length+' of '+e.articles.length+' selected articles';
    byId('lit-empty').hidden=items.length!==0;
    byId('lit-window').textContent=e.start+' – '+e.end+' (Beijing time)';
    byId('lit-note').textContent=e.note;
    byId('lit-coverage-list').replaceChildren(...e.coverage.map(c=>node('p','',sourceName(c.journal)+': '+c.status)));
    document.querySelectorAll('.lit-topics button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
    journalOpen.textContent=journals.size===sources.length?'All '+sources.length+' sources':journals.size+' selected';
  }
  function paintJournals(){
    const query=journalSearch.value.trim().toLocaleLowerCase();
    const e=selected(),counts=new Map();e.articles.forEach(a=>{const j=sourceName(a.journal);counts.set(j,(counts.get(j)||0)+1);});
    byId('lit-journals-options').replaceChildren(...sources.map(j=>{
      const label=node('label','lit-journal-option');label.hidden=!!query&&!j.toLocaleLowerCase().includes(query);
      const input=node('input');input.type='checkbox';input.value=j;input.checked=draft.has(j);
      input.addEventListener('change',()=>{input.checked?draft.add(j):draft.delete(j);selectionCount();});
      const text=node('span','',j);text.append(node('small','',(counts.get(j)||0)+' articles in this edition'));label.append(input,text);return label;
    }));selectionCount();
  }
  function selectionCount(){byId('lit-journals-selection').textContent=draft.size+' of '+sources.length+' selected';}
  function setup(){
    const e=selected();sources=[...new Set([...e.coverage.map(c=>sourceName(c.journal)),...e.articles.map(a=>sourceName(a.journal))])].sort();
    journals=new Set(sources);topic='';const topics=['',...[...new Set(e.articles.flatMap(a=>a.topics))].sort()];
    document.querySelector('.lit-topics').replaceChildren(...topics.map(t=>{const b=node('button','',t||'All topics');b.type='button';b.dataset.topic=t;b.setAttribute('aria-pressed',String(!t));b.addEventListener('click',()=>{topic=t;render();});return b;}));render();
  }
  journalOpen.addEventListener('click',()=>{draft=new Set(journals);journalSearch.value='';paintJournals();dialog.showModal();});
  journalSearch.addEventListener('input',paintJournals);
  byId('lit-journals-all').addEventListener('click',()=>{draft=new Set(sources);paintJournals();});
  byId('lit-journals-none').addEventListener('click',()=>{draft.clear();paintJournals();});
  byId('lit-journals-apply').addEventListener('click',()=>{journals=new Set(draft);render();dialog.close();});
  for(const id of ['lit-journals-close','lit-journals-cancel'])byId(id).addEventListener('click',()=>dialog.close());
  search.addEventListener('input',render);sort.addEventListener('change',render);edition.addEventListener('change',setup);
  byId('lit-reset').addEventListener('click',()=>{search.value='';sort.value='relevance';setup();search.focus();});
  // Anchor the recurring schedule in Beijing, then derive both DST-sensitive cities.
  const now=new Date(),parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  const part=t=>Number(parts.find(p=>p.type===t).value),day=new Date(Date.UTC(part('year'),part('month')-1,part('day')));
  let next=new Date(day.getTime()+((5-day.getUTCDay()+7)%7)*86400000-4.5*3600000);
  if(next<=now)next=new Date(next.getTime()+7*86400000);
  byId('lit-schedule-times').textContent=[['Asia/Shanghai','Beijing'],['America/New_York','New York'],['Europe/London','London']].map(([timeZone,city])=>new Intl.DateTimeFormat('en-GB',{timeZone,weekday:'long',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(next)+' '+city).join(' / ');
  setup();
})();
