from __future__ import annotations
from contextlib import contextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os, json, sqlite3, uuid, secrets, hashlib, time
from pathlib import Path
from domain import seed, act, assess, adoption

BASE=Path(__file__).parent
DBFILE=os.environ.get('LAUNCHLAB_SQLITE_PATH',str(BASE/'data'/'launchlab.sqlite3'))
URL=os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
app=FastAPI(title='LaunchLab • AI implementation & adoption case',docs_url=None,redoc_url=None,openapi_url=None)
app.mount('/static',StaticFiles(directory=str(BASE/'static')),name='static')

@contextmanager
def connect():
    if URL:
        import psycopg
        with psycopg.connect(URL,connect_timeout=10,autocommit=False) as conn:
            yield conn,'postgres'
    else:
        os.makedirs(Path(DBFILE).parent,exist_ok=True)
        with sqlite3.connect(DBFILE,timeout=10,isolation_level=None) as conn:
            conn.execute('PRAGMA busy_timeout=10000')
            conn.execute('PRAGMA journal_mode=WAL')
            yield conn,'sqlite'

def initialize():
    with connect() as (conn,kind):
        cur=conn.cursor()
        if kind=='postgres':
            cur.execute('CREATE TABLE IF NOT EXISTS launchlab_workspaces (id VARCHAR(72) PRIMARY KEY, document JSONB NOT NULL, updated_at TIMESTAMPTZ DEFAULT NOW())')
        else:
            cur.execute('CREATE TABLE IF NOT EXISTS launchlab_workspaces (id TEXT PRIMARY KEY, document TEXT NOT NULL, updated_at TEXT NOT NULL)')
        conn.commit()

def load(token):
    with connect() as (conn,kind):
        q='SELECT document FROM launchlab_workspaces WHERE id = %s' if kind=='postgres' else 'SELECT document FROM launchlab_workspaces WHERE id = ?'
        row=conn.execute(q,(token,)).fetchone()
        if row is None:return None
        return row[0] if isinstance(row[0],dict) else json.loads(row[0])

def save_new(token,s):
    with connect() as (conn,kind):
        if kind=='postgres': conn.execute('INSERT INTO launchlab_workspaces (id,document) VALUES (%s,%s::jsonb) ON CONFLICT DO NOTHING',(token,json.dumps(s)))
        else: conn.execute('INSERT OR IGNORE INTO launchlab_workspaces (id,document,updated_at) VALUES (?,?,?)',(token,json.dumps(s),str(time.time())))
        conn.commit()

def transact(token,revision,action,data):
    with connect() as (conn,kind):
        if kind=='postgres':
            conn.execute('BEGIN')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=%s FOR UPDATE',(token,)).fetchone()
        else:
            conn.execute('BEGIN IMMEDIATE')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=?',(token,)).fetchone()
        if row is None:raise LookupError('Workspace expired or missing')
        state=row[0] if isinstance(row[0],dict) else json.loads(row[0]);
        if state['revision']!=revision:raise RuntimeError('Workspace changed in another tab. Reload before applying another action.')
        new=act(state,action,data)
        if kind=='postgres':conn.execute('UPDATE launchlab_workspaces SET document=%s::jsonb,updated_at=NOW() WHERE id=%s',(json.dumps(new),token))
        else:conn.execute('UPDATE launchlab_workspaces SET document=?,updated_at=? WHERE id=?',(json.dumps(new),str(time.time()),token))
        conn.commit()
        return new

def _api_response(s):
    return {'state':s,'readiness':assess(s),'adoption':adoption(s),'disclaimer':'Independent synthetic implementation exercise, not affiliated with Metaview. No real ATS connection, applicant data, or AI recruiting decisions.'}

def session_id(request):
    tok=request.cookies.get('launchlab_session','')
    if tok and len(tok)==43 and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in tok):return tok
    return None

def cookie(response,token,request):
    response.set_cookie('launchlab_session',token,httponly=True,secure=request.url.scheme=='https',samesite='lax',max_age=60*60*24*60,path='/')

