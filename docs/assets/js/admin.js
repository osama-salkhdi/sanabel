const E=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),$=q=>document.querySelector(q);
const ST=["تعلّم أساسيات البحث العلمي","تعلّم البرمجة بلغة C++","الانتقال إلى المحاكاة بواسطة Tinkercad","اختيار مشاريع لاكتساب المهارة والبدء بالعمل على الهاردوير","تعليم الروبوتيك للطلبة الجدد","ابتكار مشاريع ذات أثر مجتمعي"];
const C={students:['الطلاب',[['name','الاسم','text'],['photo','الصورة','img'],['track','المسار','track'],['percent','نسبة الإنجاز من خارطة الطريق','pct'],['note','ملاحظة','area']]],
slides:['صور السلايدر',[['image','الصورة (GIF متحرك مدعوم)','img'],['caption','عنوان على الصورة','text']]],
projects:['المشاريع',[['title','اسم المشروع','text'],['image','صورة المشروع','img'],['desc','وصف المشروع','area']]],
achievements:['الإنجازات',[['title','عنوان الإنجاز','text'],['date','التاريخ','text'],['image','صورة','img'],['desc','الوصف','area']]],
settings:['الإعدادات',[['name','اسم الأكاديمية'],['tagline','الشعار'],['about','نبذة','area'],['vision','الرؤية','area'],['address','العنوان'],['phone','الهاتف'],['email','البريد'],['beneficiaries','عدد المستفيدين الكلي'],['tracks','المسارات (مفصولة بفاصلة)']]]};
let cfg=JSON.parse(localStorage.sb||'null'),D,sha,tab=(location.hash||'#students').slice(1),eid=null;
const b64=s=>btoa(unescape(encodeURIComponent(s))),unb=s=>decodeURIComponent(escape(atob(s.replace(/\s/g,''))));
async function api(p,o={}){const r=await fetch(`https://api.github.com/repos/${cfg.repo}/contents/${p}`,{...o,headers:{Authorization:'Bearer '+cfg.token,Accept:'application/vnd.github+json'}});
const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(r.status+' '+(j.message||''));return j}
const msg=(t,bad)=>{const e=$('#st');if(e){e.textContent=t;e.className='msg'+(bad?' warn':'')}};
function login(m=''){$('#nav').innerHTML='';$('#m').innerHTML=`<form class="box login" id="lf" style="text-align:start"><h1>دخول لوحة التحكم</h1>${m?`<div class="msg warn">${m}</div>`:''}
<label>المستودع<input name="repo" value="${E(cfg?.repo||'osama-salkhdi/sanabel')}" dir="ltr"></label><label>مفتاح الوصول (Token)<input name="token" type="password" dir="ltr" required></label><button>دخول</button>
<p><small>يُحفظ المفتاح في هذا المتصفح فقط.</small></p></form>`;
$('#lf').onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target);cfg={repo:f.get('repo').trim(),token:f.get('token').trim()};try{await load();localStorage.sb=JSON.stringify(cfg);draw()}catch(x){login('تعذّر الدخول: '+x.message)}}}
async function load(){const j=await api('docs/data.json');sha=j.sha;D=JSON.parse(unb(j.content))}
async function save(m){msg('جارٍ الحفظ...');try{const j=await api('docs/data.json',{method:'PUT',body:JSON.stringify({message:m,content:b64(JSON.stringify(D,null,1)),sha})});sha=j.content.sha;msg('تم الحفظ ✓ — تظهر التغييرات على الموقع خلال دقيقة تقريباً')}
catch(x){msg('فشل الحفظ: '+x.message+' (حدّث الصفحة وأعد المحاولة)',1);throw x}}
async function prep(f,sq){const ext=f.type=='image/gif'?'gif':'webp',name=Math.random().toString(36).slice(2,12)+'.'+ext;
if(ext=='gif')return[name,await new Promise(r=>{const x=new FileReader;x.onload=()=>r(x.result.split(',')[1]);x.readAsDataURL(f)})];
const bm=await createImageBitmap(f),c=document.createElement('canvas'),g=c.getContext('2d');
if(sq){c.width=c.height=600;const m=Math.min(bm.width,bm.height);g.drawImage(bm,(bm.width-m)/2,(bm.height-m)/2,m,m,0,0,600,600)}else{const k=Math.min(1,1600/Math.max(bm.width,bm.height));c.width=bm.width*k;c.height=bm.height*k;g.drawImage(bm,0,0,c.width,c.height)}
return[name,c.toDataURL('image/webp',.82).split(',')[1]]}
async function up(f,sq){const[n,c]=await prep(f,sq);await api('docs/uploads/'+n,{method:'PUT',body:JSON.stringify({message:'رفع صورة',content:c})});return'uploads/'+n}
async function rmImg(p){if(!p||!p.startsWith('uploads/'))return;try{const j=await api('docs/'+p);await api('docs/'+p,{method:'DELETE',body:JSON.stringify({message:'حذف صورة',sha:j.sha})})}catch(e){}}
function draw(){location.hash=tab;$('#nav').innerHTML='<img src="assets/img/mark.png" style="width:100%;background:#f7eee7;border-radius:8px;margin-bottom:10px" alt="">'+Object.keys(C).map(k=>`<a href="#${k}" data-t="${k}">${C[k][0]}</a>`).join('')+'<a href="index.html" target="_blank">عرض الموقع ↗</a><a href="#" id="out">خروج</a>';
document.querySelectorAll('[data-t]').forEach(a=>a.onclick=e=>{e.preventDefault();tab=a.dataset.t;eid=null;draw()});$('#out').onclick=e=>{e.preventDefault();localStorage.removeItem('sb');location.reload()};
tab=='settings'?sets():list()}
function sets(){$('#m').innerHTML=`<h1>الإعدادات</h1><div id="st"></div><form class="box" id="f">${C.settings[1].map(([k,l,t])=>`<label>${l}${t=='area'?`<textarea name="${k}" rows="3">${E(D.settings[k])}</textarea>`:`<input name="${k}" value="${E(D.settings[k])}">`}</label>`).join('')}<button>حفظ</button></form>`;
$('#f').onsubmit=async e=>{e.preventDefault();new FormData(e.target).forEach((v,k)=>D.settings[k]=v.trim());save('تحديث الإعدادات')}}
function list(){const fl=C[tab][1],items=D[tab],it=items.find(x=>x.id==eid)||{},tr=D.settings.tracks.split(',').map(x=>x.trim());
$('#m').innerHTML=`<h1>${C[tab][0]}</h1><div id="st"></div><form class="box" id="f"><h2>${it.id?'تعديل':'إضافة جديد'}</h2>${fl.map(([k,l,t])=>`<label>${l}${t=='img'?(it[k]?`<img class="th" src="${E(it[k])}">`:'')+`<input type="file" name="${k}" accept="image/*">`:t=='area'?`<textarea name="${k}" rows="4">${E(it[k]||'')}</textarea>`:t=='track'?`<select name="${k}">${tr.map(x=>`<option${it[k]==x?' selected':''}>${E(x)}</option>`).join('')}</select>`:t=='pct'?`<span class="pv"><input type="range" name="${k}" min="0" max="100" value="${it[k]||0}"><b></b></span><small></small>`:`<input name="${k}" value="${E(it[k]||'')}"${k==fl[0][0]?' required':''}>`}</label>`).join('')}<button id="sv">حفظ</button>${it.id?' <a href="#" id="cn">إلغاء</a>':''}</form>
<div class="rows">${items.map(x=>`<div class="row">${x.photo||x.image?`<img src="${E(x.photo||x.image)}">`:'<span class="ph"></span>'}<span><b>${E(x.name||x.title||x.caption||'بدون عنوان')}</b>${tab=='students'?`<br><small>${E(x.track)} — ${x.percent}٪</small>`:''}</span><a href="#" data-e="${x.id}">تعديل</a><button class="red" data-d="${x.id}">حذف</button></div>`).join('')}</div>`;
const r=$('input[type=range]');if(r){const u=()=>{const p=+r.value,n=Math.min(6,Math.max(1,Math.ceil(p/16.667-1e-9)));r.nextElementSibling.textContent=p+'٪';r.parentNode.nextElementSibling.textContent='المرحلة '+n+' من 6: '+ST[n-1];r.style.accentColor=p<34?'#d9bc8c':p<67?'#ba925f':'#214539'};r.oninput=u;u()}
if($('#cn'))$('#cn').onclick=e=>{e.preventDefault();eid=null;list()};
document.querySelectorAll('[data-e]').forEach(a=>a.onclick=e=>{e.preventDefault();eid=a.dataset.e;list();scrollTo(0,0)});
document.querySelectorAll('[data-d]').forEach(b=>b.onclick=async()=>{if(!confirm('حذف؟'))return;const x=items.find(y=>y.id==b.dataset.d);items.splice(items.indexOf(x),1);try{await save('حذف');await rmImg(x.photo||x.image)}catch(e){items.push(x)}eid=null;list()});
$('#f').onsubmit=async e=>{e.preventDefault();$('#sv').disabled=true;const f=new FormData(e.target),o=it.id?it:{id:Math.random().toString(36).slice(2,10)};
try{msg('جارٍ رفع الصورة والحفظ...');for(const[k,,t]of fl){if(t=='img'){const fi=f.get(k);if(fi&&fi.size){const old=o[k];o[k]=await up(fi,k=='photo');if(old)rmImg(old)}else o[k]=o[k]||''}else o[k]=t=='pct'?+f.get(k):f.get(k).trim()}
if(!it.id)items.push(o);await save('تحديث '+C[tab][0]);eid=null;list()}catch(x){msg('خطأ: '+x.message,1);$('#sv').disabled=false}}}
cfg?load().then(draw).catch(()=>login('انتهت الجلسة، أعد الدخول')):login();
