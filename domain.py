"""LaunchLab: deterministic synthetic AI recruiting implementation case.
No real candidate decisions, integrations, payments, or customer data.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from ai_lab import edit_prompt
import re

MAX_EVENTS = 180


def seed():
    return {
        "revision": 0,
        "account": {"name": "Northstar Labs", "sector": "B2B SaaS · fictional", "ats": "Greenhouse (simulated)", "owner": "Avery Chen · Head of Talent (fictional)", "start_date": "2026-11-03", "target": "Pilot launch across 11 users; at least 8 weekly-active by week 2", "phase": "Configuration"},
        "criteria": [
            {"id":"CR-01", "name":"Customer onboarding ownership", "description":"Led at least one multi-stakeholder B2B implementation through configuration and customer handover.", "kind":"essential", "reviewed":True},
            {"id":"CR-02", "name":"Strong communication", "description":"Excellent communicator who fits our culture.", "kind":"essential", "reviewed":False},
            {"id":"CR-03", "name":"Workflow troubleshooting", "description":"Can identify, reproduce and document configuration or data-mapping issues with steps to resolve.", "kind":"preferred", "reviewed":True},
        ],
        "icp_approved": False,
        "ats_fixture": {
            "job": {"id":"JOB-231","title":"Implementation Specialist"},
            "candidate": {"id":"SYN-104","consent":"demo only"},
            "stage": {"name":"Interview"},
            "recruiter": {"email":"recruiter@fictional.example"},
        },
        "ats_mapping": {"job_id":"job.id","candidate_id":"candidate.id","stage":"stage.name","owner":"recruiter.email"},
        "mapping_result": None,
        "integrations": [
            {"id":"INT-01", "name":"ATS field mapping", "description":"Compare sample fields: job ID, stage, owner, and scorecard mapping", "status":"pending", "evidence":""},
            {"id":"INT-02", "name":"Permission boundaries", "description":"Check simulated role permissions against least-privilege matrix", "status":"pending", "evidence":""},
            {"id":"INT-03", "name":"Round-trip dry-run", "description":"Validate synthetic record read and acknowledgement without writeback", "status":"pending", "evidence":""},
        ],
        "teams": [
            {"id":"recruiters", "name":"Recruiting", "seats":6, "trained":3, "w1":3, "w2":None, "owner":"Jordan Lee", "friction":"Inconsistent interview note structure"},
            {"id":"managers", "name":"Hiring managers", "seats":3, "trained":1, "w1":0, "w2":None, "owner":"Sam Taylor", "friction":"Unclear ideal candidate profile"},
            {"id":"ops", "name":"Talent operations", "seats":2, "trained":1, "w1":1, "w2":None, "owner":"Robin Patel", "friction":"ATS mapping confidence"},
        ],
        "training": [
            {"id":"TR-01", "title":"Recruiter walkthrough", "audience":"Recruiting", "state":"completed", "format":"live practice", "owner":"Jordan Lee", "proof":"3 of 6 participated in fictional exercise"},
            {"id":"TR-02", "title":"Hiring manager: calibrating an ICP", "audience":"Hiring managers", "state":"pending", "format":"role-play", "owner":"Sam Taylor", "proof":""},
            {"id":"TR-03", "title":"Ops: verifying integration evidence", "audience":"Talent operations", "state":"pending", "format":"dry-run", "owner":"Robin Patel", "proof":""}
        ],
        "interventions": [],
        "activity": [{"id":"EV-000", "kind":"seed", "text":"Fictional implementation workspace created; all data synthetic.", "at":"2026-11-07T09:00:00Z"}],
        "launched": False,
        "handover_signed": False,
    }

VAGUE = re.compile(r"\b(strong communication|great fit|culture fit|rockstar|world.class|excellent communicator|top university|young|native english|energetic)\b", re.I)

def test_mapping(state):
    """Read-only synthetic ATS source transformation; prevents accidental use of real PII."""
    allowed={"job.id","job.title","candidate.id","stage.name","recruiter.email"}
    required={"job_id","candidate_id","stage","owner"}
    mapping=state["ats_mapping"]
    issues=[]; output={}
    for target in sorted(required):
        path=mapping.get(target,"")
        if path not in allowed:
            issues.append(f"{target}: unsupported source path '{path}'")
            continue
        field,leaf=path.split('.')
        value=state["ats_fixture"].get(field,{}).get(leaf)
        if not isinstance(value,str) or not value.strip():
            issues.append(f"{target}: empty or missing source value")
        else: output[target]=value
    if len(set(mapping.values()))<len(mapping):
        issues.append("Two target fields point to the same source; review mapping")
    return {"passed":not issues,"issues":issues,"output":output if not issues else None,"fixture":"SYNTHETIC / not Greenhouse"}

def criterion_issues(c):
    desc = c["description"].strip()
    issues = []
    if len(desc) < 30: issues.append("Not enough observable detail to test consistently")
    if VAGUE.search(desc): issues.append("Subjective or potentially exclusionary wording needs clarification")
    if c["kind"] not in ("essential", "preferred"): issues.append("Choose essential or preferred")
    if not c.get("reviewed"): issues.append("Hiring owner has not reviewed this criterion")
    return issues

def assess(state):
    blockers = []
    for c in state["criteria"]:
        problems = criterion_issues(c)
        if problems: blockers.append({"id":c["id"],"area":"Profile", "title":c["name"], "detail":"; ".join(problems), "owner":"Hiring manager"})
    if not state["icp_approved"]: blockers.append({"id":"ICP","area":"Profile","title":"Profile approval outstanding","detail":"Hiring owner must approve the final criteria after resolving issues","owner":"Head of Talent"})
    for c in state["integrations"]:
        if c["status"] != "passed": blockers.append({"id":c["id"], "area":"Integration", "title":c["name"],"detail": "Dry-run evidence needs recording before launch" if c["status"]=="pending" else "A failed test must be investigated and rerun", "owner":"Talent operations"})
    trained = sum(t["trained"] for t in state["teams"])
    if trained < 6: blockers.append({"id":"TRAIN", "area":"Enablement", "title":"Pilot training coverage", "detail":f"{trained}/11 users prepared; pilot launch requires at least 6 (demo policy)", "owner":"Enablement lead"})
    if any(t["state"]!="completed" for t in state["training"]): blockers.append({"id":"LEARN", "area":"Enablement", "title":"Learning checks incomplete", "detail":"Complete the targeted hiring-manager and operations exercises", "owner":"Enablement lead"})
    return {"blockers":blockers,"ready":not blockers,"trained":trained,"integration_passed":sum(t["status"]=="passed" for t in state["integrations"]),"criteria_reviewed":sum(not criterion_issues(c) for c in state["criteria"]),"total_seats":sum(t["seats"] for t in state["teams"])}

def adoption(state):
    baseline=sum(t["w1"] for t in state["teams"])
    latest=sum((t["w2"] if t["w2"] is not None else t["w1"]) for t in state["teams"])
    observed_w2=all(t["w2"] is not None for t in state["teams"])
    return {"baseline":baseline,"latest":latest,"total":sum(t["seats"] for t in state["teams"]),"w2_complete":observed_w2,"target_met":observed_w2 and latest>=8,"teams":[{"id":t["id"],"name":t["name"],"seats":t["seats"],"w1":t["w1"],"w2":t["w2"],"trained":t["trained"],"friction":t["friction"],"at_risk": (t["w2"] if t["w2"] is not None else t["w1"]) < max(1,(t["seats"]+1)//2)} for t in state["teams"]]}

def _one(rows, id):
    obj=next((x for x in rows if x["id"]==id),None)
    if obj is None: raise ValueError("Unknown record")
    return obj

def act(original:dict, action:str, data:dict) -> dict:
    if not isinstance(data,dict): raise ValueError("Data must be an object")
    state=deepcopy(original)
    if len(state["activity"])>=MAX_EVENTS:raise ValueError("Workspace event limit reached; start a fresh demo")
    message=""
    if action=="edit_ai_prompt":
        lab=edit_prompt(state,data.get("mode"),data.get("instructions"))
        message=f"Saved {data.get('mode')} AI instruction version {lab['prompt_versions'][data['mode']]} (no model request made)"
    elif action=="edit_criterion":
        c=_one(state["criteria"],data.get("id"))
        desc=data.get("description","")
        kind=data.get("kind",c["kind"])
        if not isinstance(desc,str) or not 10<=len(desc)<=400 or kind not in ("essential","preferred"):raise ValueError("Criterion must have 10–400 characters and a valid type")
        c.update(description=desc.strip(),kind=kind,reviewed=False)
        state["icp_approved"]=False
        message=f"Edited {c['name']}; prior profile approval invalidated"
    elif action=="review_criterion":
        c=_one(state["criteria"],data.get("id"))
        if VAGUE.search(c["description"]) or len(c["description"])<30:raise ValueError("Resolve vague criterion before review")
        c["reviewed"]=True
        message=f"Reviewed {c['name']} against its observable requirement"
    elif action=="approve_icp":
        if any(criterion_issues(c) for c in state["criteria"]):raise ValueError("Profile contains unresolved criteria")
        state["icp_approved"]=True
        message="Recorded fictional hiring-owner profile approval"
    elif action=="edit_mapping":
        key=data.get("target")
        val=data.get("path")
        if key not in ("job_id","candidate_id","stage","owner") or not isinstance(val,str) or not 1<=len(val)<=70:
            raise ValueError("Choose a supported field and a short source path")
        state["ats_mapping"][key]=val.strip()
        state["mapping_result"]=None
        row=_one(state["integrations"],"INT-01")
        row["status"]="pending";row["evidence"]=""
        message=f"Edited synthetic {key} mapping; previous mapping test invalidated"
    elif action=="run_mapping_test":
        result=test_mapping(state)
        state["mapping_result"]=result
        row=_one(state["integrations"],"INT-01")
        row["status"]="passed" if result["passed"] else "failed"
        row["evidence"]="Synthetic schema mapping passed all checks" if result["passed"] else "; ".join(result["issues"])[:220]
        message="Ran actual deterministic mapping validation against synthetic ATS fixture: "+("passed" if result["passed"] else "failed")
    elif action=="set_integration":
        row=_one(state["integrations"],data.get("id"))
        if row["id"]=="INT-01":raise ValueError("ATS field mapping must pass the deterministic test; manual pass is not allowed")
        status=data.get("status")
        evidence=data.get("evidence","")
        if status not in ("passed","failed") or not isinstance(evidence,str) or not 12<=len(evidence.strip())<=220:raise ValueError("Choose pass/fail and enter 12–220 characters of synthetic test evidence")
        row["status"]=status;row["evidence"]=evidence.strip()
        message=f"Simulated check {row['name']} marked {status}; evidence recorded"
    elif action=="complete_training":
        t=_one(state["training"],data.get("id"))
        proof=data.get("proof","")
        if not isinstance(proof,str) or not 12<=len(proof.strip())<=220:raise ValueError("Record 12–220 characters describing the fictional learning check")
        t["state"]="completed";t["proof"]=proof.strip()
        message=f"Recorded fictional learning check for {t['audience']}"
    elif action=="set_trained":
        team=_one(state["teams"],data.get("id"))
        value=data.get("value")
        if not isinstance(value,int) or isinstance(value,bool) or value<0 or value>team["seats"]:raise ValueError("Training count must be within team seats")
        team["trained"]=value
        message=f"Updated fictional training attendance for {team['name']}: {value}/{team['seats']}"
    elif action=="launch_pilot":
        if state["launched"]:raise ValueError("Pilot has already been launched")
        if not assess(state)["ready"]:raise ValueError("Cannot launch: mandatory readiness gates remain")
        state["launched"]=True;state["account"]["phase"]="Pilot live"
        message="Pilot launched in synthetic scenario; no real integrations or customers were touched"
    elif action=="record_usage":
        if not state["launched"]:raise ValueError("Pilot must launch before recording simulated adoption")
        team=_one(state["teams"],data.get("id"))
        count=data.get("count")
        if not isinstance(count,int) or isinstance(count,bool) or count<0 or count>team["seats"]:raise ValueError("Usage count cannot exceed allocated seats")
        team["w2"]=count
        state["handover_signed"]=False
        message=f"Recorded synthetic week-two active users in {team['name']}: {count}/{team['seats']}"
    elif action=="intervene":
        if not state["launched"]:raise ValueError("Launch pilot before planning adoption interventions")
        team=_one(state["teams"],data.get("id"))
        kind=data.get("kind")
        note=data.get("note","")
        if kind not in ("training","configuration","escalation") or not isinstance(note,str) or not 12<=len(note.strip())<=220:raise ValueError("Choose intervention type and record a 12–220 character plan")
        state["interventions"].append({"id":f"IN-{len(state['interventions'])+1:03d}","team_id":team["id"],"team":team["name"],"kind":kind,"note":note.strip(),"status":"planned"})
        message=f"Planned {kind} intervention for {team['name']}; adoption is unchanged until new usage evidence is entered"
    elif action=="handover":
        a=adoption(state)
        if not state["launched"] or not a["w2_complete"]:raise ValueError("Complete pilot and week-two usage evidence first")
        if not a["target_met"]:raise ValueError("Success threshold not yet met; handover blocked")
        state["handover_signed"]=True;state["account"]["phase"]="Handover ready"
        message="Recorded synthetic operational handover following complete usage evidence"
    else:raise ValueError("Unknown action")
    state["revision"]+=1
    state["activity"].insert(0,{"id":f"EV-{state['revision']:03d}","kind":action,"text":message,"at":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    return state
