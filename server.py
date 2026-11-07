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
