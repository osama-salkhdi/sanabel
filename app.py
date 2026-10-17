# -*- coding: utf-8 -*-
"""أكاديمية سنابل التقنية: لوحة تحكم محلية + مولّد موقع ثابت (GitHub Pages)"""
import json, uuid, math, shutil, subprocess, threading, webbrowser, secrets
from pathlib import Path
from flask import Flask, request, session, redirect, render_template, flash, send_from_directory, abort
from jinja2 import Environment, FileSystemLoader
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageOps

B = Path(__file__).parent; DOCS = B/'docs'; UP = DOCS/'uploads'; DF = B/'data'/'data.json'; AF = B/'data'/'admin.json'
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

def load():
    if not DF.exists(): save(DEFAULT)
    return json.loads(DF.read_text('utf-8'))
def save(d):
    DF.parent.mkdir(exist_ok=True); DF.write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
def stage_of(p): return 1 if p <= 0 else min(6, math.ceil(p/(100/6) - 1e-9))
def save_img(f, square=False):
    ext = Path(f.filename).suffix.lower()
    if ext not in ('.jpg','.jpeg','.png','.webp','.gif'): raise ValueError('صيغة الصورة غير مدعومة')
    UP.mkdir(parents=True, exist_ok=True); im = Image.open(f.stream)
    if ext == '.gif': name = uuid.uuid4().hex[:10] + '.gif'; f.stream.seek(0); f.save(UP/name); return 'uploads/' + name
    im = ImageOps.exif_transpose(im).convert('RGB')
    im = ImageOps.fit(im, (600, 600)) if square else (im.thumbnail((1600, 1600)) or im)
    name = uuid.uuid4().hex[:10] + '.webp'; im.save(UP/name, 'WEBP', quality=82); return 'uploads/' + name
def rm_img(p):
    if p and p.startswith('uploads/'): (DOCS/p).unlink(missing_ok=True)

def build():
    d = load(); s = d['settings']
    for x in DOCS.iterdir():
        if x.name not in ('uploads', '.nojekyll'): shutil.rmtree(x) if x.is_dir() else x.unlink()
    shutil.copytree(B/'static', DOCS/'assets')
    studs = [dict(x, percent=x['percent'], stage=stage_of(x['percent'])) for x in d['students']]
    env = Environment(loader=FileSystemLoader(B/'templates'), autoescape=True)
    env.filters['ar'] = lambda v: str(v).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
    tracks = [t.strip() for t in s['tracks'].split(',') if t.strip()]
    for page in ('index','students','projects','platform','achievements','about'):
        (DOCS/f'{page}.html').write_text(env.get_template('site.html').render(page=page, s=s, d=d, studs=studs, stages=STAGES, tracks=tracks), 'utf-8')
    return f"تم بناء الموقع ({len(studs)} طالب)"

app = Flask(__name__, static_folder='admin_static', template_folder='templates')
if not AF.exists():
    AF.write_text(json.dumps({"hash": generate_password_hash("sanabel123"), "default": True, "key": secrets.token_hex(16)}))
app.secret_key = json.loads(AF.read_text())['key']
@app.context_processor
def inj():
    if 'csrf' not in session: session['csrf'] = secrets.token_hex(8)
    return dict(csrf=session['csrf'], C=C, stages=STAGES, ar=lambda v: str(v).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')))
@app.before_request
def guard():
    if request.method == 'POST' and request.form.get('csrf') != session.get('csrf'): abort(400)
    if request.endpoint not in ('login', 'static') and not session.get('ok'): return redirect('/login')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if check_password_hash(json.loads(AF.read_text())['hash'], request.form['pw']): session['ok'] = 1; return redirect('/')
        flash('كلمة المرور غير صحيحة')
    return render_template('admin.html', v='login')
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
@app.route('/', methods=['GET','POST'])
def home():
    log = ''
    if request.method == 'POST':
        log = build()
        if request.form.get('do') == 'publish':
            for c in (['git','add','-A'], ['git','commit','-m','تحديث الموقع'], ['git','push']):
                r = subprocess.run(c, cwd=B, capture_output=True, text=True, timeout=180); log += f"\n$ {' '.join(c)}\n{r.stdout}{r.stderr}"
    d = load(); return render_template('admin.html', v='home', d=d, log=log, default=json.loads(AF.read_text()).get('default'))
@app.route('/c/<c>')
def lst(c):
    if c not in C: abort(404)
    return render_template('admin.html', v='list', c=c, items=load()[c], item={}, tracks=[t.strip() for t in load()['settings']['tracks'].split(',')])
@app.route('/c/<c>/<i>', methods=['GET','POST'])
def edit(c, i):
    if c not in C: abort(404)
    d = load(); items = d[c]; it = next((x for x in items if x['id'] == i), None)
    if request.method == 'POST':
        if request.form.get('del'):
            if it: [rm_img(it.get(k)) for k, _, t in C[c][1] if t == 'img']; items.remove(it)
        else:
            if not it: it = {'id': uuid.uuid4().hex[:8]}; items.append(it)
            try:
                for k, _, t in C[c][1]:
                    if t == 'img':
                        f = request.files.get(k)
                        if f and f.filename: rm_img(it.get(k)); it[k] = save_img(f, square=(k == 'photo'))
                        else: it.setdefault(k, '')
                    elif t == 'pct': it[k] = max(0, min(100, int(request.form.get(k) or 0)))
                    else: it[k] = request.form.get(k, '').strip()
            except Exception as e: flash(f'تعذّر حفظ الصورة: {e}'); return redirect(request.url)
        save(d); flash('تم الحفظ ✓'); return redirect(f'/c/{c}')
    return render_template('admin.html', v='list', c=c, items=items, item=it or {'id': 'new'}, tracks=[t.strip() for t in d['settings']['tracks'].split(',')])
@app.route('/settings', methods=['GET','POST'])
def settings():
    d = load()
    if request.method == 'POST':
        for k, _ in SET_FIELDS: d['settings'][k] = request.form.get(k, '').strip()
        save(d)
        if request.form.get('pw'): AF.write_text(json.dumps(dict(json.loads(AF.read_text()), hash=generate_password_hash(request.form['pw']), default=False)))
        flash('تم الحفظ ✓'); return redirect('/settings')
    return render_template('admin.html', v='settings', d=d, F=SET_FIELDS)
@app.route('/preview/')
@app.route('/preview/<path:p>')
def preview(p='index.html'): return send_from_directory(DOCS, p)

if __name__ == '__main__':
    build(); threading.Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run('127.0.0.1', 5000)
