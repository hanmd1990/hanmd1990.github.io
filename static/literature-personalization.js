(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.BioERadarPersonalization=factory();})(typeof window==='object'?window:this,function(){
  'use strict';
  const key=a=>String(a.doi||a.id).trim().toLowerCase().replace(/^https?:\/\/(?:dx\.)?doi\.org\//,'').replace(/(10\.21203\/.*|10\.1101\/.*)\/v\d+$/,'$1');
  const stop=new Set('a an the of for to in on and or with by from as is are was were this that these those we our using via into study new based'.split(' '));
  const terms=a=>[...new Set(((a.title||'')+' '+(a.summary||'')).toLowerCase().match(/[a-z][a-z0-9-]{2,}/g)||[])].filter(t=>!stop.has(t));
  function rank(articles,feedback={},history=articles){
    const docs=new Map(history.map(a=>[key(a),a]));articles.forEach(a=>docs.set(key(a),a));
    const sets=new Map([...docs].map(([k,a])=>[k,terms(a)])),df=new Map();
    sets.forEach(ts=>ts.forEach(t=>df.set(t,(df.get(t)||0)+1)));
    const vectors=new Map([...sets].map(([k,ts])=>{const v=new Map(ts.map(t=>[t,Math.log((docs.size+1)/((df.get(t)||0)+1))+1]));return[k,{v,n:Math.hypot(...v.values())||1}];}));
    const training=Object.entries(feedback).filter(([k,f])=>docs.has(k)&&f.signals?.length).map(([k,f])=>[k,f.signals.includes('irrelevant')?-1:(f.signals.includes('more')?2:0)+(f.signals.includes('useful')?1:0)]);
    const scored=articles.map(a=>{
      const k=key(a),v=vectors.get(k),own=feedback[k]?.signals||[];let total=0,weight=0;
      for(const [other,w] of training){if(other===k)continue;const b=docs.get(other),u=vectors.get(other);let dot=0;v.v.forEach((n,t)=>dot+=n*(u.v.get(t)||0));const tags=new Set(b.topics||[]),ats=a.topics||[],overlap=ats.filter(t=>tags.has(t)).length/Math.max(1,new Set([...ats,...tags]).size);const similarity=.8*dot/(v.n*u.n)+.2*overlap;total+=w*similarity;weight+=Math.abs(w);}
      const adjustment=Math.max(-1.5,Math.min(1.5,weight?3*total/weight:0));
      return{article:a,score:(Number(a.relevance)||0)+adjustment+(own.includes('more')?.5:0)+(own.includes('useful')?.35:0),negative:own.includes('irrelevant')};
    });
    return scored.sort((a,b)=>Number(a.negative)-Number(b.negative)||b.score-a.score||a.article.title.localeCompare(b.article.title)).map(x=>x.article);
  }
  return{key,rank};
});
