"""T21 bounded tests for durable intent claims (not payment execution integration)."""
import multiprocessing
from app.engines.payment_intent_claim_store import reserve_intent, claim_status

def _race(path, intent, permit, queue):
    import os
    os.environ["FLOWSIGNAL_PAYMENT_INTENT_STORE"]=path
    queue.put(reserve_intent(intent, permit))

def test_t21_same_intent_different_permit_blocked(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PAYMENT_INTENT_STORE",str(tmp_path/"claims.sqlite3"))
    assert reserve_intent("intent-1","permit-A")
    assert not reserve_intent("intent-1","permit-B")
    assert claim_status("intent-1")==("permit-A","RESERVED")

def test_t21_identical_payment_fields_distinct_intents_allowed(tmp_path, monkeypatch):
    monkeypatch.setenv("FLOWSIGNAL_PAYMENT_INTENT_STORE",str(tmp_path/"claims.sqlite3"))
    assert reserve_intent("business-payment-1","permit-A")
    assert reserve_intent("business-payment-2","permit-B")

def test_t21_two_processes_only_one_wins(tmp_path):
    path=str(tmp_path/"claims.sqlite3")
    ctx=multiprocessing.get_context("spawn")
    queue=ctx.Queue()
    procs=[ctx.Process(target=_race,args=(path,"shared-intent",f"permit-{i}",queue)) for i in range(2)]
    for p in procs:p.start()
    for p in procs:
        p.join(15)
        assert p.exitcode==0
    assert sorted([queue.get(timeout=3),queue.get(timeout=3)])==[False,True]
