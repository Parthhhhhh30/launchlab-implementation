import pytest
from domain import seed,assess,act,adoption,test_mapping as verify_mapping

def try_ready():
    s=seed();s=act(s,'edit_criterion',{'id':'CR-02','description':'Explains complex implementation blockers clearly in writing and gives a customer an actionable next step.','kind':'essential'});s=act(s,'review_criterion',{'id':'CR-02'});s=act(s,'approve_icp',{});
    for i in ['INT-02','INT-03']:
        s=act(s,'set_integration',{'id':i,'status':'passed','evidence':'Synthetic mock mapping verified against the stated checklist.'})
    s=act(s,'run_mapping_test',{})
    for i in ['TR-02','TR-03']:
        s=act(s,'complete_training',{'id':i,'proof':'Fictional learner completed the exercise independently.'})
    s=act(s,'set_trained',{'id':'recruiters','value':4});s=act(s,'set_trained',{'id':'managers','value':2});return s

def test_seed_has_blockers():
 s=seed();r=assess(s);assert r['ready'] is False;assert len(r['blockers'])>4

def test_vague_criteria_cannot_be_signed():
 s=seed();
 with pytest.raises(ValueError,match='vague'):act(s,'review_criterion',{'id':'CR-02'})
 with pytest.raises(ValueError,match='unresolved'):act(s,'approve_icp',{})

def test_approved_profile_invalidated_on_edit():
 s=try_ready();assert s['icp_approved'];s=act(s,'edit_criterion',{'id':'CR-02','description':'Identifies customer rollout risks and describes mitigations with owners.','kind':'essential'});assert not s['icp_approved'];assert not assess(s)['ready']

def test_successful_readiness_and_pilot():
 s=try_ready();assert assess(s)['ready'];s=act(s,'launch_pilot',{});assert s['launched'];assert s['account']['phase']=='Pilot live'

def test_launch_blocked():
 with pytest.raises(ValueError,match='mandatory readiness'):act(seed(),'launch_pilot',{})

def test_intervention_does_not_change_usage():
 s=act(try_ready(),'launch_pilot',{});before=adoption(s);s=act(s,'intervene',{'id':'managers','kind':'training','note':'Run scenario-based manager training on role profile acceptance.'});assert adoption(s)==before

def test_no_early_handover():
 s=act(try_ready(),'launch_pilot',{})
 with pytest.raises(ValueError,match='week-two'):act(s,'handover',{})

def test_handover_requires_complete_evidence_and_threshold():
 s=act(try_ready(),'launch_pilot',{});s=act(s,'record_usage',{'id':'recruiters','count':5});s=act(s,'record_usage',{'id':'managers','count':0});s=act(s,'record_usage',{'id':'ops','count':1});assert adoption(s)['w2_complete'];assert not adoption(s)['target_met']
 with pytest.raises(ValueError,match='threshold'):act(s,'handover',{})
 s=act(s,'record_usage',{'id':'managers','count':2});assert adoption(s)['target_met'];s=act(s,'handover',{});assert s['handover_signed']
 s=act(s,'record_usage',{'id':'recruiters','count':1});assert not s['handover_signed']

def test_counter_boundaries():
 s=seed()
 with pytest.raises(ValueError):act(s,'set_trained',{'id':'ops','value':3})
 with pytest.raises(ValueError):act(s,'set_trained',{'id':'ops','value':True})
 with pytest.raises(ValueError):act(s,'set_integration',{'id':'INT-01','status':'passed','evidence':'short'})
 with pytest.raises(ValueError):act(s,'set_integration',{'id':'INT-01','status':'bogus','evidence':'This is a long enough description'})

def test_original_state_immutable():
 s=seed();a=act(s,'set_trained',{'id':'recruiters','value':4});assert s['revision']==0 and s['teams'][0]['trained']==3 and a['teams'][0]['trained']==4

def test_audit_and_revision():
 s=act(seed(),'set_trained',{'id':'ops','value':2});assert s['revision']==1;assert s['activity'][0]['kind']=='set_trained';assert s['activity'][0]['at'].endswith('Z')

def test_real_mapping_validation_and_invalidation():
 s=seed();assert verify_mapping(s)['passed']
 s=act(s,'run_mapping_test',{});assert s['integrations'][0]['status']=='passed';assert s['mapping_result']['output']['job_id']=='JOB-231'
 s=act(s,'edit_mapping',{'target':'job_id','path':'job.nonexistent'});assert s['integrations'][0]['status']=='pending'
 s=act(s,'run_mapping_test',{});assert s['integrations'][0]['status']=='failed';assert 'unsupported' in s['mapping_result']['issues'][0]
 s=act(s,'edit_mapping',{'target':'job_id','path':'job.id'});s=act(s,'run_mapping_test',{});assert s['integrations'][0]['status']=='passed'
 with pytest.raises(ValueError,match='deterministic test'):act(s,'set_integration',{'id':'INT-01','status':'passed','evidence':'Fake manual claim of passing check'})
