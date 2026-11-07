"""Headless browser E2E with real FastAPI+SQLite backing; intercepts network due sandbox localhost restriction."""
from pathlib import Path
import json, tempfile,sys
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

root=Path(__file__).resolve().parents[1]
server.DBFILE=str(root/'data'/'browser_test.sqlite3')
Path(server.DBFILE).unlink(missing_ok=True)
client=TestClient(server.app)
client.__enter__()

def backend_fetch(source,url,options=None):
    if url is None:
        return {'status':500,'body':'{}'}
    options=options or {}
    method=options.get('method','GET')
    headers=options.get('headers',{})
    body=options.get('body')
    response=client.request(method,url,headers=headers,content=body)
    return {'status':response.status_code,'body':response.text}

html=(root/'static'/'index.html').read_text().replace('<link rel="stylesheet" href="/static/styles.css" />','').replace('<script src="/static/app.js" defer></script>','')
script=(root/'static'/'app.js').read_text()
css=(root/'static'/'styles.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');",'')

with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
 page=ctx.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.expose_binding('backendFetch',backend_fetch)
 page.set_content(html)
 page.add_style_tag(content=css)
 page.evaluate("window.fetch=async (url,opts={})=>{let r=await window.backendFetch(url,opts);return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})}")
 page.add_script_tag(content=script)
 page.wait_for_selector('.hero-card',timeout=12000)
 print('Initial heading:',page.locator('h1').inner_text().replace('\n',' '))
 print('Initial blockers:',page.locator('.hero-metric strong').inner_text())
 assert 'The work between' in page.locator('h1').inner_text()
 page.screenshot(path=str(root/'docs'/'launchlab-desktop.png'),full_page=True)
 # Criterion editing (UI and API), review, signature.
 page.locator('[data-route="configuration"]').click()
 page.locator('[data-open="criterion"][data-id="CR-02"]').click()
 page.locator('#description').fill('Explains customer implementation blockers clearly and documents actionable follow-up steps with responsible owners.')
 page.locator('form#modalForm button[type=submit]').click()
 page.wait_for_function("document.querySelector('#store-status').textContent.includes('v1')")
 assert not errors,errors
 page.locator('[data-action="review_criterion"][data-id="CR-02"]').click()
 page.wait_for_function("document.querySelector('#store-status').textContent.includes('v2')")
 page.locator('[data-action="approve_icp"]').click()
 page.wait_for_function("document.querySelector('#store-status').textContent.includes('v3')")
 page.screenshot(path=str(root/'docs'/'launchlab-configuration.png'),full_page=True)
 # Record all integration pass notes
 page.locator('[data-route="readiness"]').click()
 page.locator('[data-action="run_mapping_test"]').click();page.wait_for_function("document.querySelector('#store-status').textContent.includes('v4')")
 for n,id in enumerate(['INT-02','INT-03'],start=5):
  page.locator(f'[data-open="integration"][data-id="{id}"]').click()
  page.locator('#evidence').fill('Simulated verification completed against role mapping and test records.')
  page.locator('form#modalForm button[type=submit]').click()
  page.wait_for_function(f"document.querySelector('#store-status').textContent.includes('v{n}')")
 page.locator('[data-route="enablement"]').click()
 for n,id in enumerate(['TR-02','TR-03'],start=7):
  page.locator(f'[data-open="training"][data-id="{id}"]').click()
  page.locator('#proof').fill('Fictional learner completed the required dry-run and explained the result.')
  page.locator('form#modalForm button[type=submit]').click()
  page.wait_for_function(f"document.querySelector('#store-status').textContent.includes('v{n}')")
 for n,id,value in [(9,'recruiters',4),(10,'managers',2)]:
  page.locator(f'[data-open="trained"][data-id="{id}"]').click()
  page.locator('#value').fill(str(value))
  page.locator('form#modalForm button[type=submit]').click()
  page.wait_for_function(f"document.querySelector('#store-status').textContent.includes('v{n}')")
 page.locator('[data-route="readiness"]').click()
 assert page.locator('text=READY TO PILOT').count()>=1
 page.locator('[data-action="launch_pilot"]').click()
 page.wait_for_function("document.querySelector('#store-status').textContent.includes('v11')")
 page.locator('[data-route="adoption"]').click()
 page.screenshot(path=str(root/'docs'/'launchlab-adoption.png'),full_page=True)
 assert 'Pilot active' in page.content() or 'PILOT ACTIVE' in page.content()
 # Record an intervention; usage must not change from 4/11 baseline.
 page.locator('[data-open="intervention"]').click();page.locator('#note').fill('Coach managers using two candidate profile review examples.')
 page.locator('form#modalForm button[type=submit]').click();page.wait_for_function("document.querySelector('#store-status')?.textContent.includes('v12')")
 assert '4/11' in page.locator('main').inner_text()
 # Real changes require separate simulated observation.
 for n,id,value in [(13,'recruiters',5),(14,'managers',2),(15,'ops',1)]:
  page.locator(f'[data-open="usage"][data-id="{id}"]').click()
  page.locator('#count').fill(str(value))
  page.locator('form#modalForm button[type=submit]').click()
  page.wait_for_function(f"document.querySelector('#store-status').textContent.includes('v{n}')")
 page.locator('[data-route="handover"]').click()
 assert 'Met (simulated)' in page.locator('main').inner_text()
 page.locator('[data-action="handover"]').click()
 page.wait_for_function("document.querySelector('#store-status').textContent.includes('v16')")
 assert 'HANDOVER RECORDED' in page.locator('main').inner_text()
 page.set_content(html);page.add_style_tag(content=css);page.add_script_tag(content=script);page.wait_for_selector('.hero-card',timeout=12000);assert 'Saved · v16' in page.locator('#store-status').inner_text()
 assert 'Saved · v16' in page.locator('#store-status').inner_text()
 print('Full workflow + reload persisted across 16 revisions; JS errors:',errors)
 assert not errors,errors
 mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1)
 m=mobile.new_page();m.expose_binding('backendFetch',backend_fetch);m.set_content(html);m.add_style_tag(content=css);m.evaluate("window.fetch=async (url,opts={})=>{let r=await window.backendFetch(url,opts);return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})}");m.add_script_tag(content=script);m.wait_for_selector('.hero-card',timeout=12000)
 m.screenshot(path=str(root/'docs'/'launchlab-mobile.png'),full_page=True)
 overflow=m.evaluate('document.documentElement.scrollWidth > window.innerWidth')
 print('Mobile horizontal overflow:',overflow)
 assert not overflow
 browser.close()
client.__exit__(None,None,None)
