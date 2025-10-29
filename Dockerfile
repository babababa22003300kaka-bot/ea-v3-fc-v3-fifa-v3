# Dockerfile النهائي لـ Playwright على Render
# الإصدار: 5.0 - مضمون للعمل

# 1. ابدأ من الصورة الرسمية والمجهزة مسبقاً من مايكروسوفت
# هذه الصورة تحتوي على Python 3.10 وكل اعتماديات المتصفحات
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. انقل ملفات المشروع إلى مجلد /app داخل الصندوق
WORKDIR /app

# 3. انسخ ملف المتطلبات أولاً (للاستفادة من الكاش في Docker)
COPY requirements.txt .

# 4. ثبت مكتبات البايثون الخاصة بك
RUN pip install -r requirements.txt

# 5. انسخ باقي ملفات المشروع (app.py, injector.js, config.json, etc.)
COPY . .

# 6. حدد الأمر الذي سيتم تشغيله عند بدء تشغيل الخدمة
CMD ["python", "app.py"]
