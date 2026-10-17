# -*- coding: utf-8 -*-
"""أكاديمية سنابل التقنية: لوحة تحكم محلية + مولّد موقع ثابت (GitHub Pages)"""
import json, uuid, math, shutil, threading, webbrowser, secrets, os, base64, hashlib, requests
from pathlib import Path
from flask import Flask, request, session, redirect, render_template, flash, send_from_directory, abort, jsonify
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageOps

B = Path(__file__).parent; DOCS = B/'docs'; UP = DOCS/'uploads'; DF = DOCS/'data.json'; AF = B/'data'/'admin.json'
TOKEN = os.environ.get('GITHUB_TOKEN'); REPO = os.environ.get('GITHUB_REPO'); BR = os.environ.get('GITHUB_BRANCH', 'main'); REMOTE = bool(TOKEN and REPO)
STAGES = ["تعلّم أساسيات البحث العلمي", "تعلّم البرمجة بلغة C++", "الانتقال إلى المحاكاة بواسطة Tinkercad",
          "اختيار مشاريع لاكتساب المهارة والبدء بالعمل على الهاردوير", "تعليم الروبوتيك للطلبة الجدد", "ابتكار مشاريع ذات أثر مجتمعي"]
DEFAULT = {"settings": {"name": "أكاديمية سنابل التقنية", "tagline": "جذورٌ صامدة... وعقول تُثمر",
    "about": "أكاديمية سنابل التقنية في درعا تُعنى بتعليم البرمجة والروبوتيك وبناء جيل مبتكر يخدم مجتمعه.",
    "vision": "جيلٌ يتقن التقنية ويصنع بها أثراً في مجتمعه.", "address": "درعا، سوريا", "phone": "", "email": "",
    "beneficiaries": "0", "tracks": "برمجة وروبوتيك, برمجة, روبوتيك"},
    "slides": [], "projects": [], "achievements": [],
    "students": [{"id": "demo1", "name": "طالب تجريبي ١", "photo": "", "track": "برمجة وروبوتيك", "percent": 20, "note": ""},
                 {"id": "demo2", "name": "طالب تجريبي ٢", "photo": "", "track": "برمجة وروبوتيك", "percent": 55, "note": ""}]}
C = {  # مجموعة: (عنوان, حقول)
 'students': ('الطلاب', [('name','الاسم','text'),('photo','الصورة','img'),('track','المسار','track'),('percent','نسبة الإنجاز من خارطة الطريق %','pct'),('note','ملاحظة','area')]),
 'slides': ('صور السلايدر', [('image','الصورة (يدعم GIF المتحرك)','img'),('caption','عنوان يظهر على الصورة','text')]),
 'projects': ('المشاريع', [('title','اسم المشروع','text'),('image','صورة المشروع','img'),('desc','وصف المشروع','area')]),
 'achievements': ('الإنجازات', [('title','عنوان الإنجاز','text'),('date','التاريخ','text'),('image','صورة','img'),('desc','الوصف','area')])}
SET_FIELDS = [('name','اسم الأكاديمية'),('tagline','الشعار'),('about','نبذة عن الأكاديمية'),('vision','الرؤية'),('address','العنوان'),
              ('phone','الهاتف / واتساب'),('email','البريد'),('beneficiaries','عدد المستفيدين الكلي'),('tracks','المسارات (مفصولة بفاصلة)')]

def gh(m, path, **kw):
    return requests.request(m, f'https://api.github.com/repos/{REPO}/contents/{path}', timeout=30, headers={'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json'}, **kw)
_c = {'d': None, 'sha': None}; _lk = threading.Lock()
def load():
    with _lk:
        if _c['d'] is None:
            if REMOTE:
                r = gh('GET', 'docs/data.json', params={'ref': BR})
                if r.ok: j = r.json(); _c['sha'] = j['sha']; _c['d'] = json.loads(base64.b64decode(j['content']))
            if _c['d'] is None: _c['d'] = json.loads(DF.read_text('utf-8')) if DF.exists() else DEFAULT
        return _c['d']
