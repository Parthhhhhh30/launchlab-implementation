"""Actual desktop/mobile Chromium + SQLite + mocked model transport.
Mocked inference is never represented as a live provider validation.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
from fastapi.testclient import TestClient
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
from test_ai_lab import synthetic_provider_data
ROOT=Path(__file__).resolve().parents[1]
server.DBFILE=str(ROOT/'data'/'ai_browser_test.sqlite3')
Path(server.DBFILE).unlink(missing_ok=True)
os.environ['GEMINI_API_KEY']='FAKE_TEST_ONLY_NO_NETWORK'
server.invoke_gemini=lambda key,prompt: server.ai_lab_test_provider(prompt)
server.ai_lab_test_provider=lambda prompt: __import__('ai_lab').invoke_gemini('FAKE',prompt,transport=lambda *args:synthetic_provider_data('refined' if 'Distinguish owning work' in prompt else 'baseline'))
client=TestClient(server.app);client.__enter__()
html=(ROOT/'static'/'agent-lab.html').read_text().replace('<link rel="stylesheet" href="/static/experience.css">','').replace('<link rel="stylesheet" href="/static/agent-lab.css">','').replace('<script src="/static/agent-lab.js" defer></script>','')
css=(ROOT/'static'/'experience.css').read_text()+(ROOT/'static'/'agent-lab.css').read_text()
css=__import__('re').sub(r'@import\s+url\([^;]*;', '', css)
js=(ROOT/'static'/'agent-lab.js').read_text()

def inject(page):
    def bridge(source,url,opts=None):
        opts=opts or {}
        response=client.request(opts.get('method','GET'),url,headers=opts.get('headers',{}),content=opts.get('body'))
        return {'status':response.status_code,'body':response.text}
    page.expose_binding('bridge',bridge)
    page.set_content(html)
    page.add_style_tag(content=css)
    page.evaluate("(()=>{window.fetch=async (url,opts={})=>{const r=await window.bridge(url,opts);return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})};return true})()")
    page.add_script_tag(content=js)

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':950},reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    inject(page)
    page.get_by_text('LIVE FREE-TIER MODEL READY').wait_for()
    assert page.locator('.case-item').count()==6
    page.locator('#run-model').click()
    page.get_by_text('Recorded baseline evaluation').wait_for()
    assert page.locator('#results-score').inner_text()=='4 / 6'
    page.locator('[data-version="refined"]').click()
    page.locator('#run-model').click()
    page.get_by_text('Recorded refined evaluation').wait_for()
    assert page.locator('#results-score').inner_text()=='6 / 6'
    assert 'VERSION A / 4/6' in page.locator('#comparison-strip').inner_text()
    assert 'VERSION B / 6/6' in page.locator('#comparison-strip').inner_text()
    page.screenshot(path=str(ROOT/'docs'/'agent-lab-desktop.png'),full_page=True)
    page.set_content(html);page.add_style_tag(content=css);page.add_script_tag(content=js)
    page.get_by_text('LIVE FREE-TIER MODEL READY').wait_for()
    assert '6/6' in page.locator('#comparison-strip').inner_text()
    assert not errors,errors
    m=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    inject(m)
    m.get_by_text('LIVE FREE-TIER MODEL READY').wait_for()
    assert m.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),'Mobile overflow'
    m.screenshot(path=str(ROOT/'docs'/'agent-lab-mobile.png'),full_page=True)
    print('Desktop real browser + mocked model + database persistence + mobile 390px: PASS')
    browser.close()
client.__exit__(None,None,None)
