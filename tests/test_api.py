import os,tempfile,json
from fastapi.testclient import TestClient
import server

def test_persistent_workspace_across_requests(tmp_path,monkeypatch):
 monkeypatch.setattr(server,'DBFILE',str(tmp_path/'workspace.sqlite'))
 client=TestClient(server.app)
 r=client.get('/api/workspace');assert r.status_code==200
 token=r.cookies['launchlab_session'];assert len(token)==43
 assert r.json()['state']['revision']==0
 r=client.post('/api/action',json={'revision':0,'action':'set_trained','data':{'id':'ops','value':2}});assert r.status_code==200,r.text
 assert r.json()['state']['revision']==1
 assert client.get('/api/workspace').json()['state']['teams'][2]['trained']==2
 assert client.get('/api/export').json()['workspace']['revision']==1

def test_revision_conflict(tmp_path,monkeypatch):
 monkeypatch.setattr(server,'DBFILE',str(tmp_path/'conflict.sqlite'))
 with TestClient(server.app) as client:
  client.get('/api/workspace')
  action={'revision':0,'action':'set_trained','data':{'id':'ops','value':2}}
  assert client.post('/api/action',json=action).status_code==200
  assert client.post('/api/action',json=action).status_code==409

def test_origin_and_content_type(tmp_path,monkeypatch):
 monkeypatch.setattr(server,'DBFILE',str(tmp_path/'origin.sqlite'))
 with TestClient(server.app) as client:
  client.get('/api/workspace')
  assert client.post('/api/action',headers={'Origin':'https://other.example'},json={'revision':0,'action':'approve_icp'}).status_code==403
  assert client.post('/api/action',data='{"revision":0}',headers={'content-type':'text/plain'}).status_code==415

def test_separate_sessions(tmp_path,monkeypatch):
 monkeypatch.setattr(server,'DBFILE',str(tmp_path/'separate.sqlite'))
 with TestClient(server.app) as a, TestClient(server.app) as b:
  sa=a.get('/api/workspace');sb=b.get('/api/workspace')
  assert sa.cookies['launchlab_session']!=sb.cookies['launchlab_session']
  a.post('/api/action',json={'revision':0,'action':'set_trained','data':{'id':'ops','value':2}})
  assert b.get('/api/workspace').json()['state']['revision']==0

def test_reset_creates_new_workspace(tmp_path,monkeypatch):
 monkeypatch.setattr(server,'DBFILE',str(tmp_path/'reset.sqlite'))
 with TestClient(server.app) as client:
  x=client.get('/api/workspace');t=x.cookies['launchlab_session']
  r=client.post('/api/reset');assert r.status_code==200
  assert r.cookies['launchlab_session']!=t