@app.get('/')
async def index():return FileResponse(str(BASE/'static'/'experience.html'))

@app.get('/studio')
async def studio():return FileResponse(str(BASE/'static'/'studio.html'))

@app.get('/api/workspace')
async def get_workspace(request:Request):
    try:
        initialize()
        token=session_id(request)
        s=load(token) if token else None
        if s is None:
            token=secrets.token_urlsafe(32)
            s=seed();save_new(token,s)
        r=JSONResponse(_api_response(s),headers={'Cache-Control':'no-store'})
        cookie(r,token,request)
        return r
    except Exception as exc:
        # never expose database credentials/stack traces
        return JSONResponse({'error':'Persistent store unavailable. Configure a private DATABASE_URL before using the hosted workspace.'},status_code=503)

@app.post('/api/action')
async def do_action(request:Request):
    if request.headers.get('content-type','').split(';')[0]!='application/json':raise HTTPException(415,'JSON required')
    origin=request.headers.get('origin')
    if origin:
        from urllib.parse import urlparse
        if urlparse(origin).hostname!=request.url.hostname: raise HTTPException(403,'Cross-site request blocked')
    token=session_id(request)
    if token is None:raise HTTPException(401,'Start a workspace first')
    try:payload=await request.json()
    except Exception:raise HTTPException(400,'Invalid JSON')
    if not isinstance(payload,dict) or len(json.dumps(payload))>3000:raise HTTPException(400,'Action payload too large')
    revision=payload.get('revision'); action=payload.get('action'); data=payload.get('data',{})
    if not isinstance(revision,int) or isinstance(revision,bool) or not isinstance(action,str):raise HTTPException(400,'Revision and action required')
    try:
        s=transact(token,revision,action,data)
        return JSONResponse(_api_response(s),headers={'Cache-Control':'no-store'})
    except ValueError as exc:raise HTTPException(422,str(exc))
    except RuntimeError as exc:raise HTTPException(409,str(exc))
    except LookupError as exc:raise HTTPException(404,str(exc))
    except Exception:raise HTTPException(503,'Persistent data store unavailable')

@app.post('/api/reset')
async def reset(request:Request):
    origin=request.headers.get('origin')
    if origin:
        from urllib.parse import urlparse
        if urlparse(origin).hostname!=request.url.hostname:raise HTTPException(403,'Cross-site request blocked')
    try:
        initialize()
        token=secrets.token_urlsafe(32)
        s=seed();save_new(token,s)
        r=JSONResponse(_api_response(s),headers={'Cache-Control':'no-store'})
        cookie(r,token,request)
        return r
    except Exception:raise HTTPException(503,'Persistent data store unavailable')

@app.get('/api/health')
async def health():
    try:
        initialize()
        return {'status':'ok','storage':'postgres' if URL else 'sqlite', 'synthetic':True}
    except Exception:return JSONResponse({'status':'error','storage':'unavailable'},status_code=503)

@app.get('/api/export')
async def export(request:Request):
    token=session_id(request)
    if not token:raise HTTPException(401,'Workspace session required')
    try:s=load(token)
    except Exception:raise HTTPException(503,'Data store unavailable')
    if not s:raise HTTPException(404,'No workspace')
    response=JSONResponse({'workspace':s,'readiness':assess(s),'adoption':adoption(s),'synthetic':True,'note':'This records operator entries, not authenticated reviews or real customer results.'})
    response.headers['Content-Disposition']='attachment; filename="launchlab-synthetic-handover.json"'
    response.headers['Cache-Control']='no-store'
    return response

# MODEL EVALUATION: free-tier-only, server-side key, fixed synthetic cases.
# See ai_lab.py. No external ATS, tools, arbitrary user profiles or applicant records.
from ai_lab import init_lab, public_cases, MODEL, invoke_gemini, now_iso
import asyncio
from datetime import datetime, timezone

AI_MAX_PER_WORKSPACE_DAY = 3
AI_MAX_GLOBAL_DAY = 12

