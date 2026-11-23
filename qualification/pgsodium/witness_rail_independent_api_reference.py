"""IE-W09 isolated API-bound replay authority reference; NOT independent administration."""
import json
import multiprocessing as mp
import os
import sqlite3
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def server(db, ready, stop, portq):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass
        def do_POST(self):
            length=int(self.headers.get("Content-Length","0"))
            try: payload=json.loads(self.rfile.read(length))
            except (ValueError,UnicodeError): payload={}
            result="UNRESOLVED_UNAUTHENTICATED"
            if self.headers.get("Authorization")=="Bearer executor-test-token":
                if self.path!="/consume":
                    result="REFUSED_UNSUPPORTED_OPERATION"
                elif not isinstance(payload.get("event_id"),str) or not payload["event_id"]:
                    result="UNRESOLVED_INVALID_EVENT"
                else:
                    with sqlite3.connect(db,timeout=20) as conn:
                        try:
                            conn.execute("INSERT INTO events(event_id) VALUES(?)",(payload["event_id"],))
                            result="ACCEPTED_REFERENCE_EVENT"
                        except sqlite3.IntegrityError:
                            result="UNRESOLVED_REPLAYED_RAIL_EVENT"
            body=json.dumps({"result":result}).encode()
            self.send_response(200);self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY)")
    httpd=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    httpd.timeout=0.15
    portq.put(httpd.server_address[1]);ready.set()
    while not stop.is_set():httpd.handle_request()
    httpd.server_close()

def request(port,event,token="executor-test-token",path="/consume"):
    req=urllib.request.Request("http://127.0.0.1:%s%s"%(port,path),
        data=json.dumps({"event_id":event}).encode(),
        headers={"Content-Type":"application/json","Authorization":"Bearer "+token},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=3) as response:
            return json.load(response)["result"]
    except (urllib.error.URLError,TimeoutError,OSError):
        return "UNRESOLVED_REPLAY_AUTHORITY_UNAVAILABLE"

def start(db):
    ready=mp.Event();stop=mp.Event();q=mp.Queue()
    p=mp.Process(target=server,args=(db,ready,stop,q),daemon=True)
    p.start();assert ready.wait(8);return p,stop,q.get(timeout=5)

def close(p,stop):
    stop.set();p.join(3)
    if p.is_alive():p.terminate();p.join(3)

def main():
    with tempfile.TemporaryDirectory() as directory:
        db=str(Path(directory)/"authority.sqlite")
        p,stop,port=start(db)
        try:
            assert request(port,"E-001")=="ACCEPTED_REFERENCE_EVENT"
            assert request(port,"E-001")=="UNRESOLVED_REPLAYED_RAIL_EVENT"
            assert request(port,"E-001",path="/reset")=="REFUSED_UNSUPPORTED_OPERATION"
            assert request(port,"E-001",token="wrong")=="UNRESOLVED_UNAUTHENTICATED"
            print("IE-W09 API: replay, reset and unauthenticated operations refused")
            barrier=threading.Barrier(2);results=[]
            def worker():
                barrier.wait(timeout=5);results.append(request(port,"E-002"))
            threads=[threading.Thread(target=worker) for _ in range(2)]
            for t in threads:t.start()
            for t in threads:t.join(8)
            assert all(not t.is_alive() for t in threads)
            assert sorted(results)==["ACCEPTED_REFERENCE_EVENT","UNRESOLVED_REPLAYED_RAIL_EVENT"],results
            print("IE-W09 CONCURRENT: exactly one reference event accepted")
        finally:close(p,stop)
        p,stop,port=start(db)
        try:
            assert request(port,"E-001")=="UNRESOLVED_REPLAYED_RAIL_EVENT"
            print("IE-W09 RESTART: replay refused after service process restart")
        finally:close(p,stop)
        assert request(port,"E-003")=="UNRESOLVED_REPLAY_AUTHORITY_UNAVAILABLE"
        print("IE-W09 OUTAGE: unavailable authority cannot classify success")
        Path(db).unlink()
        p,stop,port=start(db)
        try:
            assert request(port,"E-001")=="ACCEPTED_REFERENCE_EVENT"
            print("IE-W09 PRESERVED RED: administrator deleting local store reopens replay")
        finally:close(p,stop)
        print("LIMITATION: local processes share host/admin; no separate cloud IAM, external rail, signed source verification, durable key-status authority or settlement")

if __name__=="__main__":main()
