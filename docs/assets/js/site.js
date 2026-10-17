(function(){
const sl=[...document.querySelectorAll('.slide')],dots=document.querySelector('.dots');let i=0,t;
function go(n){sl[i].classList.remove('on');i=(n+sl.length)%sl.length;sl[i].classList.add('on');if(dots)[...dots.children].forEach((d,k)=>d.classList.toggle('on',k==i))}
if(sl.length>1){sl.forEach((_,k)=>{const b=document.createElement('button');b.setAttribute('aria-label','صورة '+(k+1));b.onclick=()=>{go(k);play()};dots.append(b)});go(0);
const h=document.querySelector('.hero');function play(){clearInterval(t);t=setInterval(()=>go(i+1),5500)}play();h.onmouseenter=()=>clearInterval(t);h.onmouseleave=play}
const io=new IntersectionObserver(e=>e.forEach(x=>x.isIntersecting&&x.target.classList.add('in')),{threshold:.3});
document.querySelectorAll('.bar,.stairs').forEach(b=>io.observe(b));
document.querySelectorAll('.filters button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.filters button').forEach(x=>x.classList.toggle('on',x==b));
document.querySelectorAll('.stu').forEach(c=>c.hidden=b.dataset.f&&c.dataset.track!=b.dataset.f)});
})();
