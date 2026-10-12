import fs from 'node:fs/promises';
import path from 'node:path';
const root='outputs/hmd-lab-site',report=JSON.parse(await fs.readFile('work/mirror-report.json'));
for(const a of report.assets.filter(x=>x.error?.includes('timeout'))){try{const r=await fetch(a.url,{signal:AbortSignal.timeout(15000)});if(r.ok){await fs.writeFile(path.join(root,a.file),Buffer.from(await r.arrayBuffer()));delete a.error;report.failures=report.failures.filter(x=>x.url!==a.url);}}catch{}}
const map=new Map(report.assets.filter(a=>!a.error).map(a=>[a.url,'/'+a.file]));
function walk(o){if(typeof o==='string'){try{return map.get(new URL(o,'https://hmd-lab.com').href)||o;}catch{return o;}}if(Array.isArray(o))return o.map(walk);if(o&&typeof o==='object')for(const k of Object.keys(o))o[k]=walk(o[k]);return o;}
for(const a of report.assets.filter(a=>a.url.includes('/dollars/')&&!a.error)){const file=path.join(root,a.file);const text=await fs.readFile(file,'utf8');const d=walk(JSON.parse(text.replace(/^window\.\$S\s*=\s*/,'')));d.conf.is_google_analytics_enabled=false;d.conf.is_strikingly_analytics_enabled=false;await fs.writeFile(file,'window.$S = '+JSON.stringify(d));}
// Keep optional vendor decorations at their original CDN URL when not mirrored.
for(const f of await fs.readdir(path.join(root,'vendor'))){const file=path.join(root,'vendor',f);let text=await fs.readFile(file,'utf8');text=text.replace(/\b[a-zA-Z_$][\w$]*\.p\+"([^"]+)"/g,(all,p)=>JSON.stringify(new URL(p,'https://static-assets.sxlcdn.com/webpack/').href));await fs.writeFile(file,text);}
await fs.writeFile('work/mirror-report.json',JSON.stringify(report,null,2));
console.log('Remaining resource failures',report.failures.length);

