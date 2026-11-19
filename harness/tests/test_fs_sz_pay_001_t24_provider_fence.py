"""T24 qualification of cooperative provider-side SQLite fence."""
import multiprocessing
from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence

def _race(path, action, queue):
    fence=ProviderCommitFence(path)
    result=fence.revoke("mandate") if action=="revoke" else fence.commit("mandate",1,"intent")
    queue.put((action,result))

def test_revocation_first_refuses_commit(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("mandate")
    f.revoke("mandate")
    assert f.commit("mandate",1,"intent")=="REFUSED_AUTHORITY"
    assert f.count()==0

def test_commit_first_then_revoke_is_serialised(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("mandate")
    assert f.commit("mandate",1,"intent")=="COMMITTED"
    f.revoke("mandate")
    assert f.commit("mandate",1,"new-intent")=="REFUSED_AUTHORITY"
    assert f.count()==1

def test_same_intent_two_claims_refuses_second(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("mandate")
    assert f.commit("mandate",1,"intent")=="COMMITTED"
    assert f.commit("mandate",1,"intent")=="REFUSED_DUPLICATE_INTENT"
    assert f.count()==1

def test_distinct_intents_both_allowed(tmp_path):
    f=ProviderCommitFence(tmp_path/"provider.sqlite3")
    f.establish("mandate")
    assert f.commit("mandate",1,"intent-A")=="COMMITTED"
    assert f.commit("mandate",1,"intent-B")=="COMMITTED"

def test_revocation_commit_process_race_has_valid_serial_order(tmp_path):
    path=str(tmp_path/"provider.sqlite3")
    f=ProviderCommitFence(path)
    f.establish("mandate")
    ctx=multiprocessing.get_context("spawn")
    q=ctx.Queue()
    ps=[ctx.Process(target=_race,args=(path,action,q)) for action in ("revoke","commit")]
    for p in ps:p.start()
    for p in ps:
        p.join(15)
        assert p.exitcode==0
    outcomes=dict(q.get(timeout=3) for _ in ps)
    assert outcomes["commit"] in ("COMMITTED","REFUSED_AUTHORITY")
    assert f.count()==(1 if outcomes["commit"]=="COMMITTED" else 0)
    assert f.commit("mandate",1,"later-intent")=="REFUSED_AUTHORITY"
