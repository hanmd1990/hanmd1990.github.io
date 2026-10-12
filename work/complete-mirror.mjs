import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve('outputs/hmd-lab-site'), origin='https://hmd-lab.com';
const report=JSON.parse(await fs.readFile('work/mirror-report.json'));
const assets=new Map(report.assets.map(a=>[a.url,a]));
const failures=[];
const decode=s=>s.replaceAll('&amp;','&').replaceAll('&gt;','>').replaceAll('\\u003e','>');
async function bytes(url){const r=await fetch(url,{signal:AbortSignal.timeout(40000)});if(!r.ok)throw Error('HTTP '+r.status);return Buffer.from(await r.arrayBuffer());}
const dataAssets=report.assets.filter(a=>a.url.includes('/dollars/'));
const data=JSON.parse((await fs.readFile(path.join(root,dataAssets[0].file),'utf8')).replace(/^window\.\$S\s*=\s*/,''));
const pageJobs=data.nav.filter(p=>!p.isHomePage&&!p.memberOnly&&!p.hasPassword&&!report.pages.includes(p.name));
for(const p of pageJobs){const html=(await bytes(origin+p.name)).toString();await fs.mkdir(path.join(root,p.name),{recursive:true});await fs.writeFile(path.join(root,p.name,'index.html'),html);report.pages.push(p.name);console.log('Added page '+p.name);}
const tasks=[];
function add(raw){try{const u=new URL(decode(raw),origin);if(!u.hostname.endsWith('sxlcdn.com')&&!(u.hostname==='hmd-lab.com'&&u.pathname.startsWith('/dollars/')))return;u.hash='';if(u.pathname==='/')return;const url=u.href;if(assets.has(url))return assets.get(url);let ext=path.extname(u.pathname);if(!/^\.[a-z0-9]{1,6}$/i.test(ext))ext=u.pathname==='/css'?'.css':'.bin';const a={url,file:'assets/'+crypto.createHash('sha256').update(url).digest('hex').slice(0,20)+ext};assets.set(url,a);tasks.push(a);return a;}catch{}}
const regex=/(?:https?:)?\/\/[a-z0-9.-]+\.sxlcdn\.com\/[^\s"'<>\\)]+/gi;
for(const route of report.pages){const h=await fs.readFile(path.join(root,route==='/'?'index.html':route+'/index.html'),'utf8');for(const m of h.matchAll(regex))add(m[0]);for(const m of h.matchAll(/src=['"](\/dollars\/[^'"]+)/g))add(m[1]);}
function walk(o,fn){if(typeof o==='string')return fn(o);if(Array.isArray(o))return o.map(v=>walk(v,fn));if(o&&typeof o==='object')for(const k of Object.keys(o))o[k]=walk(o[k],fn);return o;}
walk(data,s=>{if(/^(?:https?:)?\/\/.*sxlcdn\.com\//.test(s))add(s);return s;});
while(tasks.length){const batch=tasks.splice(0,8);await Promise.all(batch.map(async a=>{try{const b=await bytes(a.url);await fs.writeFile(path.join(root,a.file),b);if(a.file.endsWith('.css'))for(const m of b.toString().matchAll(/url\(['"]?([^)'"\s]+)/g))add(new URL(m[1],a.url).href);}catch(e){a.error=e.message;failures.push(a);}}));console.log('Supplement assets remaining '+tasks.length);}
const bundle=report.assets.find(a=>a.url.includes('page-site-bundle'));
let source=await fs.readFile(path.join(root,bundle.file),'utf8');
const chunkMap=source.match(/u\.u=function\(t\)\{return t\+"\."\+\{([^}]+)\}/)?.[1];
if(!chunkMap)throw Error('Cannot identify webpack chunk manifest');
const chunks=[...chunkMap.matchAll(/(\d+):"([a-f0-9]+)"/g)].map(m=>m[1]+'.'+m[2]+'-site-bundle.js');
await fs.mkdir(path.join(root,'vendor'),{recursive:true});
while(chunks.length){const batch=chunks.splice(0,8);await Promise.all(batch.map(async name=>{try{await fs.writeFile(path.join(root,'vendor',name),await bytes('https://static-assets.sxlcdn.com/webpack/'+name));}catch(e){failures.push({url:name,error:e.message});}}));console.log('Runtime chunks remaining '+chunks.length);}
if(!failures.some(a=>a.url.endsWith('-site-bundle.js')))await fs.writeFile(path.join(root,bundle.file),source.replace('u.p="https://static-assets.sxlcdn.com/webpack/"','u.p="/vendor/"'));
function replacement(raw){try{const a=assets.get(new URL(decode(raw),origin).href);return a&&!a.error?'/'+a.file:raw;}catch{return raw;}}
for(const a of assets.values()){if(a.error)continue;if(a.url.includes('/dollars/')){const text=await fs.readFile(path.join(root,a.file),'utf8');let d=JSON.parse(text.replace(/^window\.\$S\s*=\s*/,''));d=walk(d,s=>replacement(s)!==s?replacement(s):s.replace(regex,replacement));await fs.writeFile(path.join(root,a.file),'window.$S = '+JSON.stringify(d));}else if(a.file.endsWith('.css')){let text=await fs.readFile(path.join(root,a.file),'utf8');text=text.replace(/url\(['"]?([^)'"\s]+)['"]?\)/g,(all,s)=>{if(s.startsWith('/assets/'))return all;const v=replacement(new URL(s,a.url).href);return v.startsWith('/assets/')?'url('+v+')':all;});await fs.writeFile(path.join(root,a.file),text);}}
for(const route of report.pages){const file=path.join(root,route==='/'?'index.html':route+'/index.html');let h=await fs.readFile(file,'utf8');h=h.replace(regex,replacement).replace(/(src=['"])(\/dollars\/[^'"]+)/g,(_,prefix,s)=>prefix+replacement(s));h=h.replace(/(href\s*=\s*['"])https?:\/\/(?:www\.)?hmd-lab\.com(?=[/'"])/gi,'$1');h=h.replace('</body>','<script src="/migration-navigation.js"></script></body>');await fs.writeFile(file,h);}
await fs.writeFile(path.join(root,'migration-navigation.js'),`// Use real static pages rather than the original platform's page API.\ndocument.addEventListener('click',function(e){const a=e.target.closest('a[href]');if(!a||e.button!==0||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||a.target==='_blank'||a.hasAttribute('download'))return;const u=new URL(a.href,location.href);if(![location.hostname,'hmd-lab.com','www.hmd-lab.com'].includes(u.hostname))return;if(u.pathname===location.pathname&&u.hash)return;e.preventDefault();e.stopImmediatePropagation();location.assign(u.pathname+u.search+u.hash);},true);\n`);
await fs.mkdir(path.join(root,'home'),{recursive:true});await fs.writeFile(path.join(root,'home/index.html'),'<meta http-equiv="refresh" content="0;url=/"><a href="/">Home</a>');
report.assets=[...assets.values()];report.failures.push(...failures);await fs.writeFile('work/mirror-report.json',JSON.stringify(report,null,2));console.log(JSON.stringify({pages:report.pages.length,assets:assets.size,newFailures:failures},null,2));

