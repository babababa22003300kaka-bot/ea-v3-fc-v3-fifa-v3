# app.py - التطبيق الرئيسي المحسن والمعاد تنظيمه - نسخة مُصححة
"""
🚀 FC 26 Profile System - النسخة المعاد تنظيمها
================================================
تطبيق ويب متكامل لإدارة ملفات المستخدمين مع التحقق من الواتساب
والربط مع التليجرام وأنظمة الدفع المصرية

البنية الجديدة:
- وزارة التحقق (validators.py)
- وزارة التليجرام (telegram_manager.py)
- وزارة البيانات (profile_handler.py)
- وزارة الإعدادات (app_config.py)
"""

import json
import os  # 🔥 إضافة import os المطلوب لـ os.urandom()
import re  # 🔥 إضافة هذا الاستيراد المفقود
from datetime import datetime

from dotenv import load_dotenv  # <--- ✅✅ السطر الأول المطلوب هنا ✅✅
from flask import jsonify, render_template, request, session

load_dotenv()  # <--- ✅✅ السطر الثاني المطلوب هنا ✅✅


# ============================================================================
# 🏛️ الخطوة 1: استيراد جميع الوزارات مرة واحدة في الأعلى
# ============================================================================

# استيراد الوزارات المتخصصة
from app_config import app_config, create_flask_app, generate_csrf_token
from profile_handler import create_user_profile, profile_handler
from telegram_manager import (
    create_telegram_code,
    get_payment_display_text,
    process_telegram_webhook,
    telegram_manager,
)
from validators import (
    sanitize_input,
    validate_card_number,
    validate_instapay_link,
    validate_mobile_payment,
    validate_whatsapp_ultimate,
)

# ... (باقي الملف يبقى كما هو) ...
# ============================================================================
# 🚀 الخطوة 2: إنشاء التطبيق وتهيئته
# ============================================================================

# إنشاء التطبيق مع الإعدادات المحسنة
app = create_flask_app()


print("🚀 FC 26 Profile System بدأ التشغيل مع البنية المعاد تنظيمها")
print(f"📊 ملخص الإعدادات: {app_config.get_config_summary()}")

# تعيين webhook للتليجرام تلقائياً عند بدء التشغيل
if telegram_manager.bot_token:
    print("🔄 محاولة تعيين Telegram Webhook...")
    webhook_result = telegram_manager.set_webhook()
    if webhook_result.get("success"):
        print("✅ تم تعيين Telegram Webhook بنجاح")
    else:
        print(f"⚠️ فشل تعيين Webhook: {webhook_result.get('error')}")
else:
    print("⚠️ لا يمكن تعيين Webhook - TELEGRAM_BOT_TOKEN غير موجود")

# ============================================================================
# 🛡️ الخطوة 3: التحقق من الإعدادات (حارس البوابة)
# ============================================================================

# في بداية التطبيق
config_validation = app_config.validate_config()
if not config_validation[0]:
    print("❌ فشل في التحقق من الإعدادات:")
    for error in config_validation[1]:
        print(error)
    # في بيئة الإنتاج، قم بإلغاء التعليق على السطر التالي:
    # exit(1)


# ============================================================================
# 🔑 الخطوة 4: إعداد الجلسات والأمان
# ============================================================================


@app.before_request
def before_request():
    """تهيئة الجلسة - محدثة لحل مشاكل CSRF"""
    if "csrf_token" not in session:
        session["csrf_token"] = generate_csrf_token()
        session.permanent = True


# ============================================================================
# 🏰 وزارة لوحة التحكم - Dashboard Ministry Routes
# ============================================================================

# استيراد وزارة لوحة التحكم
try:
    from dashboard_ministry import (
        dashboard_ministry,
        export_data,
        get_analytics,
        get_dashboard_data,
    )

    print("🏰 وزارة لوحة التحكم محملة بنجاح")
except ImportError:
    print("⚠️ تحذير: لم يتم العثور على وزارة لوحة التحكم")
    dashboard_ministry = None

# 🏰 استيراد وزارة الهوية الصامتة - Identity Ministry
try:
    from identity_ministry import IdentityMinistry
    identity_ministry = IdentityMinistry()
    if identity_ministry.initialize():
        print("🕵️ وزارة الهوية الصامتة محملة ومُهيأة بنجاح")
    else:
        print("⚠️ فشل في تهيئة وزارة الهوية الصامتة")
        identity_ministry = None
except ImportError as e:
    print(f"⚠️ تحذير: لم يتم العثور على وزارة الهوية الصامتة: {e}")
    identity_ministry = None


