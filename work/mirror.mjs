import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve('outputs/hmd-lab-site');
const origin='https://hmd-lab.com';
await fs.mkdir(root,{recursive:true});
const pages=new Map(), assets=new Map(), failures=[];
const decode=s=>s.replaceAll('&amp;','&').replaceAll('&gt;','>').replaceAll('&lt;','<').replaceAll('&#39;',"'").replaceAll('&quot;','"');
const localHost=h=>['hmd-lab.com','www.hmd-lab.com'].includes(h);
async function fetchBytes(url){let error;for(let n=0;n<3;n++){try{const r=await fetch(url,{signal:AbortSignal.timeout(45000)});if(!r.ok)throw Error('HTTP '+r.status);return {data:Buffer.from(await r.arrayBuffer()),type:r.headers.get('content-type')||''};}catch(e){error=e;}}throw error;}
const queue=['/'];
while(queue.length){const batch=queue.splice(0,5);await Promise.all(batch.map(async route=>{if(pages.has(route))return;pages.set(route,null);try{const {data,type}=await fetchBytes(origin+route);if(!type.includes('html'))throw Error('Not HTML: '+type);const html=data.toString();pages.set(route,html);for(const m of html.matchAll(/\bhref\s*=\s*['"]([^'"]+)['"]/gi)){try{const u=new URL(decode(m[1]),origin+route);const p=u.pathname.replace(/\/$/,'')||'/';if(localHost(u.hostname)&&!p.startsWith('/dollars/')&&!p.startsWith('/pages/')&&!path.extname(p)&&!pages.has(p)&&!queue.includes(p))queue.push(p);}catch{}}console.log('Page '+route);}catch(e){failures.push({url:origin+route,error:e.message});}}));}
function addAsset(raw,base){try{const u=new URL(decode(raw),base);if(!['https:','http:'].includes(u.protocol))return;u.hash='';if(!(/sxlcdn\.com$/.test(u.hostname)||/strikinglycdn\.com$/.test(u.hostname)||localHost(u.hostname)&&u.pathname.startsWith('/dollars/')))return;if(u.pathname==='/'&&!u.search)return;const url=u.href;if(!assets.has(url)){let ext=path.extname(u.pathname);if(!/^\.[a-z0-9]{1,6}$/i.test(ext))ext=u.pathname==='/css'?'.css':'.bin';const file='assets/'+crypto.createHash('sha256').update(url).digest('hex').slice(0,20)+ext;assets.set(url,{url,file,raws:new Set([raw]),done:false});}else assets.get(url).raws.add(raw);return assets.get(url);}catch{}}
function scan(text,base){for(const m of text.matchAll(/(?:https?:)?\/\/(?:[a-z0-9.-]+\.)?(?:sxlcdn\.com|strikinglycdn\.com)\/[^\s"'<>\\)]+/gi))addAsset(m[0],base);for(const m of text.matchAll(/(?:src|href)\s*=\s*['"]([^'"]+)['"]/gi))if(m[1].startsWith('/dollars/'))addAsset(m[1],base);}
for(const [route,h] of pages)if(h)scan(h,origin+route);
while([...assets.values()].some(a=>!a.done)){const pending=[...assets.values()].filter(a=>!a.done).slice(0,8);await Promise.all(pending.map(async a=>{a.done=true;try{const r=await fetchBytes(a.url);a.data=r.data;a.type=r.type;if(r.type.includes('text/css')||a.file.endsWith('.css')){a.text=r.data.toString();for(const m of a.text.matchAll(/url\(\s*['"]?([^)'"\s]+)['"]?\s*\)/g))addAsset(m[1],a.url);}console.log('Asset '+assets.size+' '+a.file+' '+r.data.length);}catch(e){a.error=e.message;failures.push({url:a.url,error:e.message});}}));}
function rewrite(text,base){return text.replace(/(?:https?:)?\/\/(?:[a-z0-9.-]+\.)?(?:sxlcdn\.com|strikinglycdn\.com)\/[^\s"'<>\\)]+/gi,raw=>{const a=addAsset(raw,base);return a?.data?'/'+a.file:raw;}).replace(/((?:src|href)\s*=\s*['"])(\/dollars\/[^'"]+)/gi,(all,p,raw)=>{const a=addAsset(raw,base);return a?.data?p+'/'+a.file:all;});}
for(const a of assets.values()){if(!a.data)continue;let data=a.data;if(a.text)data=a.text.replace(/url\(\s*['"]?([^)'"\s]+)['"]?\s*\)/g,(all,raw)=>{const v=addAsset(raw,a.url);return v?.data?'url(/'+v.file+')':all;});await fs.mkdir(path.dirname(path.join(root,a.file)),{recursive:true});await fs.writeFile(path.join(root,a.file),data);}
for(const [route,html] of pages){if(!html)continue;let h=rewrite(html,origin+route);h=h.replace(/(href\s*=\s*['"])https?:\/\/(?:www\.)?hmd-lab\.com(?=[/'"])/gi,'$1').replace(/(href\s*=\s*['"])(['"])/gi,'$1/$2');const file=path.join(root,route==='/'?'index.html':route.slice(1)+'/index.html');await fs.mkdir(path.dirname(file),{recursive:true});await fs.writeFile(file,h);}
await fs.writeFile(path.join(root,'.nojekyll'),'');
await fs.writeFile('work/mirror-report.json',JSON.stringify({pages:[...pages].filter(x=>x[1]).map(x=>x[0]),assets:[...assets.values()].map(({url,file,error})=>({url,file,error})),failures},null,2));
console.log(JSON.stringify({pages:pages.size,assets:assets.size,failures},null,2));

