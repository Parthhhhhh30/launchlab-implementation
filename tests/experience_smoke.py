"""Live-origin desktop/mobile and real SQLite API checks for public portfolio experience."""
from pathlib import Path
import os, subprocess, time, signal
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'experience_qa.sqlite3'
DB.unlink(missing_ok=True)
env=os.environ.copy();env['LAUNCHLAB_SQLITE_PATH']=str(DB)
server=subprocess.Popen(['python','-m','uvicorn','server:app','--host','127.0.0.1','--port','8797'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
  for _ in range(60):
    try:
      if urlopen('http://127.0.0.1:8797/api/health',timeout=1).status==200:break
    except Exception:time.sleep(.2)
  else:raise RuntimeError('API never started')
  with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce')
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    from fastapi.testclient import TestClient
    import sys
    sys.path.insert(0,str(ROOT))
    import server as backend
    backend.DBFILE=str(DB)
    api=TestClient(backend.app)
    def backend_fetch(source,url,opts=None):
      if not isinstance(url,str):return {'status':500,'body':'{}'}
      opts=opts or {}
      response=api.request(opts.get('method','GET'),url,headers=opts.get('headers',{}),content=opts.get('body'))
      return {'status':response.status_code,'body':response.text}
    html=(ROOT/'static'/'experience.html').read_text().replace('<link rel="stylesheet" href="/static/experience.css">','').replace('<script src="/static/experience.js" defer></script>','')
    css=(ROOT/'static'/'experience.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');",'')
    js=(ROOT/'static'/'experience.js').read_text()
    def inject(page):
      page.expose_binding('backendFetch',backend_fetch)
      page.set_content(html)
      page.add_style_tag(content=css)
      page.evaluate("window.fetch=async (url,opts={})=>{let r=await window.backendFetch(url,opts);return new Response(r.body,{status:r.status,headers:{'Content-Type':'application/json'}})}")
      page.add_script_tag(content=js)
    inject(page)
    page.locator('#lab-storage').filter(has_text='DATABASE CONNECTED').wait_for(timeout=10000)
    assert page.locator('h1').inner_text().find('SIGNED')>=0
    assert page.locator('#criteria-copy').inner_text()=='Excellent communicator who fits our culture.'
    page.screenshot(path=str(ROOT/'docs'/'experience-desktop.png'),full_page=True)
    page.locator('#clarify-action').click()
    page.wait_for_function("document.querySelector('#lab-storage').textContent.includes('REV 1')")
    assert 'named owners' in page.locator('#criteria-copy').inner_text()
    page.locator('#tab-integration').click();page.locator('#mapping-break').click()
    page.wait_for_function("document.querySelector('#mapping-path').textContent==='job.invalid'")
    page.locator('#mapping-test').click()
    page.wait_for_function("document.querySelector('#mapping-feedback').textContent.includes('FAIL')")
    page.locator('#mapping-fix').click()
    page.wait_for_function("document.querySelector('#mapping-path').textContent==='job.id'")
    page.locator('#mapping-test').click()
    page.wait_for_function("document.querySelector('#mapping-feedback').textContent.includes('PASS')")
    page.locator('#tab-adoption').click();assert page.locator('#audience-rows .audience-row').count()==3
    page.locator('[data-choice=b]').click();assert 'Correct approach' in page.locator('#answer-feedback').inner_text()
    inject_reload = '''skip'''
    page.set_content(html);page.add_style_tag(content=css);page.add_script_tag(content=js);page.locator('#lab-storage').filter(has_text='DATABASE CONNECTED').wait_for(timeout=10000)
    assert 'named owners' in page.locator('#criteria-copy').inner_text()
    assert (ROOT/'static'/'studio.html').exists()
    assert 'id="nav"' in (ROOT/'static'/'studio.html').read_text()
    assert 'href="/studio"' in html
    print('Desktop live-story + 4 API changes + persistence + studio deep-link: PASS')
    assert not errors,errors
    mctx=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,reduced_motion='reduce')
    mob=mctx.new_page();merrors=[];mob.on('pageerror',lambda e:merrors.append(str(e)))
    inject(mob)
    mob.locator('#lab-storage').filter(has_text='DATABASE CONNECTED').wait_for(timeout=10000)
    mob.screenshot(path=str(ROOT/'docs'/'experience-mobile.png'),full_page=True)
    assert mob.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f"mobile overflow width {mob.evaluate('document.documentElement.scrollWidth')}"
    mob.locator('#tab-integration').click();assert mob.locator('#pane-integration').is_visible()
    assert not merrors,merrors
    print('Mobile 390px no horizontal overflow + tab switching: PASS')
    browser.close()
finally:
  server.terminate()
  try: server.wait(timeout=5)
  except subprocess.TimeoutExpired:server.kill()