def save(d):
    with _lk:
        _c['d'] = d; DF.parent.mkdir(exist_ok=True); DF.write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
        if REMOTE:
            body = {'message': 'تحديث البيانات', 'branch': BR, 'content': base64.b64encode(DF.read_bytes()).decode()}
            for _ in range(2):
                if _c['sha']: body['sha'] = _c['sha']
                r = gh('PUT', 'docs/data.json', json=body)
                if r.ok: _c['sha'] = r.json()['content']['sha']; return
                g = gh('GET', 'docs/data.json', params={'ref': BR}); _c['sha'] = g.json().get('sha') if g.ok else None
            raise RuntimeError('تعذّر الحفظ في GitHub: ' + r.text[:150])
def stage_of(p): return 1 if p <= 0 else min(6, math.ceil(p/(100/6) - 1e-9))
def save_img(f, square=False):
    ext = Path(f.filename).suffix.lower()
    if ext not in ('.jpg','.jpeg','.png','.webp','.gif'): raise ValueError('صيغة الصورة غير مدعومة')
    UP.mkdir(parents=True, exist_ok=True); im = Image.open(f.stream)
    if ext == '.gif': name = uuid.uuid4().hex[:10] + '.gif'; f.stream.seek(0); f.save(UP/name); push_img(name); return 'uploads/' + name
    im = ImageOps.exif_transpose(im).convert('RGB')
    im = ImageOps.fit(im, (600, 600)) if square else (im.thumbnail((1600, 1600)) or im)
    name = uuid.uuid4().hex[:10] + '.webp'; im.save(UP/name, 'WEBP', quality=82); push_img(name); return 'uploads/' + name
def push_img(n):
    if REMOTE:
        r = gh('PUT', 'docs/uploads/' + n, json={'message': 'رفع صورة', 'branch': BR, 'content': base64.b64encode((UP/n).read_bytes()).decode()})
        if not r.ok: raise RuntimeError('تعذّر رفع الصورة إلى GitHub')
def rm_img(p):
    if p and p.startswith('uploads/'):
        (DOCS/p).unlink(missing_ok=True)
        if REMOTE:
            g = gh('GET', 'docs/' + p, params={'ref': BR})
            if g.ok: gh('DELETE', 'docs/' + p, json={'message': 'حذف صورة', 'branch': BR, 'sha': g.json()['sha']})

def build():
    d = load(); s = d['settings']
    for x in DOCS.iterdir():
        if x.name not in ('uploads', '.nojekyll', 'data.json'): shutil.rmtree(x) if x.is_dir() else x.unlink()
    shutil.copytree(B/'static', DOCS/'assets'); shutil.move(DOCS/'assets'/'admin.html', DOCS/'admin.html')
    studs = [dict(x, percent=x['percent'], stage=stage_of(x['percent'])) for x in d['students']]
    env = Environment(loader=FileSystemLoader(B/'templates'), autoescape=True)
    env.filters['ar'] = lambda v: str(v).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
    tracks = [t.strip() for t in s['tracks'].split(',') if t.strip()]
    for page in ('index','students','projects','platform','achievements','about'):
        (DOCS/f'{page}.html').write_text(env.get_template('site.html').render(page=page, s=s, d=d, studs=studs, stages=STAGES, tracks=tracks), 'utf-8')
    return f"تم بناء الموقع ({len(studs)} طالب)"

PAGES = ('index','students','projects','platform','achievements','about')
app = Flask(__name__, static_folder='admin_static', static_url_path='/static', template_folder='templates')
app.config.update(MAX_CONTENT_LENGTH=20*1024*1024, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=REMOTE)
AF.parent.mkdir(exist_ok=True)
if not AF.exists(): AF.write_text(json.dumps({"hash": generate_password_hash("sanabel123"), "default": True, "key": secrets.token_hex(16)}))
app.secret_key = os.environ.get('SECRET_KEY') or hashlib.sha256((os.environ.get('ADMIN_PASSWORD') or json.loads(AF.read_text())['key']).encode()).hexdigest()
def pw_ok(p):
    e = os.environ.get('ADMIN_PASSWORD')
    return secrets.compare_digest(p, e) if e else check_password_hash(json.loads(AF.read_text())['hash'], p)