def _safe_origin(request):
    origin=request.headers.get('origin')
    if not origin:return
    from urllib.parse import urlparse
    o=urlparse(origin)
    if o.scheme not in ('http','https') or o.hostname!=request.url.hostname:
        raise HTTPException(403,'Cross-site request blocked')

def _ai_key():
    return os.environ.get('GEMINI_API_KEY','').strip()

@app.get('/agent-lab')
async def ai_lab_page():
    return FileResponse(str(BASE/'static'/'agent-lab.html'))

@app.get('/api/ai/status')
async def ai_status(request:Request):
    tok=session_id(request)
    if not tok:raise HTTPException(401,'Open the site to initialise a workspace')
    try:s=load(tok)
    except Exception:raise HTTPException(503,'Persistent store unavailable')
    if not s:raise HTTPException(404,'Workspace missing')
    import copy
    lab=copy.deepcopy(init_lab(s))
    if lab.get('pending'):
        # A stale lease is displayed as unavailable rather than silently billed again.
        lab['pending']={'status':'running'}
    return JSONResponse({'ai_lab':lab,'cases':public_cases(),'model':MODEL,
                         'available':bool(_ai_key()),'free_tier_only':True,
                         'limits':{'per_workspace_per_day':AI_MAX_PER_WORKSPACE_DAY,'global_per_day':AI_MAX_GLOBAL_DAY},
                         'disclaimer':'Public fictional evidence only. Model responses are QA observations, not applicant decisions.'},
                        headers={'Cache-Control':'no-store'})

def _reserve_model_call(tok, revision, mode):
    """Two atomic quotas and one workspace lease, counted before contacting provider."""
    import copy
    day=datetime.now(timezone.utc).strftime('%Y-%m-%d')
    lease=secrets.token_hex(12)
    with connect() as (conn,kind):
        if kind=='postgres':
            conn.execute('BEGIN')
            conn.execute('CREATE TABLE IF NOT EXISTS launchlab_ai_usage (day TEXT NOT NULL, subject TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day,subject))')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=%s FOR UPDATE',(tok,)).fetchone()
        else:
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('CREATE TABLE IF NOT EXISTS launchlab_ai_usage (day TEXT NOT NULL, subject TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day,subject))')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=?',(tok,)).fetchone()
        if row is None:raise LookupError('Workspace missing')
        state=row[0] if isinstance(row[0],dict) else json.loads(row[0])
        if state['revision']!=revision:raise RuntimeError('Workspace changed; reload to avoid a stale configuration')
        lab=init_lab(state)
        pending=lab.get('pending')
        if pending:
            from datetime import datetime as dt
            started=dt.fromisoformat(pending['started'].replace('Z','+00:00'))
            if (datetime.now(timezone.utc)-started).total_seconds()<90:
                raise ValueError('A model evaluation is already running. Reload after it finishes.')
        if mode not in ('baseline','refined'):raise ValueError('Unknown instruction version')
        for subject,limit in [('global',AI_MAX_GLOBAL_DAY),('workspace:'+tok,AI_MAX_PER_WORKSPACE_DAY)]:
            if kind=='postgres':
                conn.execute('INSERT INTO launchlab_ai_usage (day,subject,count) VALUES (%s,%s,0) ON CONFLICT DO NOTHING',(day,subject))
                updated=conn.execute('UPDATE launchlab_ai_usage SET count=count+1 WHERE day=%s AND subject=%s AND count<%s RETURNING count',(day,subject,limit)).fetchone()
            else:
                conn.execute('INSERT OR IGNORE INTO launchlab_ai_usage(day,subject,count) VALUES (?,?,0)',(day,subject))
                updated=conn.execute('UPDATE launchlab_ai_usage SET count=count+1 WHERE day=? AND subject=? AND count<? RETURNING count',(day,subject,limit)).fetchone()
            if updated is None:raise ValueError('Daily free-tier demonstration quota exhausted. No paid fallback is enabled.')
        instructions=lab['prompts'][mode]
        lab['pending']={'id':lease,'started':now_iso(),'mode':mode}
        state['revision']+=1
        state['activity'].insert(0,{'id':f'AI-{lease[:8]}','kind':'ai_run_requested', 'text':'Synthetic evidence QA evaluation requested ('+mode+')','at':now_iso()})
        if kind=='postgres':conn.execute('UPDATE launchlab_workspaces SET document=%s::jsonb,updated_at=NOW() WHERE id=%s',(json.dumps(state),tok))
        else:conn.execute('UPDATE launchlab_workspaces SET document=?,updated_at=? WHERE id=?',(json.dumps(state),str(time.time()),tok))
        conn.commit()
        return lease,instructions,lab['prompt_versions'][mode]