@app.route("/dashboard")
def dashboard_page():
    """صفحة لوحة التحكم الرئيسية"""
    return render_template("dashboard.html")


@app.route("/api/dashboard-data")
def dashboard_data_api():
    """API لجلب بيانات لوحة التحكم"""
    if not dashboard_ministry:
        return jsonify({"success": False, "error": "وزارة لوحة التحكم غير متاحة"}), 503

    try:
        result = get_dashboard_data()
        return jsonify(result)
    except Exception as e:
        print(f"خطأ في API لوحة التحكم: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard-analytics")
def dashboard_analytics_api():
    """API لجلب التحليلات فقط"""
    if not dashboard_ministry:
        return jsonify({"success": False, "error": "وزارة لوحة التحكم غير متاحة"}), 503

    try:
        result = get_analytics()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard-export")
def dashboard_export_api():
    """API لتصدير بيانات لوحة التحكم"""
    if not dashboard_ministry:
        return jsonify({"success": False, "error": "وزارة لوحة التحكم غير متاحة"}), 503

    try:
        result = export_data()

        if result["success"]:
            # إرجاع البيانات كـ JSON file للتحميل
            response = jsonify(result["export_data"])
            response.headers["Content-Disposition"] = (
                f'attachment; filename=fc26_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# 🕵️ وزارة الهوية الصامتة - Identity Ministry API Routes
# ============================================================================

@app.route("/api/identity/request", methods=["POST"])
def identity_request_api():
    """API لطلب تسجيل هوية صامتة جديدة"""
    if not identity_ministry:
        return jsonify({"success": False, "error": "وزارة الهوية غير متاحة"}), 503
    
    try:
        # قراءة البيانات من الطلب
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "لا توجد بيانات في الطلب"}), 400
        
        device_fingerprint = data.get('device_fingerprint', '')
        metadata = data.get('metadata', {})
        
        # معالجة الطلب عبر وزارة الهوية
        result = identity_ministry.process_identity_request(device_fingerprint, metadata)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": f"خطأ في معالجة الطلب: {str(e)}"}), 500


@app.route("/api/identity/session", methods=["POST"])  
def identity_session_api():
    """API لإنشاء جلسة جديدة للهوية الصامتة"""
    if not identity_ministry:
        return jsonify({"success": False, "error": "وزارة الهوية غير متاحة"}), 503
    
    try:
        # قراءة البيانات من الطلب
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "لا توجد بيانات في الطلب"}), 400
        
        identity_id = data.get('identity_id', '')
        session_metadata = data.get('metadata', {})
        
        if not identity_id:
            return jsonify({"success": False, "error": "معرف الهوية مطلوب"}), 400
        
        # إنشاء جلسة جديدة
        result = identity_ministry.create_session_for_identity(identity_id, session_metadata)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": f"خطأ في إنشاء الجلسة: {str(e)}"}), 500


@app.route("/api/identity/track-event", methods=["POST"])
def identity_track_event_api():
    """API لتتبع الأحداث للهوية الصامتة"""
    if not identity_ministry:
        return jsonify({"success": False, "error": "وزارة الهوية غير متاحة"}), 503
    
    try:
        # قراءة البيانات من الطلب
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "لا توجد بيانات في الطلب"}), 400
        
        session_id = data.get('session_id', '')
        event_type = data.get('event_type', '')
        event_data = data.get('event_data', {})
        
        if not session_id or not event_type:
            return jsonify({"success": False, "error": "معرف الجلسة ونوع الحدث مطلوبان"}), 400
        
        # تسجيل الحدث
        result = identity_ministry.track_user_event(session_id, event_type, event_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": f"خطأ في تتبع الحدث: {str(e)}"}), 500


# ============================================================================
# 🗺️ الخطوة 5: تعريف مسارات التطبيق (Routes)
# ============================================================================


# ============================================================================
# 🏦 وزارة طلبات البيع - Sell Orders Ministry
# ============================================================================


@app.route("/api/sell-coins", methods=["POST"])
def handle_sell_coins_request():
    """
    API لاستقبال ومعالجة طلبات بيع الكوينز.
    """
    try:
        # 1. قراءة البيانات من الطلب
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "لم يتم إرسال أي بيانات"}), 400

        print(f"🔍 طلب بيع جديد: {data}")

        # 2. التحقق من البيانات الأساسية
        required_fields = ["coins_amount", "transfer_type", "ea_account"]
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "error": "بيانات الطلب ناقصة"}), 400

        # 3. استخدام sell_handler لإنشاء الطلب
        if not sell_handler:
            return (
                jsonify({"success": False, "error": "خدمة بيع الكوينز غير متاحة"}),
                503,
            )

        result = create_sell_request(data)

        # 4. إرسال إشعار تليجرام (إذا كانت الوزارة متاحة)
        if (
            result.get("success")
            and "telegram_manager" in globals()
            and telegram_manager
        ):
            request_id = result.get("request_id", "Unknown")
            message = (
                f"🚀 **طلب بيع جديد - #{request_id}** 🚀\n\n"
                f"👤 **المستخدم:** {data.get('user_id', 'غير معروف')}\n"
                f"💰 **الكمية:** {data.get('coins_amount', 0):,} كوين\n"
                f"⚡ **نوع التحويل:** {data.get('transfer_type', 'غير محدد')}\n"
                f"📧 **حساب EA:** {data.get('ea_account', {}).get('email', 'غير متوفر')}\n\n"
                f"يرجى مراجعة لوحة التحكم للمزيد من التفاصيل."
            )
            try:
                telegram_manager.send_admin_notification(message)
            except:
                print("⚠️ فشل في إرسال إشعار تليجرام")

        # 5. إضافة redirect_url للرد إذا كان الطلب نجح
        if result.get("success"):
            result["redirect_url"] = "/dashboard"

        return jsonify(result)

    except Exception as e:
        print(f"❌ خطأ فادح في معالجة طلب البيع: {str(e)}")
        return jsonify({"success": False, "error": "حدث خطأ داخلي في الخادم"}), 500


