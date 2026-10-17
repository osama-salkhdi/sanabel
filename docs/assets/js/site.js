(async function(){
const E=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),AR=v=>String(v).replace(/\d/g,d=>'٠١٢٣٤٥٦٧٨٩'[d]);
const ST=["تعلّم أساسيات البحث العلمي","تعلّم البرمجة بلغة C++","الانتقال إلى المحاكاة بواسطة Tinkercad","اختيار مشاريع لاكتساب المهارة والبدء بالعمل على الهاردوير","تعليم الروبوتيك للطلبة الجدد","ابتكار مشاريع ذات أثر مجتمعي"];
const IC=['<circle cx="11" cy="11" r="7"/><path d="m21 21-4-4M11 8v6M8 11h6"/>','<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>','<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4M6 10h3l2-3 2 5 1-2h2"/>','<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>','<rect x="4" y="9" width="16" height="11" rx="3"/><path d="M12 9V5"/><circle cx="12" cy="4" r="1"/><path d="M9 14v1M15 14v1"/>','<path d="M7 20h10M12 20v-9"/><path d="M12 11c0-3 2-5 6-5 0 4-2 6-6 5ZM12 13c0-3-2-5-6-5 0 4 2 6 6 5Z"/>'];
const stage=p=>p<=0?1:Math.min(6,Math.ceil(p/(100/6)-1e-9));
const stairs=()=>`<ol class="stairs">${ST.map((t,i)=>`<li class="st${i+1}${i==5?' last':''}"><span class="n">${AR(i+1)}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${IC[i]}</svg><p>${t}</p></li>`).join('')}</ol>`;
const app=document.getElementById('app'),pg=app.dataset.page;let d;
try{d=await (await fetch('data.json?t='+Date.now(),{cache:'no-store'})).json()}catch(e){app.innerHTML='<section class="wrap"><p class="empty">تعذّر تحميل البيانات.</p></section>';return}
const s=d.settings;document.title=s.name;document.getElementById('bn').textContent=s.name;document.getElementById('ft').innerHTML=`<b>${E(s.name)}</b> — ${E(s.tagline)}`;
const stu=d.students.map(x=>({...x,percent:+x.percent||0,stage:stage(+x.percent||0)})),tracks=s.tracks.split(',').map(x=>x.trim()).filter(Boolean);
const card=x=>`<article class="stu" data-track="${E(x.track)}"><div class="ph">${x.photo?`<img src="${E(x.photo)}" alt="${E(x.name)}" loading="lazy">`:`<span>${E(x.name.slice(0,1))}</span>`}</div><h3>${E(x.name)}</h3><em>${E(x.track)}</em><p>المرحلة ${AR(x.stage)} من ٦: ${ST[x.stage-1]}</p><div class="bar" style="--p:${Math.max(x.percent,1)}" title="${AR(x.percent)}٪ من خارطة الطريق"><i></i><b>${AR(x.percent)}٪</b></div></article>`;
const item=(p,dt)=>`<article class="pr">${p.image?`<img src="${E(p.image)}" alt="${E(p.title)}" loading="lazy">`:''}<h3>${E(p.title)}</h3>${dt&&p.date?`<small>${E(p.date)}</small>`:''}<p>${E(p.desc)}</p></article>`;
const emp=m=>`<p class="empty">${m}</p>`;
const V={
index:()=>`<section class="hero">${d.slides.map((l,i)=>`<figure class="slide${i?'':' on'}"><img src="${E(l.image)}" alt="${E(l.caption)}"><figcaption>${E(l.caption)}</figcaption></figure>`).join('')}<div class="veil">${d.slides.length?'':'<img class="big" src="assets/img/logo.png" alt="">'}<h1>${E(s.name)}</h1><p>${E(s.tagline)}</p><a class="btn" href="students.html">تعرّف على طلابنا</a></div>${d.slides.length>1?'<div class="dots"></div>':''}</section>
<section class="wrap"><h2>خطة الطريق</h2><p class="sub">مراحل التعلّم في ${E(s.name)}: يبدأ كل طالب بمسار البرمجة والروبوتيك ويصعد مرحلة بعد مرحلة</p>${stairs()}</section>
<section class="wrap nums"><h2>المستفيدون من الأكاديمية</h2><div class="cnt"><div><b>${AR(+s.beneficiaries||0)}</b>مستفيد</div><div><b>${AR(stu.length)}</b>طالب متابَع</div><div><b>${AR(d.projects.length)}</b>مشروع</div><div><b>${AR(d.achievements.length)}</b>إنجاز</div></div><div class="faces">${stu.slice(0,14).map(x=>`<span>${x.photo?`<img src="${E(x.photo)}" alt="${E(x.name)}">`:E(x.name.slice(0,1))}</span>`).join('')}</div></section>`,
students:()=>`<section class="wrap"><h1>طلابنا</h1><p class="sub">كل بطاقة تُظهر المسار والمرحلة التي وصل إليها الطالب ونسبة إنجازه من خارطة الطريق</p><div class="filters"><button class="on" data-f="">الكل</button>${tracks.map(t=>`<button data-f="${E(t)}">${E(t)}</button>`).join('')}</div><div class="grid">${stu.map(card).join('')||emp('لم تُضف طلاب بعد.')}</div></section><section class="wrap"><h2>خارطة الطريق</h2>${stairs()}</section>`,
projects:()=>`<section class="wrap"><h1>مشاريعنا</h1><div class="grid g2">${d.projects.map(p=>item(p)).join('')||emp('ستظهر المشاريع هنا قريباً.')}</div></section>`,
platform:()=>`<section class="wrap soon"><img src="assets/img/logo.png" alt=""><h1>منصة التدريب</h1><p class="big">قريباً</p></section>`,
achievements:()=>`<section class="wrap"><h1>إنجازاتنا</h1><div class="grid g2">${[...d.achievements].reverse().map(p=>item(p,1)).join('')||emp('ستظهر الإنجازات هنا قريباً.')}</div></section>`,
about:()=>`<section class="wrap about"><h1>من نحن</h1><p>${E(s.about)}</p><h2>رؤيتنا</h2><p>${E(s.vision)}</p><h2>تواصل معنا</h2><p>${E(s.address)}${s.phone?'<br>'+E(s.phone):''}${s.email?'<br>'+E(s.email):''}</p></section>`};
app.innerHTML=V[pg]();
const sl=[...document.querySelectorAll('.slide')],dots=document.querySelector('.dots');let i=0,t;
function go(n){sl[i].classList.remove('on');i=(n+sl.length)%sl.length;sl[i].classList.add('on');if(dots)[...dots.children].forEach((x,k)=>x.classList.toggle('on',k==i))}
if(sl.length>1){sl.forEach((_,k)=>{const b=document.createElement('button');b.setAttribute('aria-label','صورة '+(k+1));b.onclick=()=>{go(k);play()};dots.append(b)});go(0);
const h=document.querySelector('.hero');function play(){clearInterval(t);t=setInterval(()=>go(i+1),5500)}play();h.onmouseenter=()=>clearInterval(t);h.onmouseleave=play}
const io=new IntersectionObserver(e=>e.forEach(x=>x.isIntersecting&&x.target.classList.add('in')),{threshold:.3});
document.querySelectorAll('.bar,.stairs').forEach(b=>io.observe(b));
document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x==b));document.querySelectorAll('.stu').forEach(c=>c.hidden=b.dataset.f&&c.dataset.track!=b.dataset.f)});
})();