def _finish_model_call(tok,lease,mode,prompt,version,result,error):
    with connect() as (conn,kind):
        if kind=='postgres':
            conn.execute('BEGIN')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=%s FOR UPDATE',(tok,)).fetchone()
        else:
            conn.execute('BEGIN IMMEDIATE')
            row=conn.execute('SELECT document FROM launchlab_workspaces WHERE id=?',(tok,)).fetchone()
        if not row:raise LookupError('Workspace missing')
        state=row[0] if isinstance(row[0],dict) else json.loads(row[0]);lab=init_lab(state)
        if not lab.get('pending') or lab['pending'].get('id')!=lease:
            raise RuntimeError('Evaluation lease expired; result was not recorded')
        record={'id':lease,'model':MODEL,'mode':mode,'prompt':prompt,'version':version,
                'created':now_iso(),'status':'failed' if error else 'completed',
                'result':result if not error else None,'error':error}
        lab['runs']=[record]+lab['runs'][:5]
        lab['pending']=None
        state['revision']+=1
        state['activity'].insert(0,{'id':f'AI-{lease[:8]}-done','kind':'ai_run_result','text':'AI QA '+('failed: '+error if error else f'completed for {mode}; {result["agreement_count"]}/6 synthetic reference matches'), 'at':now_iso()})
        if kind=='postgres':conn.execute('UPDATE launchlab_workspaces SET document=%s::jsonb,updated_at=NOW() WHERE id=%s',(json.dumps(state),tok))
        else:conn.execute('UPDATE launchlab_workspaces SET document=?,updated_at=? WHERE id=?',(json.dumps(state),str(time.time()),tok))
        conn.commit()
        return record

@app.post('/api/ai/run')
async def ai_run(request:Request):
    _safe_origin(request)
    if request.headers.get('content-type','').split(';')[0]!='application/json':raise HTTPException(415,'JSON required')
    key=_ai_key()
    if not key:raise HTTPException(503,'Live inference not configured. No paid provider fallback.')
    tok=session_id(request)
    if not tok:raise HTTPException(401,'Open a workspace first')
    try:body=await request.json()
    except Exception:raise HTTPException(400,'Invalid JSON')
    if not isinstance(body,dict) or len(json.dumps(body))>500:raise HTTPException(400,'Invalid evaluation request')
    mode=body.get('mode'); rev=body.get('revision')
    if mode not in ('baseline','refined') or not isinstance(rev,int) or isinstance(rev,bool):raise HTTPException(422,'Expected instruction version and workspace revision')
    try:lease,prompt,version=await asyncio.to_thread(_reserve_model_call,tok,rev,mode)
    except ValueError as exc:raise HTTPException(429,str(exc))
    except RuntimeError as exc:raise HTTPException(409,str(exc))
    except LookupError as exc:raise HTTPException(404,str(exc))
    except Exception:raise HTTPException(503,'Unable to reserve free-tier inference capacity')
    result=None;err=None
    try:result=await asyncio.to_thread(invoke_gemini,key,prompt)
    except Exception as exc:
        err=str(exc) if isinstance(exc,(ValueError,RuntimeError)) else 'Model provider response unavailable'
    try:record=await asyncio.to_thread(_finish_model_call,tok,lease,mode,prompt,version,result,err)
    except Exception:raise HTTPException(503,'Model evaluation could not be saved')
    if err:raise HTTPException(502,err)
    return JSONResponse({'run':record,'status':'completed'},headers={'Cache-Control':'no-store'})
