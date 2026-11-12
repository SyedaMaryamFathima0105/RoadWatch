"""RoadWatch's Docker-free local server. Uses only the Python standard library."""
from __future__ import annotations
import base64, json, math, mimetypes, os, sqlite3, threading, time, uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "python-web"
UPLOADS = ROOT / "uploads"
DB = ROOT / "roadwatch.sqlite3"
PORT = int(os.getenv("PORT", "8000"))
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "change-this-admin-key")
ML_URL = os.getenv("ML_SERVICE_URL", "")
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}
LOCK = threading.RLock()

@contextmanager
def connect():
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    UPLOADS.mkdir(exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS reports (
          id INTEGER PRIMARY KEY AUTOINCREMENT, image_url TEXT NOT NULL,
          latitude REAL, longitude REAL, note TEXT,
          status TEXT NOT NULL DEFAULT 'SUBMITTED', ai_confidence REAL,
          damage_type TEXT, issue_id INTEGER, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS issues (
          id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
          damage_type TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL,
          status TEXT NOT NULL DEFAULT 'OPEN', report_count INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit (
          id INTEGER PRIMARY KEY AUTOINCREMENT, report_id INTEGER NOT NULL,
          actor_id TEXT, action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(report_id) REFERENCES reports(id)
        );
        """)

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def report_dict(row):
    d = dict(row); d["detectedDamageType"] = d.pop("damage_type"); d["aiConfidence"] = d.pop("ai_confidence")
    d["imageUrl"] = d.pop("image_url"); d["issueId"] = d.pop("issue_id")
    d["createdAt"] = d.pop("created_at"); d["updatedAt"] = d.pop("updated_at")
    return d
def issue_dict(row):
    d = dict(row); d["reportCount"] = d.pop("report_count"); d["damageType"] = d.pop("damage_type")
    d["createdAt"] = d.pop("created_at"); d["updatedAt"] = d.pop("updated_at")
    return d
def meters(a,b,c,d):
    p=math.pi/180; x=(c-a)*p; y=(d-b)*p
    h=math.sin(x/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin(y/2)**2
    return 6371000*2*math.atan2(math.sqrt(min(1,h)),math.sqrt(max(0,1-h)))
def detect(raw, content_type, filename):
    if not ML_URL: return None
    boundary="----RoadWatch"+uuid.uuid4().hex
    body=(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n").encode()+raw+f"\r\n--{boundary}--\r\n".encode()
    try:
        req=Request(ML_URL.rstrip("/")+"/detect",data=body,headers={"Content-Type":f"multipart/form-data; boundary={boundary}"},method="POST")
        with urlopen(req,timeout=20) as response: return json.loads(response.read())
    except Exception:
        return None

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(WEB),**kwargs)
    def log_message(self,fmt,*args): print(f"{self.log_date_time_string()} {self.address_string()} {fmt % args}")
    def send_json(self,status,data):
        raw=json.dumps(data,ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def read_json(self):
        n=int(self.headers.get("Content-Length","0"))
        if n>MAX_BYTES*2: raise ValueError("Request exceeds the upload limit")
        return json.loads(self.rfile.read(n) or b"{}")
    def admin(self):
        import hmac
        if not hmac.compare_digest(self.headers.get("X-Admin-Key", ""), ADMIN_KEY): self.send_json(403,{"error":"Admin key required"}); return False
        return True
    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith("/uploads/"):
            target=(UPLOADS/unquote(path.removeprefix("/uploads/"))).resolve()
            if target.parent != UPLOADS.resolve() or not target.is_file(): return self.send_json(404,{"error":"Image not found"})
            data=target.read_bytes(); self.send_response(200); self.send_header("Content-Type",mimetypes.guess_type(target.name)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data); return
        if path=="/api/health": return self.send_json(200,{"status":"ok","database":"sqlite","mlConfigured":bool(ML_URL)})
        if path=="/api/map/reports":
            with connect() as db: rows=db.execute("SELECT * FROM reports WHERE status='ACCEPTED' AND latitude IS NOT NULL ORDER BY created_at DESC").fetchall()
            return self.send_json(200,[report_dict(r) for r in rows])
        if path.startswith("/api/admin/") and not self.admin(): return
        if path=="/api/admin/reports":
            with connect() as db: rows=db.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
            return self.send_json(200,[report_dict(r) for r in rows])
        if path=="/api/admin/issues":
            with connect() as db: rows=db.execute("SELECT * FROM issues ORDER BY updated_at DESC").fetchall()
            return self.send_json(200,[issue_dict(r) for r in rows])
        if path=="/api/admin/stats":
            with connect() as db:
                total=db.execute("SELECT count(*) FROM reports").fetchone()[0]; accepted=db.execute("SELECT count(*) FROM reports WHERE status='ACCEPTED'").fetchone()[0]; review=db.execute("SELECT count(*) FROM reports WHERE status='UNDER_REVIEW'").fetchone()[0]; issues=db.execute("SELECT count(*) FROM issues").fetchone()[0]
            return self.send_json(200,{"totalReports":total,"accepted":accepted,"underReview":review,"groupedIssues":issues})
        if path.startswith("/api/admin/reports/") and path.endswith("/audit"):
            try: rid=int(path.split("/")[-2])
            except ValueError: return self.send_json(400,{"error":"Invalid report id"})
            with connect() as db: rows=db.execute("SELECT * FROM audit WHERE report_id=? ORDER BY created_at",(rid,)).fetchall()
            return self.send_json(200,[dict(r) for r in rows])
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!="/api/reports": return self.send_json(404,{"error":"Route not found"})
        try:
            data=self.read_json(); content_type=data.get("contentType",""); encoded=data.get("imageData","")
            if content_type not in ALLOWED: return self.send_json(415,{"error":"Use a JPEG, PNG, or WebP image"})
            if not encoded.startswith("data:") or "," not in encoded: return self.send_json(400,{"error":"Choose an image first"})
            raw=base64.b64decode(encoded.split(",",1)[1],validate=True)
            if not raw or len(raw)>MAX_BYTES: return self.send_json(413 if raw else 400,{"error":"Image must be nonempty and at most 10 MB"})
            valid_image=(content_type=="image/jpeg" and raw.startswith(b"\xff\xd8\xff")) or (content_type=="image/png" and raw.startswith(b"\x89PNG\r\n\x1a\n")) or (content_type=="image/webp" and raw.startswith(b"RIFF") and raw[8:12]==b"WEBP")
            if not valid_image: return self.send_json(400,{"error":"File contents do not match the selected image type"})
            lat=data.get("latitude"); lon=data.get("longitude")
            if (lat is None)!=(lon is None): return self.send_json(400,{"error":"Enter both coordinates, or leave both blank"})
            if lat is not None and (not -90<=float(lat)<=90 or not -180<=float(lon)<=180): return self.send_json(400,{"error":"Coordinates are out of range"})
            ext={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}[content_type]; name=uuid.uuid4().hex+ext; (UPLOADS/name).write_bytes(raw)
            inferred=detect(raw,content_type,name); detections=(inferred or {}).get("detections",[]); best=max(detections,key=lambda d:d.get("confidence",0),default=None)
            stamp=now(); status="AI_FLAGGED" if best else "SUBMITTED"; issue_id=None
            with LOCK,connect() as db:
                cur=db.execute("INSERT INTO reports(image_url,latitude,longitude,note,status,ai_confidence,damage_type,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",("/uploads/"+name,lat,lon,(data.get("note") or "")[:500],status,best.get("confidence") if best else None,best.get("class",best.get("type")) if best else None,stamp,stamp)); rid=cur.lastrowid
                if lat is not None:
                    nearby=[r for r in db.execute("SELECT * FROM issues").fetchall() if meters(float(lat),float(lon),r['latitude'],r['longitude'])<=30]
                    if nearby:
                        issue=min(nearby,key=lambda r:meters(float(lat),float(lon),r['latitude'],r['longitude'])); issue_id=issue['id']; db.execute("UPDATE issues SET report_count=report_count+1,updated_at=? WHERE id=?",(stamp,issue_id))
                    else:
                        cur=db.execute("INSERT INTO issues(title,damage_type,latitude,longitude,created_at,updated_at) VALUES(?,?,?,?,?,?)",("Road damage report",best.get("class",best.get("type")) if best else "unclassified",lat,lon,stamp,stamp)); issue_id=cur.lastrowid
                    db.execute("UPDATE reports SET issue_id=? WHERE id=?",(issue_id,rid))
                db.execute("INSERT INTO audit(report_id,action,details,created_at) VALUES(?,?,?,?)",(rid,"REPORT_SUBMITTED","AI output is a suggestion requiring human review.",stamp))
                row=db.execute("SELECT * FROM reports WHERE id=?",(rid,)).fetchone()
            return self.send_json(201,{**report_dict(row),"detections":detections,"modelVersion":(inferred or {}).get("modelVersion"),"inferenceTimeMs":(inferred or {}).get("inferenceTimeMs")})
        except (ValueError,KeyError,json.JSONDecodeError) as exc: return self.send_json(400,{"error":str(exc) or "Invalid request"})
        except Exception as exc: print("Request error:",exc); return self.send_json(500,{"error":"Could not save report"})
    def do_PATCH(self):
        if not urlparse(self.path).path.startswith("/api/admin/reports/"): return self.send_json(404,{"error":"Route not found"})
        if not self.admin(): return
        try:
            parts=urlparse(self.path).path.split("/"); rid=int(parts[4]); status=self.read_json().get("status")
            if status not in {"SUBMITTED","AI_FLAGGED","UNDER_REVIEW","ACCEPTED","REJECTED","REPAIRED"}: return self.send_json(400,{"error":"Invalid report status"})
            stamp=now()
            with connect() as db:
                row=db.execute("SELECT status FROM reports WHERE id=?",(rid,)).fetchone()
                if not row: return self.send_json(404,{"error":"Report not found"})
                db.execute("UPDATE reports SET status=?,updated_at=? WHERE id=?",(status,stamp,rid)); db.execute("INSERT INTO audit(report_id,action,details,created_at) VALUES(?,?,?,?)",(rid,"STATUS_CHANGED",row['status']+" -> "+status,stamp)); updated=db.execute("SELECT * FROM reports WHERE id=?",(rid,)).fetchone()
            return self.send_json(200,report_dict(updated))
        except Exception: return self.send_json(400,{"error":"Invalid status update"})

if __name__=="__main__":
    init_db(); print(f"RoadWatch running at http://127.0.0.1:{PORT}")
    print("Admin key:",ADMIN_KEY," | AI:","connected" if ML_URL else "not configured")
    threading.Timer(1.0,lambda:webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