TR = lambda: [t.strip() for t in load()['settings']['tracks'].split(',') if t.strip()]
@app.context_processor
def inj():
    if 'csrf' not in session: session['csrf'] = secrets.token_hex(8)
    return dict(csrf=session['csrf'], C=C, stages=STAGES, ar=lambda v: str(v).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')), stage_of=stage_of, counts={k: len(load()[k]) for k in C})
@app.before_request
def guard():
    if request.method == 'POST' and request.form.get('csrf') != session.get('csrf'): abort(400)
    if request.path.startswith('/admin') and request.endpoint != 'login' and not session.get('ok'): return redirect('/admin/login')
# ---------- الموقع العام ----------
@app.route('/')
def idx(): return send_from_directory(DOCS, 'index.html')
@app.route('/<page>.html')
def pg(page):
    if page not in PAGES: abort(404)
    return send_from_directory(DOCS, page + '.html')
@app.route('/assets/<path:p>')
def assets(p): return send_from_directory(DOCS/'assets', p)
@app.route('/data.json')
def data():
    r = jsonify(load()); r.headers['Cache-Control'] = 'no-store'; return r
@app.route('/uploads/<n>')
def upl(n):
    if not (UP/n).exists() and REMOTE:
        r = requests.get(f'https://api.github.com/repos/{REPO}/contents/docs/uploads/{n}', params={'ref': BR}, timeout=30, headers={'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github.raw'})
        if r.ok: UP.mkdir(parents=True, exist_ok=True); (UP/n).write_bytes(r.content)
    r = send_from_directory(UP, n); r.headers['Cache-Control'] = 'public, max-age=86400'; return r
# ---------- لوحة التحكم ----------
@app.route('/admin/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if pw_ok(request.form['pw']): session['ok'] = 1; return redirect('/admin')
        import time; time.sleep(1); flash('كلمة المرور غير صحيحة')
    return render_template('admin.html', v='login')
@app.route('/admin/logout')
def logout(): session.clear(); return redirect('/admin/login')
@app.route('/admin')
def home():
    d = load(); dist = [0]*6
    for s in d['students']: dist[stage_of(s['percent'])-1] += 1
    return render_template('admin.html', v='home', d=d, dist=dist, default=(not os.environ.get('ADMIN_PASSWORD')) and json.loads(AF.read_text()).get('default'), remote=REMOTE)
@app.route('/admin/c/<c>')
def lst(c):
    if c not in C: abort(404)
    return render_template('admin.html', v='list', c=c, items=load()[c], item={}, tracks=TR())
@app.route('/admin/c/<c>/<i>', methods=['GET','POST'])
def edit(c, i):
    if c not in C: abort(404)
    d = load(); items = d[c]; it = next((x for x in items if x['id'] == i), None)
    if request.method == 'POST':
        try:
            if request.form.get('del'):
                if it: items.remove(it); save(d); [rm_img(it.get(k)) for k, _, t in C[c][1] if t == 'img']
            else:
                new = it is None; it = it or {'id': uuid.uuid4().hex[:8]}
                for k, _, t in C[c][1]:
                    if t == 'img':
                        f = request.files.get(k)
                        if f and f.filename: old = it.get(k); it[k] = save_img(f, square=(k == 'photo')); rm_img(old)
                        else: it.setdefault(k, '')
                    elif t == 'pct': it[k] = max(0, min(100, int(request.form.get(k) or 0)))
                    else: it[k] = request.form.get(k, '').strip()
                if new: items.append(it)
                save(d)
            flash('تم الحفظ بنجاح ✓')
        except Exception as e: _c['d'] = None; flash(f'تعذّر الحفظ: {e}')
        return redirect(f'/admin/c/{c}')
    return render_template('admin.html', v='list', c=c, items=items, item=it or {'id': 'new'}, tracks=TR())
@app.route('/admin/settings', methods=['GET','POST'])
def settings():
    d = load()
    if request.method == 'POST':
        for k, _ in SET_FIELDS: d['settings'][k] = request.form.get(k, '').strip()
        try: save(d)
        except Exception as e: _c['d'] = None; flash(str(e)); return redirect('/admin/settings')
        if request.form.get('pw') and not os.environ.get('ADMIN_PASSWORD'): AF.write_text(json.dumps(dict(json.loads(AF.read_text()), hash=generate_password_hash(request.form['pw']), default=False)))
        flash('تم الحفظ بنجاح ✓'); return redirect('/admin/settings')
    return render_template('admin.html', v='settings', d=d, F=SET_FIELDS, envpw=bool(os.environ.get('ADMIN_PASSWORD')))

if __name__ == '__main__':
    build(); threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000/admin')).start()
    app.run('127.0.0.1', 5000)
