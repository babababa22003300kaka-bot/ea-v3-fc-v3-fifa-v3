#!/usr/bin/env python3
"""
إصلاح بسيط وآمن لمشكلة Markdown parsing
- نزيل parse_mode فقط من الرسائل
- لا نلمس أي مناطق محظورة
"""

# قراءة الملف
with open('app_complete.py', 'r') as f:
    lines = f.readlines()

# البحث عن parse_mode وإزالته بحذر
new_lines = []
for i, line in enumerate(lines):
    # نزيل parse_mode فقط من المناطق الآمنة
    if "parse_mode" in line and "# parse_mode removed" in line:
        # ده معناه إنه اتعدل خلاص، نسيبه
        new_lines.append(line)
    elif "parse_mode='Markdown'" in line:
        # نشيل parse_mode='Markdown' من السطر
        new_line = line.replace("parse_mode='Markdown'", "")
        # نشيل الفاصلة الزيادة لو موجودة
        new_line = new_line.replace(", ,", ",").replace("(,", "(").replace(",)", ")")
        new_lines.append(new_line)
    else:
        new_lines.append(line)

# كتابة الملف المعدل
with open('app_complete_fixed.py', 'w') as f:
    f.writelines(new_lines)

print("✅ تم إنشاء app_complete_fixed.py")