@app.route("/")
def index():
    """الصفحة الرئيسية - محدثة"""
    # تأكد من وجود csrf token
    if "csrf_token" not in session:
        session["csrf_token"] = generate_csrf_token()
        session.permanent = True

    return render_template("index.html", csrf_token=session["csrf_token"])


@app.route("/validate-whatsapp", methods=["POST"])
def validate_whatsapp_endpoint():
    """API للتحقق المبتكر من رقم الواتساب - مُحسن مع الوزارة الجديدة"""
    try:
        data = request.get_json()
        phone = sanitize_input(data.get("phone", ""))

        if not phone:
            return jsonify({"is_valid": False, "error": "يرجى إدخال رقم الهاتف"})

        # استخدام وزارة التحقق الجديدة
        result = validate_whatsapp_ultimate(phone)
        return jsonify(result)

    except Exception as e:
        print(f"خطأ في التحقق من الواتساب: {str(e)}")
        return jsonify({"is_valid": False, "error": "خطأ في الخادم"})


@app.route("/update-profile", methods=["POST"])
def update_profile():
    """تحديث الملف الشخصي - محدثة مع الوزارات الجديدة"""
    try:
        client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
        user_agent = request.headers.get("User-Agent", "")

        # التحقق من CSRF
        token = request.form.get("csrf_token")
        session_token = session.get("csrf_token")

        if not token or not session_token or token != session_token:
            session["csrf_token"] = generate_csrf_token()
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "انتهت صلاحية الجلسة، يرجى إعادة تحميل الصفحة",
                        "error_code": "csrf_expired",
                        "new_csrf_token": session["csrf_token"],
                    }
                ),
                403,
            )

        # استخراج البيانات
        form_data = {
            "platform": sanitize_input(request.form.get("platform")),
            "whatsapp_number": sanitize_input(request.form.get("whatsapp_number")),
            "payment_method": sanitize_input(request.form.get("payment_method")),
            "payment_details": sanitize_input(request.form.get("payment_details")),
            "telegram_username": sanitize_input(request.form.get("telegram_username")),
            "email_addresses": sanitize_input(
                request.form.get("email_addresses", "[]")
            ),
        }

        # التحقق من البيانات المطلوبة
        if not all(
            [
                form_data["platform"],
                form_data["whatsapp_number"],
                form_data["payment_method"],
            ]
        ):
            return (
                jsonify({"success": False, "message": "Missing required fields"}),
                400,
            )

        # التحقق من الواتساب باستخدام وزارة التحقق
        whatsapp_validation = validate_whatsapp_ultimate(form_data["whatsapp_number"])
        if not whatsapp_validation.get("is_valid"):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"رقم الواتساب غير صحيح: {whatsapp_validation.get('error', 'رقم غير صالح')}",
                    }
                ),
                400,
            )

        # التحقق من طريقة الدفع
        payment_method = form_data["payment_method"]
        payment_details = form_data["payment_details"]

        if payment_method in [
            "vodafone_cash",
            "etisalat_cash",
            "orange_cash",
            "we_cash",
            "bank_wallet",
        ]:
            if not validate_mobile_payment(payment_details):
                return (
                    jsonify(
                        {"success": False, "message": "Invalid mobile payment number"}
                    ),
                    400,
                )

        elif payment_method == "tilda":
            # 🔥 استخدام re المُستورد الآن
            clean_card = re.sub(r"[^\d]", "", payment_details)
            if not validate_card_number(clean_card):
                return (
                    jsonify({"success": False, "message": "Invalid card number"}),
                    400,
                )
            # 🔥 إضافة تحديث payment_details مع الرقم المُنظف
            form_data["payment_details"] = clean_card

        elif payment_method == "instapay":
            is_valid, extracted_link = validate_instapay_link(payment_details)
            if not is_valid:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "لم يتم العثور على رابط InstaPay صحيح في النص المدخل",
                        }
                    ),
                    400,
                )
            form_data["payment_details"] = extracted_link

        # إنشاء الملف الشخصي باستخدام وزارة البيانات
        result = create_user_profile(form_data, client_ip, user_agent)

        if result["success"]:
            # إضافة معلومات الواتساب للاستجابة
            user_data = result["user_data"]
            user_data["whatsapp_info"] = {
                "country": whatsapp_validation.get("country"),
                "carrier": whatsapp_validation.get("carrier"),
                "whatsapp_status": whatsapp_validation.get("whatsapp_status"),
                "verification_method": whatsapp_validation.get("verification_method"),
                "confidence": whatsapp_validation.get("confidence"),
                "score": whatsapp_validation.get("score"),
            }

            # توليد token جديد للأمان
            session["csrf_token"] = generate_csrf_token()

            response_data = {
                "success": True,
                "message": "تم التحقق بالطرق المبتكرة وحفظ البيانات بنجاح!",
                "user_id": result["user_id"],
                "new_csrf_token": session["csrf_token"],
                "data": user_data,
            }

            return jsonify(response_data)
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("message", "فشل في حفظ البيانات"),
                    }
                ),
                500,
            )

    except Exception as e:
        print(f"خطأ في تحديث الملف الشخصي: {str(e)}")
        print(f"تفاصيل الخطأ: {repr(e)}")  # 🔥 إضافة تفاصيل أكثر للخطأ
        return jsonify({"success": False, "message": "Internal server error"}), 500


