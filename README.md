# موقع أكاديمية سنابل التقنية (نسخة Render)

## الفكرة
- تطبيق Flask يعرض الموقع ولوحة التحكم (`/admin`) بكلمة مرور.
- البيانات والصور تُحفظ في مستودع GitHub (لأن قرص Render المجاني يُمسح عند إعادة التشغيل).
- الموقع القديم على GitHub Pages يبقى يعمل ويقرأ البيانات نفسها.

## النشر على Render (مجاناً)
1. ارفع محتوى هذا المجلد إلى مستودعك على GitHub (فوق الملفات القديمة).
2. أنشئ مفتاح GitHub: Settings ← Developer settings ← Fine-grained tokens ← المستودع `sanabel` فقط ← Contents: Read and write.
3. في render.com: New ← Blueprint ← اختر المستودع (يقرأ `render.yaml`).
4. أدخل المتغيرات: `GITHUB_TOKEN` (المفتاح) و `ADMIN_PASSWORD` (كلمة مرور اللوحة). `GITHUB_REPO` مضبوط على osama-salkhdi/sanabel.
5. بعد النشر: الموقع على رابط Render، واللوحة على `/admin`.

## ملاحظات
- النسخة المجانية تنام بعد ~15 دقيقة من عدم الاستخدام، وأول فتح بعدها يستغرق نحو دقيقة.
- كل حفظ يُنشئ commit في GitHub دون إعادة نشر على Render (مضبوط في render.yaml).
- تشغيل محلي: `pip install -r requirements.txt && python app.py` (يعمل دون GitHub، وكلمة المرور sanabel123).
