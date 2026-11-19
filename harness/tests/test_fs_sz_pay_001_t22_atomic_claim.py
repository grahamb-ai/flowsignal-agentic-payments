"""T22 bounded atomic claim tests; not yet integrated into external execution."""
import sqlite3
from app.engines.permit_consumption_store import consume_permit_begin_outcome_and_claim_intent_once as claim

def test_t22_three_records_commit_together(tmp_path,monkeypatch):
    p=tmp_path/"permits.sqlite3"
    o=tmp_path/"outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(p))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(o))
    assert claim("permit-a","binding-a","intent-1")=="RESERVED"
    with sqlite3.connect(p) as c:
        assert c.execute("SELECT signature FROM consumed_execution_permits").fetchall()==[("permit-a",)]
        assert c.execute("SELECT payment_intent_id FROM payment_intent_claims").fetchall()==[("intent-1",)]
    with sqlite3.connect(o) as c:
        assert c.execute("SELECT outcome FROM consequence_outcomes").fetchall()==[("CONSEQUENCE_OUTCOME_UNRESOLVED",)]

def test_t22_fresh_permit_same_intent_denied_without_consumption(tmp_path,monkeypatch):
    p=tmp_path/"permits.sqlite3"
    o=tmp_path/"outcomes.sqlite3"
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(p))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(o))
    assert claim("permit-a","binding-a","intent-1")=="RESERVED"
    assert claim("permit-b","binding-a","intent-1")=="DENIED_PAYMENT_INTENT_ALREADY_CLAIMED"
    assert claim("permit-a","binding-a","intent-2")=="DENIED_EXECUTION_PERMIT_REPLAY"
    with sqlite3.connect(p) as c:
        assert c.execute("SELECT COUNT(*) FROM consumed_execution_permits").fetchone()[0]==1
    with sqlite3.connect(o) as c:
        assert c.execute("SELECT COUNT(*) FROM consequence_outcomes").fetchone()[0]==1

def test_t22_distinct_intents_allowed_even_same_binding(tmp_path,monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PERMIT_CONSUMPTION_STORE",str(tmp_path/"p.sqlite3"))
    monkeypatch.setenv("FLOWSIGNAL_CONSEQUENCE_OUTCOME_STORE",str(tmp_path/"o.sqlite3"))
    assert claim("permit-a","same-binding","intent-1")=="RESERVED"
    assert claim("permit-b","same-binding","intent-2")=="RESERVED"
