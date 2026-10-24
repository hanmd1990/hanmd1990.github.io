// Local UI contract test: account adapter is stubbed; no production data is used.
// NODE_PATH must expose playwright and @sparticuz/chromium for this optional check.
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http');
test('sign-in, feedback, undo and clearing private UI on sign-out',async()=>{
 const {chromium}=require('playwright'),bundle=await import(require.resolve('@sparticuz/chromium'));
 const root=path.resolve(process.env.BIOE_TEST_SITE||'../output-account');
 const server=http.createServer((req,res)=>{try{const p=path.join(root,new URL(req.url,'http://local').pathname);const file=fs.statSync(p).isDirectory()?path.join(p,'index.html'):p;res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.statusCode=404;res.end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,executablePath:process.env.BIOE_TEST_CHROMIUM||'/tmp/chromium',args:bundle.default.args});
 try{
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/static/literature-account.js*',route=>route.fulfill({contentType:'application/javascript',body:`(()=>{let state={status:'signed-out',user:null,feedback:{},message:'Signed out'},listeners=[];const emit=()=>listeners.forEach(fn=>fn(state));window.BioERadarAccount={subscribe(fn){listeners.push(fn);fn(state)},signIn(){state={status:'signed-in',user:{uid:'alice',displayName:'Alice'},feedback:{},message:'Synced'};emit()},signOut(){state={status:'signed-out',user:null,feedback:{},message:'Signed out'};emit()},async save(entry){state.feedback={...state.feedback,[entry.key]:entry};emit();return true},getState(){return state}}})();`}));
  await page.goto('http://127.0.0.1:'+server.address().port+'/literature/');
  await page.getByRole('button',{name:'Sign in with Google',exact:true}).waitFor();
  assert.equal(await page.locator('.lit-paper').count(),52);
  assert.equal(await page.getByRole('button',{name:'Useful',exact:true}).first().isEnabled(),false);
  await page.getByRole('button',{name:'Sign in with Google',exact:true}).click();
  assert.equal(await page.locator('#lit-sort').inputValue(),'personal');
  const first=page.locator('.lit-paper').first(),id=await first.getAttribute('data-id');
  await first.getByRole('button',{name:'Useful',exact:true}).click();
  let card=page.locator('.lit-paper').filter({has:page.locator('[data-signal="useful"][aria-pressed="true"]')});
  assert.equal(await card.count(),1);await card.getByRole('button',{name:'More like this',exact:true}).click();
  await card.getByRole('button',{name:'Not relevant',exact:true}).click();
  card=page.locator('.lit-paper').filter({has:page.locator('[data-signal="irrelevant"][aria-pressed="true"]')});
  assert.equal(await card.getByRole('button',{name:'Useful',exact:true}).getAttribute('aria-pressed'),'false');
  await page.locator('#lit-feedback-filter').selectOption('marked');assert.equal(await page.locator('.lit-paper').count(),1);
  await card.getByRole('button',{name:'Not relevant',exact:true}).click();assert.equal(await page.locator('.lit-paper').count(),0);
  await page.locator('#lit-feedback-filter').selectOption('all');
  await page.getByRole('button',{name:'Sign out',exact:true}).click();
  assert.equal(await page.locator('.lit-paper').count(),52);assert.equal(await page.locator('#lit-sort').inputValue(),'relevance');
  assert.equal(await page.locator('[aria-pressed="true"][data-signal]').count(),0);
  assert.equal(await page.getByRole('button',{name:'Useful',exact:true}).first().isEnabled(),false);
  assert.equal(await page.locator('#lit-feedback-export').count(),0);assert.deepEqual(errors,[]);
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
});
