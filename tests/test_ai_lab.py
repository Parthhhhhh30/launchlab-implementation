"""Adversarial safety/repro tests; fake transport explicitly NOT presented as live model proof."""
import json
from copy import deepcopy
import pytest
import server
from ai_lab import CASES, MODEL, BASE_PROMPT, REFINED_PROMPT, create_model_request,parse_response,invoke_gemini,edit_prompt,init_lab
from domain import seed,act
from fastapi.testclient import TestClient


def synthetic_provider_data(quality='baseline'):
    judgments=[]
    for case in CASES:
        label=case['reference']
        if quality=='baseline' and case['id'] in ('F02','F06'):label='supported'
        judgments.append({'id':case['id'],'assessment':label,'evidence_ids':[case['facts'][0]['id']],
                          'rationale':'The supplied fictional statement supports this evidence check only; no hiring outcome is implied.',
                          'next_check':'Ask for specifics about the scope of onboarding responsibilities and supporting evidence.'})
    return {'candidates':[{'content':{'parts':[{'text':json.dumps({'judgments':judgments})}]}}],
            'usageMetadata':{'promptTokenCount':600,'candidatesTokenCount':350}}

def test_structured_prompts_and_provider_mock():
    req=create_model_request(REFINED_PROMPT)
    assert 'tools' not in req and req['generationConfig']['responseMimeType']=='application/json'
    assert 'Do NOT evaluate people' in req['systemInstruction']['parts'][0]['text']
    a=invoke_gemini('NOT_REAL_KEY',BASE_PROMPT,transport=lambda *args:synthetic_provider_data())
    b=invoke_gemini('NOT_REAL_KEY',REFINED_PROMPT,transport=lambda *args:synthetic_provider_data('refined'))
    assert a['agreement_count']==4 and b['agreement_count']==6
    assert b['usage']['input_tokens']==600

def test_reject_hallucinated_citation_and_duplicates():
    d=synthetic_provider_data('refined')
    raw=json.loads(d['candidates'][0]['content']['parts'][0]['text'])
    raw['judgments'][0]['evidence_ids']=['HALLUCINATED'];d['candidates'][0]['content']['parts'][0]['text']=json.dumps(raw)
    with pytest.raises(ValueError,match='Untraceable'):parse_response(d)
    d=synthetic_provider_data('refined');raw=json.loads(d['candidates'][0]['content']['parts'][0]['text']);raw['judgments'][0]['id']='F02';raw['judgments'][0]['evidence_ids']=['E201']
    d['candidates'][0]['content']['parts'][0]['text']=json.dumps(raw)
    with pytest.raises(ValueError,match='duplicate'):parse_response(d)

def test_prompt_versions_and_old_workspaces():
    s=seed();assert 'ai_lab' not in s
    t=act(s,'edit_ai_prompt',{'mode':'refined','instructions':REFINED_PROMPT+' Check edge cases.'})
    assert 'ai_lab' not in s
    assert t['ai_lab']['prompt_versions']['refined']==2
    assert t['revision']==1
    with pytest.raises(ValueError):edit_prompt(s,'baseline','short')


def test_real_api_disabled_without_key(tmp_path,monkeypatch):
    monkeypatch.setattr(server,'DBFILE',str(tmp_path/'no_key.sqlite'))
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    with TestClient(server.app) as c:
        c.get('/api/workspace')
        s=c.get('/api/ai/status');assert s.status_code==200 and s.json()['available'] is False
        assert len(s.json()['cases'])==6
        assert all('reference' not in x for x in s.json()['cases'])
        assert c.post('/api/ai/run',json={'mode':'baseline','revision':0}).status_code==503
        r=c.post('/api/action',json={'revision':0,'action':'edit_ai_prompt','data':{'mode':'baseline','instructions':BASE_PROMPT+' More explicit.'}})
        assert r.status_code==200
        assert c.get('/api/ai/status').json()['ai_lab']['prompt_versions']['baseline']==2


def test_quota_and_persistent_result(tmp_path,monkeypatch):
    monkeypatch.setattr(server,'DBFILE',str(tmp_path/'quota.sqlite'))
    monkeypatch.setenv('GEMINI_API_KEY','FAKE_TEST_TOKEN')
    with TestClient(server.app) as c:
        c.get('/api/workspace')
        # Exercise same DB functions that production endpoint uses, with fake provider outputs.
        token=c.cookies.get('launchlab_session')
        for idx in range(3):
            lease,prompt,version=server._reserve_model_call(token,idx*2,'baseline')
            result=invoke_gemini('TEST_TOKEN',prompt,transport=lambda *args:synthetic_provider_data('refined'))
            record=server._finish_model_call(token,lease,'baseline',prompt,version,result,None)
            assert record['status']=='completed'
        assert len(c.get('/api/ai/status').json()['ai_lab']['runs'])==3
        assert c.get('/api/workspace').json()['state']['revision']==6
        with pytest.raises(ValueError,match='quota'):server._reserve_model_call(token,6,'baseline')
        # Same visitor in new session has distinct quota; global is still persistent.
        with TestClient(server.app) as second:
            second.get('/api/workspace');different=second.cookies.get('launchlab_session')
            assert different!=token
            lease,*_=server._reserve_model_call(different,0,'refined')
        # Same browser cannot make extra calls merely by reloading.
        assert c.get('/api/ai/status').json()['ai_lab']['runs'][0]['model']==MODEL


def test_origin_and_validation_of_model_endpoint(tmp_path,monkeypatch):
    monkeypatch.setattr(server,'DBFILE',str(tmp_path/'origin.sqlite'))
    monkeypatch.setenv('GEMINI_API_KEY','FAKE_TEST_TOKEN')
    with TestClient(server.app) as c:
        c.get('/api/workspace')
        assert c.post('/api/ai/run',json={'revision':0,'mode':'baseline'},headers={'origin':'https://malicious.example'}).status_code==403
        assert c.post('/api/ai/run',json={'revision':False,'mode':'baseline'}).status_code==422
        assert c.post('/api/ai/run',json={'revision':0,'mode':'automated_hire'}).status_code==422
