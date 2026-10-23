(() => {
  'use strict';
  const payload=document.getElementById('lit-data');
  if(!payload)return;
  const data=JSON.parse(payload.content.textContent);
  const byId=id=>document.getElementById(id);
  const search=byId('lit-search'),edition=byId('lit-edition'),sort=byId('lit-sort'),results=byId('lit-results');
  const dialog=byId('lit-journals-dialog'),journalOpen=byId('lit-journals-open');
  let topic='',journals=new Set(),draft=new Set(),sources=[];
  const node=(tag,cls,value)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(value!==undefined)el.textContent=value;return el;};
  const feedbackKey='bioe-radar-feedback-v1';
  let feedback=Object.create(null),storageAvailable=true;
  const feedbackId=a=>String(a.doi||a.id).trim().toLowerCase().replace(/^https?:\/\/(?:dx\.)?doi\.org\//,'').replace(/(10\.21203\/.*|10\.1101\/.*)\/v\d+$/,'$1');
  function validateFeedback(value){
    if(!value||value.version!==1||!Array.isArray(value.entries)||value.entries.length>10000)throw Error('Invalid feedback file.');
    const clean=Object.create(null);
    for(const e of value.entries){
      if(!e||typeof e.key!=='string'||!e.key||e.key.length>1000||!Array.isArray(e.signals)||e.signals.some(x=>!['useful','more','irrelevant'].includes(x))||typeof e.note!=='string'||e.note.length>2000)throw Error('Invalid feedback entry.');
      if(e.signals.includes('irrelevant')&&e.signals.length>1)throw Error('Conflicting feedback.');
      clean[e.key]={key:e.key,id:String(e.id||'').slice(0,1000),doi:String(e.doi||'').slice(0,1000),title:String(e.title||'').slice(0,2000),journal:String(e.journal||'').slice(0,300),topics:Array.isArray(e.topics)?e.topics.filter(x=>typeof x==='string').slice(0,30).map(x=>x.slice(0,200)):[],signals:[...new Set(e.signals)],note:e.note,updatedAt:String(e.updatedAt||'').slice(0,50)};
    }return clean;
  }
  try{const saved=localStorage.getItem(feedbackKey);if(saved)feedback=validateFeedback(JSON.parse(saved));}catch(error){storageAvailable=false;}
  function feedbackStatus(message){byId('lit-feedback-status').textContent=message||Object.keys(feedback).length+' articles with feedback. '+(storageAvailable?'Saved in this browser only.':'Browser storage unavailable; export before leaving.');}
  function saveFeedback(){
    try{localStorage.setItem(feedbackKey,JSON.stringify({version:1,entries:Object.values(feedback)}));storageAvailable=true;}catch(error){storageAvailable=false;}
    feedbackStatus();
  }
  function feedbackControls(a){
    const key=feedbackId(a),box=node('div','lit-feedback'),buttons=node('div','lit-feedback-buttons');
    const current=()=>feedback[key]||{key,id:a.id,doi:a.doi||'',title:a.title,journal:a.journal,topics:a.topics,signals:[],note:'',updatedAt:''};
    const update=entry=>{entry.updatedAt=new Date().toISOString();if(!entry.signals.length&&!entry.note)delete feedback[key];else feedback[key]=entry;saveFeedback();};
    for(const [signal,title] of [['useful','Useful'],['more','More like this'],['irrelevant','Not relevant']]){
      const b=node('button','',title);b.type='button';b.dataset.signal=signal;b.setAttribute('aria-pressed',String(current().signals.includes(signal)));
      b.addEventListener('click',()=>{const entry={...current(),signals:[...current().signals]};if(entry.signals.includes(signal))entry.signals=entry.signals.filter(x=>x!==signal);else entry.signals=signal==='irrelevant'?['irrelevant']:[...entry.signals.filter(x=>x!=='irrelevant'),signal];update(entry);buttons.querySelectorAll('button').forEach(el=>el.setAttribute('aria-pressed',String(entry.signals.includes(el.dataset.signal))));if(byId('lit-feedback-filter').value!=='all')render();});buttons.append(b);
    }
    const details=node('details','lit-feedback-note'),summary=node('summary','','Add a note'),note=node('textarea');note.maxLength=2000;note.rows=2;note.placeholder='What was useful, or why was it not relevant?';note.setAttribute('aria-label','Feedback note for '+a.title);note.value=current().note;note.addEventListener('change',()=>update({...current(),note:note.value.trim()}));details.append(summary,note);box.append(buttons,details);return box;
  }
  const selected=()=>data.editions.find(e=>e.id===edition.value);
  const sourceName=s=>s.replace('bioRxiv - Bioengineering','bioRxiv · Bioengineering').replace('Arxiv - Applied Physics','arXiv · Applied Physics');
  function row(a){
    const card=node('article','lit-paper');card.dataset.id=a.id;
    const meta=node('p','lit-meta');meta.append(node('span','lit-journal',a.journal));
    const date=node(a.date?'time':'span','',a.dateLabel||a.date||'Publication date unverified');if(a.date)date.dateTime=a.date;meta.append(date);
    const heading=node('h2'),link=node('a','',a.title);link.href=a.url;link.target='_blank';link.rel='noopener noreferrer';heading.append(link);
    const bottom=node('div','lit-paper-bottom');bottom.append(node('p','lit-tags',a.topics.join(' / ')));
    const authors=node('p','lit-author-line',(a.authors.length?a.authors.join(', '):'Author list unavailable.')+(a.authorsComplete?'':' (Complete author list not verified.)'));
    card.append(meta,heading,authors,node('p','lit-summary',a.summary),bottom,feedbackControls(a));return card;
  }
  function render(){
    const e=selected(),q=search.value.trim().toLocaleLowerCase();
    const feedbackFilter=byId('lit-feedback-filter').value;
    const items=e.articles.filter(a=>(feedbackFilter==='all'||(feedbackFilter==='marked'?!!feedback[feedbackId(a)]:feedback[feedbackId(a)]?.signals.includes(feedbackFilter)))&&(!topic||a.topics.includes(topic))&&journals.has(sourceName(a.journal))&&(!q||[a.title,a.journal,a.summary,a.doi,...a.authors,...a.topics].join(' ').toLocaleLowerCase().includes(q)));
    items.sort((a,b)=>sort.value==='date'?String(b.date||'').localeCompare(String(a.date||''))||a.title.localeCompare(b.title):sort.value==='journal'?a.journal.localeCompare(b.journal)||String(b.date||'').localeCompare(String(a.date||'')):b.relevance-a.relevance||a.journal.localeCompare(b.journal)||a.title.localeCompare(b.title));
    results.replaceChildren(...items.map(row));
    byId('lit-count').textContent=items.length+' of '+e.articles.length+' selected articles';
    byId('lit-empty').hidden=items.length!==0;
    byId('lit-window').textContent=e.start+' – '+e.end+' (Beijing time)';
    byId('lit-coverage-list').textContent=sources.join('; ')+'.';
    document.querySelectorAll('.lit-topics button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.topic===topic)));
    journalOpen.textContent=journals.size===sources.length?'All '+sources.length+' sources':journals.size+' selected';
  }
  function journalGroup(j){
    if(/^Nature\b|^npj\b|^Microsystems & Nanoengineering$/.test(j))return 'Nature Portfolio';
    if(/^Science(?:$| )/.test(j))return 'Science journals';
    if(['Cell','Neuron','Matter','Device'].includes(j))return 'Cell Press';
    if(/^Advanced /.test(j))return 'Wiley';
    if(/^ACS |^Nano Letters$/.test(j))return 'ACS';
    if(/^Biosensors and Bioelectronics$|^Sensors and Actuators/.test(j))return 'Elsevier';
    if(j==='Journal of Micromechanics and Microengineering')return 'IOP Publishing';
    if(/^IEEE |^Journal of Microelectromechanical Systems$/.test(j))return 'IEEE';
    if(j==='Proceedings of the National Academy of Sciences')return 'PNAS';
    if(/arXiv|bioRxiv|Research Square/.test(j))return 'Preprints';
    return 'Other journals';
  }
  function paintJournals(){
    const e=selected(),coverage=new Map(e.coverage.map(c=>[sourceName(c.journal),c])),counts=new Map();e.articles.forEach(a=>{const j=sourceName(a.journal);counts.set(j,(counts.get(j)||0)+1);});
    const order=['Nature Portfolio','Science journals','Cell Press','Wiley','ACS','Elsevier','IOP Publishing','IEEE','PNAS','Preprints','Other journals'];
    const sections=order.map(group=>{
      const all=sources.filter(j=>journalGroup(j)===group);
      const visible=all;
      if(!visible.length)return null;
      const section=node('section','lit-publisher-group');section.dataset.publisher=group;
      const heading=node('div','lit-publisher-heading'),label=node('label','lit-publisher-toggle'),toggle=node('input');
      toggle.type='checkbox';toggle.checked=all.every(j=>draft.has(j));toggle.indeterminate=!toggle.checked&&all.some(j=>draft.has(j));toggle.setAttribute('aria-label','Select all '+group+' sources');
      toggle.addEventListener('change',()=>{all.forEach(j=>toggle.checked?draft.add(j):draft.delete(j));paintJournals();});
      const title=node('span','',group);label.append(toggle,title);
      heading.append(label,node('span','lit-publisher-count',all.filter(j=>draft.has(j)).length+' / '+all.length+' selected'));
      const grid=node('div','lit-publisher-journals');
      grid.append(...visible.map(j=>{
        const label=node('label','lit-journal-option');
        const input=node('input');input.type='checkbox';input.value=j;input.checked=draft.has(j);
        input.addEventListener('change',()=>{input.checked?draft.add(j):draft.delete(j);selectionCount();
          toggle.checked=all.every(name=>draft.has(name));toggle.indeterminate=!toggle.checked&&all.some(name=>draft.has(name));
          heading.querySelector('.lit-publisher-count').textContent=all.filter(name=>draft.has(name)).length+' / '+all.length+' selected';});
        const record=coverage.get(j),read=Number.isInteger(record?.readCount)&&record.readCount>=0?record.readCount:0;
        const text=node('span','',j);text.append(node('small','',read+' articles, '+(counts.get(j)||0)+' selected'));label.append(input,text);return label;
      }));
      section.append(heading,grid);return section;
    }).filter(Boolean);
    byId('lit-journals-options').replaceChildren(...sections);
    if(!sections.length)byId('lit-journals-options').append(node('p','lit-journal-no-match','No matching journals or publishers.'));
    selectionCount();
  }
  function selectionCount(){byId('lit-journals-selection').textContent=draft.size+' of '+sources.length+' selected';}
  function setup(){
    const e=selected();sources=[...new Set([...e.coverage.map(c=>sourceName(c.journal)),...e.articles.map(a=>sourceName(a.journal))])].filter(j=>j!=='Small').sort();
    journals=new Set(sources);topic='';const topics=['',...[...new Set(e.articles.flatMap(a=>a.topics))].sort()];
    document.querySelector('.lit-topics').replaceChildren(...topics.map(t=>{const b=node('button','',t||'All topics');b.type='button';b.dataset.topic=t;b.setAttribute('aria-pressed',String(!t));b.addEventListener('click',()=>{topic=t;render();});return b;}));render();
  }
  const sourcesToggle=byId('lit-sources-toggle'),sourcesPanel=byId('lit-sources-panel');
  sourcesToggle.addEventListener('click',()=>{const open=sourcesToggle.getAttribute('aria-expanded')!=='true';sourcesToggle.setAttribute('aria-expanded',String(open));sourcesPanel.hidden=!open;});
  journalOpen.addEventListener('click',()=>{draft=new Set(journals);paintJournals();dialog.showModal();});
  byId('lit-journals-all').addEventListener('click',()=>{draft=new Set(sources);paintJournals();});
  byId('lit-journals-none').addEventListener('click',()=>{draft.clear();paintJournals();});
  byId('lit-journals-apply').addEventListener('click',()=>{journals=new Set(draft);render();dialog.close();});
  for(const id of ['lit-journals-close','lit-journals-cancel'])byId(id).addEventListener('click',()=>dialog.close());
  search.addEventListener('input',render);sort.addEventListener('change',render);edition.addEventListener('change',setup);
  byId('lit-reset').addEventListener('click',()=>{search.value='';sort.value='relevance';byId('lit-feedback-filter').value='all';setup();search.focus();});
  byId('lit-feedback-filter').addEventListener('change',render);
  byId('lit-feedback-export').addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify({version:1,exportedAt:new Date().toISOString(),entries:Object.values(feedback)},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=node('a');a.href=url;a.download='bioe-radar-feedback-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);feedbackStatus('Exported. Share this file in the research-report chat to update future recommendations.');
  });
  byId('lit-feedback-import').addEventListener('click',()=>byId('lit-feedback-file').click());
  byId('lit-feedback-file').addEventListener('change',async event=>{
    const file=event.target.files[0];if(!file)return;
    try{if(file.size>5000000)throw Error('File is too large.');const incoming=validateFeedback(JSON.parse(await file.text()));for(const [key,entry] of Object.entries(incoming)){if(!feedback[key]||entry.updatedAt>=feedback[key].updatedAt)feedback[key]=entry;}saveFeedback();render();feedbackStatus('Imported feedback. '+Object.keys(feedback).length+' articles saved in this browser.');}catch(error){feedbackStatus('Could not import: '+error.message);}finally{event.target.value='';}
  });
  window.addEventListener('storage',event=>{if(event.key===feedbackKey){try{feedback=event.newValue?validateFeedback(JSON.parse(event.newValue)):Object.create(null);render();feedbackStatus();}catch(error){feedbackStatus('Could not read feedback from another tab.');}}});
  feedbackStatus();
  // Anchor the recurring schedule in Beijing, then derive both DST-sensitive cities.
  const now=new Date(),parts=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  const part=t=>Number(parts.find(p=>p.type===t).value),day=new Date(Date.UTC(part('year'),part('month')-1,part('day')));
  let next=new Date(day.getTime()+((5-day.getUTCDay()+7)%7)*86400000-4.5*3600000);
  if(next<=now)next=new Date(next.getTime()+7*86400000);
  byId('lit-schedule-times').textContent=[['Asia/Shanghai','Beijing'],['America/New_York','New York'],['Europe/London','London']].map(([timeZone,city])=>new Intl.DateTimeFormat('en-GB',{timeZone,weekday:'long',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(next)+' '+city).join(' / ');
  setup();
})();