@app.route("/generate-telegram-code", methods=["POST"])
def generate_telegram_code_endpoint():
    """API لتوليد كود التليجرام - مُصلحة"""
    try:
        data = request.get_json()

        platform = sanitize_input(data.get("platform", ""))
        whatsapp_number = sanitize_input(data.get("whatsapp_number", ""))

        if not platform or not whatsapp_number:
            return (
                jsonify({"success": False, "message": "يرجى إكمال الملف الشخصي أولاً"}),
                400,
            )

        # استخدام وزارة التليجرام
        result = create_telegram_code(
            platform,
            whatsapp_number,
            data.get("payment_method", ""),
            data.get("payment_details", ""),
            data.get("telegram_username", ""),
        )

        # 🔥 إضافة bot_username للاستجابة
        if "bot_username" not in result:
            result["bot_username"] = telegram_manager.bot_username

        print(f"🤖 Generated Telegram Code Response: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"خطأ في توليد كود التليجرام: {str(e)}")
        return jsonify({"success": False, "message": "خطأ في الخادم"})


@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    """استقبال رسائل من التليجرام بوت - محدثة مع الوزارة الجديدة"""
    try:
        update = request.get_json()

        # استخدام وزارة التليجرام لمعالجة الـ webhook
        result = process_telegram_webhook(update)

        return jsonify({"ok": True, "result": result})

    except Exception as e:
        print(f"خطأ في معالجة telegram webhook: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/get-bot-username", methods=["GET"])
def get_bot_username():
    """الحصول على username البوت - مُصلحة"""
    try:
        # 🔥 إصلاح: إرجاع username البوت بشكل مضمون
        username = telegram_manager.bot_username or "ea_fc_fifa_bot"

        # محاولة الحصول على معلومات البوت الحقيقية
        if telegram_manager.bot_token:
            bot_info = telegram_manager.get_bot_info()
            if bot_info and bot_info.get("username"):
                username = bot_info.get("username")

        print(f"🤖 Returning bot username: @{username}")

        return jsonify(
            {
                "success": True,
                "username": username,
                "bot_username": username,  # 🔥 إضافة للتوافق
            }
        )

    except Exception as e:
        print(f"خطأ في الحصول على username البوت: {str(e)}")
        # 🔥 إرجاع قيمة افتراضية حتى في حالة الخطأ
        return jsonify(
            {
                "success": False,
                "username": "ea_fc_fifa_bot",
                "bot_username": "ea_fc_fifa_bot",
                "error": str(e),
            }
        )


@app.route("/admin-data")
def admin_data():
    """عرض البيانات الإدارية - محدثة مع الوزارات الجديدة"""
    try:
        # جمع البيانات من جميع الوزارات
        telegram_data = telegram_manager.get_admin_data()
        profile_data = profile_handler.get_all_users()
        config_summary = app_config.get_config_summary()

        admin_data = {
            "config": config_summary,
            "telegram": {
                "codes_count": telegram_data["telegram_codes_count"],
                "bot_username": telegram_data["bot_username"],
            },
            "profiles": {"users_count": profile_data["users_count"]},
            "system_info": {
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0 - Modular Architecture",
            },
        }

        return jsonify(admin_data)

    except Exception as e:
        print(f"خطأ في البيانات الإدارية: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/check-telegram-status/<code>")
def check_telegram_status(code):
    """فحص حالة كود التليجرام - محدثة مع الوزارة الجديدة"""
    try:
        status = telegram_manager.check_telegram_status(code)
        return jsonify(status)

    except Exception as e:
        print(f"خطأ في فحص حالة التليجرام: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/set-telegram-webhook", methods=["POST"])
def set_telegram_webhook():
    """تعيين webhook للتليجرام - محدثة مع الوزارة الجديدة"""
    try:
        data = request.get_json()
        webhook_url = data.get("webhook_url")

        if not webhook_url:
            return jsonify({"success": False, "error": "webhook_url مطلوب"}), 400

        result = telegram_manager.set_webhook(webhook_url)
        return jsonify(result)

    except Exception as e:
        print(f"خطأ في تعيين webhook: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/setup-telegram", methods=["GET"])
def setup_telegram():
    """إعداد التليجرام تلقائياً - للاستخدام مرة واحدة"""
    try:
        # تعيين webhook
        result = telegram_manager.set_webhook()

        # اختبار البوت
        bot_info = telegram_manager.get_bot_info()

        setup_info = {
            "webhook_result": result,
            "bot_info": bot_info,
            "config": telegram_manager.get_admin_data(),
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(setup_info)

    except Exception as e:
        print(f"خطأ في إعداد التليجرام: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# 💰 وزارة بيع الكوينز - Sell Coins Ministry Routes
# ============================================================================

# استيراد وزارة بيع الكوينز
try:
    from sell_handler import calculate_price, create_sell_request, sell_handler

    print("💰 وزارة بيع الكوينز محملة بنجاح")
except ImportError:
    print("⚠️ تحذير: لم يتم العثور على وزارة بيع الكوينز")
    sell_handler = None


@app.route("/sell-coins")
def sell_coins_page():
    """صفحة بيع الكوينز"""
    return render_template("sell_coins.html")


@app.route("/api/calculate-price", methods=["POST"])
def calculate_price_api():
    """حساب سعر الكوينز"""
    if not sell_handler:
        return jsonify({"success": False, "error": "الخدمة غير متاحة حالياً"}), 503

    data = request.json
    coins = data.get("coins", 0)
    transfer_type = data.get("transferType", "normal")

    result = calculate_price(coins, transfer_type)
    return jsonify(result)


# ============================================================================
# 🚦 الخطوة 6: تعريف معالجات الأخطاء
# ============================================================================


@app.errorhandler(404)
def not_found(error):
    """معالج خطأ 404"""
    return jsonify({"error": "الصفحة المطلوبة غير موجودة"}), 404


@app.errorhandler(500)
def internal_error(error):
    """معالج خطأ 500"""
    print(f"خطأ داخلي في الخادم: {str(error)}")
    return jsonify({"error": "خطأ داخلي في الخادم"}), 500


# ============================================================================
# 🏁 الخطوة 7: تشغيل التطبيق
# ============================================================================


if __name__ == "__main__":
    print("\n🚀 بدء تشغيل FC 26 Profile System")
    print("📦 البنية الجديدة:")
    print("   ✅ وزارة التحقق (validators.py)")
    print("   ✅ وزارة التليجرام (telegram_manager.py)")
    print("   ✅ وزارة البيانات (profile_handler.py)")
    print("   ✅ وزارة الإعدادات (app_config.py)")
    print("   ✅ التطبيق الرئيسي المُحسن (app.py)")

    # 🔥 إصلاح: استخدام القيم مباشرة من app_config
    host = app_config.HOST or "0.0.0.0"
    port = app_config.PORT or 10000
    debug = app_config.DEBUG or False

    print(f"\n🌐 Server starting on {host}:{port} (debug={debug})")

    app.run(host=host, port=port, debug=debug)
