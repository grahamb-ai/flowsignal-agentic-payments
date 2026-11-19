"""HTTP-level route closure against actual CBP-002 service process.

Cooperating reference provider only; does not qualify legacy-test-mode or live rails.
"""
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib import request, error

from app.engines.t24_provider_commit_fence_reference import ProviderCommitFence


def _port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0))
        return s.getsockname()[1]


def _send(url,payload):
    req=request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
    try:
        with request.urlopen(req,timeout=3) as resp:
            return resp.status,json.loads(resp.read())
    except error.HTTPError as exc:
        return exc.code,json.loads(exc.read())


def _payment(intent):
    return {"transaction_id":intent,"mandate_id":"MANDATE-TREASURY-001","authority_epoch":1,"source_account":"TREASURY-001",
            "beneficiary":"SUPPLIER-X","amount":750000.0,
            "currency":"GBP","purpose":"supplier settlement"}


def _start(port,path):
    process=subprocess.Popen([
        sys.executable,"external_targets/cbp002_consequence_service.py",
        "--port",str(port),"--fence-db",str(path),
        "--mandate-id","MANDATE-TREASURY-001","--authority-epoch","1",
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    for _ in range(100):
        if process.poll() is not None:
            raise AssertionError("provider exited during startup: "+process.stderr.read())
        try:
            with request.urlopen(f"http://127.0.0.1:{port}/health",timeout=.3) as response:
                if response.status==200:return process
        except Exception:
            time.sleep(.05)
    process.kill()
    raise AssertionError("provider did not become ready")


def test_http_fenced_route_refuses_after_effective_revocation(tmp_path):
    db=tmp_path/"authority.sqlite3"
    provider=ProviderCommitFence(db)
    provider.establish("MANDATE-TREASURY-001",epoch=1)
    provider.revoke("MANDATE-TREASURY-001")
    port=_port()
    service=_start(port,db)
    try:
        status,result=_send(f"http://127.0.0.1:{port}/payments",_payment("intent-after-revoke"))
        assert status==403 and result["status"]=="REFUSED_AUTHORITY"
        assert provider.transfer_count()==0
    finally:
        service.terminate()
        service.wait(timeout=5)


def test_http_fenced_route_accepts_then_refuses(tmp_path):
    db=tmp_path/"authority.sqlite3"
    provider=ProviderCommitFence(db)
    provider.establish("MANDATE-TREASURY-001",epoch=1)
    port=_port()
    service=_start(port,db)
    try:
        status,result=_send(f"http://127.0.0.1:{port}/payments",_payment("intent-before-revoke"))
        assert status==201 and result["status"]=="TRANSFER_RECORDED"
        provider.revoke("MANDATE-TREASURY-001")
        status,result=_send(f"http://127.0.0.1:{port}/payments",_payment("intent-after-revoke"))
        assert status==403 and result["status"]=="REFUSED_AUTHORITY"
        assert provider.transfer_count()==1
    finally:
        service.terminate()
        service.wait(timeout=5)


def test_http_provider_refuses_to_start_unconfigured():
    port=_port()
    proc=subprocess.run([sys.executable,"external_targets/cbp002_consequence_service.py",
                         "--port",str(port)],capture_output=True,text=True,timeout=5)
    assert proc.returncode!=0
    assert "REFUSED_UNQUALIFIED_PROVIDER_ROUTE" in proc.stderr
