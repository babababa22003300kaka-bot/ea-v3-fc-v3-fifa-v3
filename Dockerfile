# Dockerfile for Playwright on Render

# 1. ابدأ من صورة بايثون رسمية مجهزة بـ Playwright
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. انقل ملفات المشروع جوه الصندوق
WORKDIR /app
COPY requirements.txt .
COPY . .

# 3. ثبت المكتبات بتاعتك
RUN pip install -r requirements.txt

# 4. حدد الأمر اللي هيشتغل لما الصندوق يقوم
CMD ["python", "app.py"]
