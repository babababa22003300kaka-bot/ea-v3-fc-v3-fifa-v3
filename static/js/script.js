// ============================================================================
// 🚀 النظام الأساسي - المتغيرات العامة
// ============================================================================
let isSubmitting = false;
let lastSubmitTime = 0;
let currentTelegramCode = null;
let telegramStatusChecker = null;
let correctBotUsername = null;

let validationStates = {
    whatsapp: false,
    paymentMethod: false,
    platform: false
};

// ============================================================================
// WhatsAppManager DOM Class - تحويل من ES6 Module
// ============================================================================

class WhatsAppManager {
    constructor() {
        this.validPrefixes = ['010', '011', '012', '015'];
        this.whatsappLength = 11;
        this.initialized = false;

        // تخزين العناصر للأداء
        this.whatsappInput = null;
        this.whatsappError = null;
        this.submitButton = null;

        // 🔥 إضافة تهيئة فورية
        this.init();
    }

    // تهيئة النظام
    init() {
        if (this.initialized) return;

        this.whatsappInput = document.getElementById('whatsapp');
        this.whatsappError = document.getElementById('whatsapp-error');
        this.submitButton = document.querySelector('.submit-btn');

        if (this.whatsappInput) {
            this.setupEventListeners();
            this.initialized = true;
            console.log('✅ WhatsAppManager initialized successfully');
        }
    }

    // إعداد مستمعي الأحداث
    setupEventListeners() {
        // التحقق أثناء الكتابة
        this.whatsappInput.addEventListener('input', (e) => {
            this.handleWhatsAppInput(e);
        });

        // التحقق عند فقدان التركيز
        this.whatsappInput.addEventListener('blur', (e) => {
            this.validateWhatsAppNumber(e.target.value);
        });

        // منع إدخال الحروف
        this.whatsappInput.addEventListener('keypress', (e) => {
            this.restrictToNumbers(e);
        });

        // التحقق عند الإرسال
        if (this.submitButton) {
            this.submitButton.addEventListener('click', (e) => {
                if (!this.validateWhatsAppNumber(this.whatsappInput.value)) {
                    e.preventDefault();
                }
            });
        }
    }

    // معالجة إدخال الواتساب
    handleWhatsAppInput(event) {
        let value = event.target.value;

        // تنظيف القيمة
        value = this.cleanWhatsAppNumber(value);
        event.target.value = value;

        // التحقق المباشر
        if (value.length >= 3) {
            this.validateWhatsAppNumber(value, false);
        } else {
            this.hideWhatsAppError();
        }
    }

    // تنظيف رقم الواتساب
    cleanWhatsAppNumber(number) {
        if (!number) return '';

        // إزالة كل شيء عدا الأرقام
        return number.replace(/[^\d]/g, '');
    }

    // تقييد الإدخال للأرقام فقط
    restrictToNumbers(event) {
        const charCode = event.which ? event.which : event.keyCode;

        // السماح بالمفاتيح الخاصة (Backspace, Delete, Arrow keys, etc.)
        if (charCode <= 31 || (charCode >= 48 && charCode <= 57)) {
            return true;
        }

        event.preventDefault();
        return false;
    }

    // التحقق من صحة رقم الواتساب
    validateWhatsAppNumber(number, showError = true) {
        if (!number) {
            if (showError) this.showWhatsAppError('يرجى إدخال رقم الواتساب');
            return false;
        }

        // تنظيف الرقم
        const cleanNumber = this.cleanWhatsAppNumber(number);

        // التحقق من الطول
        if (cleanNumber.length !== this.whatsappLength) {
            if (showError) {
                this.showWhatsAppError(
                    `رقم الواتساب يجب أن يكون ${this.whatsappLength} أرقام بالضبط`
                );
            }
            return false;
        }

        // التحقق من البادئة
        const prefix = cleanNumber.substring(0, 3);
        if (!this.validPrefixes.includes(prefix)) {
            if (showError) {
                this.showWhatsAppError(
                    'رقم الواتساب يجب أن يبدأ بـ ' + this.validPrefixes.join(' أو ')
                );
            }
            return false;
        }

        // إذا وصل هنا، الرقم صحيح
        this.hideWhatsAppError();
        return true;
    }

    // عرض رسالة خطأ الواتساب
    showWhatsAppError(message) {
        if (this.whatsappError) {
            this.whatsappError.textContent = message;
            this.whatsappError.style.display = 'block';
        }

        if (this.whatsappInput) {
            this.whatsappInput.classList.add('error');
        }
    }

    // إخفاء رسالة خطأ الواتساب
    hideWhatsAppError() {
        if (this.whatsappError) {
            this.whatsappError.style.display = 'none';
        }

        if (this.whatsappInput) {
            this.whatsappInput.classList.remove('error');
        }
    }

    // تنسيق رقم الواتساب للعرض
    formatWhatsAppNumber(number) {
        const cleanNumber = this.cleanWhatsAppNumber(number);
        if (cleanNumber.length === this.whatsappLength) {
            return `+20${cleanNumber}`;
        }
        return cleanNumber;
    }

    // الحصول على رقم الواتساب المنظف
    getCleanWhatsAppNumber() {
        if (!this.whatsappInput) return '';
        return this.cleanWhatsAppNumber(this.whatsappInput.value);
    }

    // الحصول على رقم الواتساب المنسق
    getFormattedWhatsAppNumber() {
        return this.formatWhatsAppNumber(this.getCleanWhatsAppNumber());
    }

    // التحقق من حالة الواتساب
    isWhatsAppValid() {
        return this.validateWhatsAppNumber(this.getCleanWhatsAppNumber(), false);
    }

    // إعادة تعيين حقل الواتساب
    resetWhatsApp() {
        if (this.whatsappInput) {
            this.whatsappInput.value = '';
            this.hideWhatsAppError();
        }
    }

    // تحديث القيم المسموحة
    updateValidPrefixes(prefixes) {
        if (Array.isArray(prefixes)) {
            this.validPrefixes = prefixes;
        }
    }

    // تحديث طول الرقم المطلوب
    updateWhatsAppLength(length) {
        if (typeof length === 'number' && length > 0) {
            this.whatsappLength = length;
        }
    }
}



// ============================================================================
// WhatsApp  🚀🚀   - نهاية كلاش واتساب
// ============================================================================


// ============================================================================
// 🎨 WhatsApp Visual Enhancement System - نظام التحسين البصري للواتساب
// ============================================================================

class WhatsAppVisualEnhancer {
    constructor(whatsappManager) {
        this.manager = whatsappManager;
        this.progressBar = null;
        this.statusDisplay = null;
        this.formattedDisplay = null;
        this.initialized = false;
    }

    // تهيئة النظام البصري
    init() {
        if (this.initialized || !this.manager.whatsappInput) return;

        // إنشاء العناصر البصرية
        this.createProgressBar();
        this.createStatusDisplay();
        this.setupEnhancedListeners();

        this.initialized = true;
        console.log('✨ WhatsApp Visual Enhancer initialized');
    }

    // إنشاء شريط التقدم
    createProgressBar() {
        const container = this.manager.whatsappInput.parentNode;

        // إنشاء حاوي شريط التقدم
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'whatsapp-progress';
        this.progressBar.innerHTML = '<div class="whatsapp-progress-fill"></div>';
        // CSS classes will handle styling

        container.appendChild(this.progressBar);
    }

    // إنشاء عرض الحالة
    createStatusDisplay() {
        const container = this.manager.whatsappInput.parentNode;

        this.statusDisplay = document.createElement('div');
        this.statusDisplay.className = 'whatsapp-status';
        // CSS classes will handle styling

        container.appendChild(this.statusDisplay);
    }

    // إعداد المستمعين المحسنين
    setupEnhancedListeners() {
        const input = this.manager.whatsappInput;

        // معالج الإدخال المحسن
        input.addEventListener('input', (e) => {
            this.handleEnhancedInput(e);
        });

        // معالج التركيز
        input.addEventListener('focus', () => {
            this.showProgressBar();
        });

        // معالج فقدان التركيز
        input.addEventListener('blur', () => {
            if (!input.value) {
                this.hideProgressBar();
            }
        });
    }

    // معالجة الإدخال المحسن
    handleEnhancedInput(event) {
        const input = event.target;
        let value = input.value;

        // إزالة كل شيء عدا الأرقام
        const numbersOnly = value.replace(/[^\d]/g, '');

        // تطبيق التنسيق
        const formatted = this.formatWhatsAppNumber(numbersOnly);

        // تحديث القيمة المنسقة فقط إذا تغيرت
        if (formatted !== value) {
            input.value = formatted;
        }

        // تحديث شريط التقدم
        this.updateProgress(numbersOnly.length);

        // تحديث الحالة
        this.updateStatus(numbersOnly);
    }

    // تنسيق رقم الواتساب
    formatWhatsAppNumber(numbers) {
        if (!numbers) return '';
        // تنسيق: بدون فواصل
        let formatted = '';
        if (numbers.length <= 3) {
            formatted = numbers;
        } else if (numbers.length <= 7) {
            formatted = numbers.slice(0, 3) + numbers.slice(3);
        } else {
            formatted = numbers.slice(0, 3) +
                numbers.slice(3, 7) +
                numbers.slice(7, 11);
        }
        return formatted;
    }

    // تحديث شريط التقدم
    updateProgress(length) {
        if (!this.progressBar) return;

        const progressFill = this.progressBar.querySelector('.whatsapp-progress-fill');
        const percentage = Math.min((length / 11) * 100, 100);

        progressFill.style.width = percentage + '%';

        // تغيير اللون حسب التقدم باستخدام CSS classes
        progressFill.className = 'whatsapp-progress-fill';
        if (percentage < 27) { // أقل من 3 أرقام
            progressFill.classList.add('stage-early');
        } else if (percentage < 64) { // 3-7 أرقام
            progressFill.classList.add('stage-partial');
        } else if (percentage < 100) { // 8-10 أرقام
            progressFill.classList.add('stage-almost');
        } else { // 11 رقم كامل
            progressFill.classList.add('stage-complete');
        }
    }

    // تحديث عرض الحالة
    updateStatus(numbers) {
        if (!this.statusDisplay) return;

        const length = numbers.length;
        let message = '';
        let color = '';
        let icon = '';

        if (length === 0) {
            this.hideStatus();
            return;
        } else if (length < 3) {
            message = `جاري الكتابة... (${length}/11)`;
            color = '#F59E0B';
            icon = '⏳';
        } else if (length < 11) {
            const prefix = numbers.substring(0, 3);
            const validPrefixes = ['010', '011', '012', '015'];

            if (!validPrefixes.includes(prefix)) {
                message = 'البادئة غير صحيحة - استخدم 010/011/012/015';
                color = '#EF4444';
                icon = '⚠️';
            } else {
                message = `جاري الكتابة... (${length}/11)`;
                color = '#3B82F6';
                icon = '📱';
            }
        } else if (length === 11) {
            const prefix = numbers.substring(0, 3);
            const validPrefixes = ['010', '011', '012', '015'];

            if (validPrefixes.includes(prefix)) {
                message = 'رقم واتساب صحيح';
                color = '#10B981';
                icon = '✅';

                // اهتزاز نجاح
                if (navigator.vibrate) {
                    navigator.vibrate([50, 30, 50]);
                }
            } else {
                message = 'رقم غير صحيح - تحقق من البادئة';
                color = '#EF4444';
                icon = '❌';
            }
        } else {
            message = 'رقم طويل جداً';
            color = '#EF4444';
            icon = '❌';
        }

        this.showStatus(`${icon} ${message}`, color);
    }

    // إظهار الحالة
    showStatus(message, color) {
        if (!this.statusDisplay) return;

        this.statusDisplay.textContent = message;
        this.statusDisplay.className = 'whatsapp-status show';
        
        // إضافة الكلاس المناسب حسب اللون
        if (color === '#10B981') {
            this.statusDisplay.classList.add('success');
        } else if (color === '#EF4444') {
            this.statusDisplay.classList.add('error');
        } else if (color === '#3B82F6') {
            this.statusDisplay.classList.add('partial');
        }
    }

    // إخفاء الحالة
    hideStatus() {
        if (!this.statusDisplay) return;

        this.statusDisplay.classList.remove('show');
    }

    // إظهار شريط التقدم
    showProgressBar() {
        if (this.progressBar) {
            this.progressBar.classList.add('show');
        }
    }

    // إخفاء شريط التقدم
    hideProgressBar() {
        if (this.progressBar) {
            this.progressBar.classList.remove('show');
        }
    }
}

// إنشاء مثيل عام من المحسن البصري
window.whatsappEnhancer = null;


// ============================================================================
// WhatsApp Real Validation - الدالة المفقودة
// ============================================================================

// 🔥 إضافة هذه الدالة بعد السطر 270
function validateWhatsAppReal(number, showMessages = true) {
    // استخدام WhatsAppManager للتحقق
    if (window.whatsappManager) {
        return window.whatsappManager.validateWhatsAppNumber(number, showMessages);
    }

    // تحقق احتياطي إذا لم يكن WhatsAppManager متاح
    if (!number) return false;

    const cleanNumber = number.replace(/[^\d]/g, '');
    const validPrefixes = ['010', '011', '012', '015'];

    if (cleanNumber.length !== 11) return false;

    const prefix = cleanNumber.substring(0, 3);
    return validPrefixes.includes(prefix);
}

// ============================================================================
// إنشاء المثيل العام
// ============================================================================

// إنشاء مثيل عام من WhatsAppManager
window.whatsappManager = null;

// ============================================================================
// AFTER (السطر - الكود المحدث):
// ============================================================================
// تهيئة WhatsAppManager عند تحميل DOM - محسن
document.addEventListener('DOMContentLoaded', function () {
    if (!window.whatsappManager) {
        window.whatsappManager = new WhatsAppManager();
    }

    // التأكد من التهيئة
    if (window.whatsappManager && !window.whatsappManager.initialized) {
        window.whatsappManager.init();
    }

    // 🎨 تهيئة المحسن البصري الجديد
    if (!window.whatsappEnhancer) {
        window.whatsappEnhancer = new WhatsAppVisualEnhancer(window.whatsappManager);
        window.whatsappEnhancer.init();
    }

    console.log('✅ WhatsApp Manager & Visual Enhancer DOM ready');
});

// ============================================================================
// جسر التوافقية - Backward Compatibility Bridge
// ============================================================================

// ✅✅✅ هذا هو التعديل الصحيح ✅✅✅
function initializeWhatsAppValidator() {
    console.log('🔄 initializeWhatsAppValidator called - using WhatsAppManager');

    if (!window.whatsappManager) {
        window.whatsappManager = new WhatsAppManager();
    }

    // استدعاء init من هنا لضمان أن الـ DOM جاهز
    window.whatsappManager.init();

    return window.whatsappManager;
}

// دوال مساعدة للتوافق مع الكود القديم
window.validateWhatsApp = function (number) {
    if (window.whatsappManager) {
        return window.whatsappManager.validateWhatsAppNumber(number);
    }
    return false;
};

window.cleanWhatsAppNumber = function (number) {
    if (window.whatsappManager) {
        return window.whatsappManager.cleanWhatsAppNumber(number);
    }
    return number;
};

window.formatWhatsAppNumber = function (number) {
    if (window.whatsappManager) {
        return window.whatsappManager.formatWhatsAppNumber(number);
    }
    return number;
};

// تصدير للاستخدام مع ES6 (إذا احتجت لاحقاً)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        WhatsAppManager,
        initializeWhatsAppValidator
    };
}



// FC 26 Platform Module - JS DOM Class النسخة المحولة
class PlatformModule {
    constructor() {
        this.selectedPlatform = null;
        this.platformCards = [];
        this.onPlatformChange = null;
        this.initialized = false;
    }

    /**
     * تهيئة وحدة المنصة
     */
    init(onChangeCallback = null) {
        if (this.initialized) {
            console.warn('🎮 Platform Module already initialized');
            return;
        }

        this.onPlatformChange = onChangeCallback;
        this.setupPlatformCards();
        this.initialized = true;

        console.log('🎮 Platform Module initialized as DOM Class');
    }

    /**
     * إعداد بطاقات المنصة مع مستمعي الأحداث
     */
    setupPlatformCards() {
        this.platformCards = document.querySelectorAll('.platform-card');

        if (this.platformCards.length === 0) {
            console.warn('⚠️ No platform cards found');
            return;
        }

        this.platformCards.forEach(card => {
            card.addEventListener('click', (event) => {
                this.handlePlatformSelection(event, card);
            });

            // تحسينات للهواتف
            if ('ontouchstart' in window) {
                card.addEventListener('touchstart', () => {
                    card.classList.add('touch-active');
                }, { passive: true });

                card.addEventListener('touchend', () => {
                    setTimeout(() => {
                        card.classList.remove('touch-active');
                    }, 150);
                }, { passive: true });
            }
        });

        console.log(`🎮 ${this.platformCards.length} platform cards initialized with DOM Class`);
    }

    /**
     * معالجة اختيار المنصة
     */
    handlePlatformSelection(event, selectedCard) {
        event.preventDefault();

        // إزالة التحديد من جميع البطاقات
        this.clearAllSelections();

        // تحديد البطاقة المختارة
        selectedCard.classList.add('selected');

        // حفظ المنصة المختارة
        const platform = selectedCard.dataset.platform;
        this.selectedPlatform = platform;

        // تحديث الحقل المخفي
        this.updatePlatformInput(platform);

        // تأثيرات بصرية
        this.addSelectionEffects(selectedCard);

        // إشعار النظام الرئيسي
        this.notifyPlatformChange(platform, selectedCard);

        console.log(`🎮 Platform selected via DOM Class: ${platform}`);
    }

    /**
     * إزالة التحديد من جميع البطاقات
     */
    clearAllSelections() {
        this.platformCards.forEach(card => {
            card.classList.remove('selected', 'touch-active');
        });
    }

    /**
     * تحديث الحقل المخفي للمنصة
     */
    updatePlatformInput(platform) {
        const platformInput = document.getElementById('platform');
        if (platformInput) {
            platformInput.value = platform;
        } else {
            console.warn('⚠️ Platform input field not found');
        }
    }

    /**
     * إضافة تأثيرات بصرية للاختيار
     */
    addSelectionEffects(card) {
        // اهتزاز للهواتف
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }

        // تأثير نبضة
        card.classList.add('pulse-effect');
        setTimeout(() => {
            card.classList.remove('pulse-effect');
        }, 300);
    }

    /**
     * إشعار النظام الرئيسي بتغيير المنصة
     */
    notifyPlatformChange(platform, card) {
        if (typeof this.onPlatformChange === 'function') {
            this.onPlatformChange({
                platform: platform,
                card: card,
                isValid: true,
                selectedPlatform: this.selectedPlatform
            });
        }

        // إرسال حدث مخصص للنظام
        const event = new CustomEvent('platformChanged', {
            detail: {
                platform: platform,
                card: card,
                module: this
            }
        });
        document.dispatchEvent(event);
    }

    /**
     * الحصول على المنصة المختارة حالياً
     */
    getSelectedPlatform() {
        return this.selectedPlatform;
    }

    /**
     * التحقق من صحة اختيار المنصة
     */
    isValid() {
        return this.selectedPlatform !== null && this.selectedPlatform !== '';
    }

    /**
     * إعادة تعيين المنصة المختارة
     */
    reset() {
        this.clearAllSelections();
        this.selectedPlatform = null;
        this.updatePlatformInput('');
        console.log('🎮 Platform selection reset');
    }
}

// ============================================================================
// PaymentValidator Class - إصلاح مشاكل التحقق من طرق الدفع
// ============================================================================


// ============================================================================
// النهاية الكلاس و نهاية العزل و صندوق اسود
// ============================================================================


// إنشاء instance عام من الكلاس الجديد
const platformModule = new PlatformModule();

// جسر التوافقية - يحافظ على الواجهة القديمة
function setupPlatformSelection(platformCards) {
    // تهيئة الكلاس الجديد
    platformModule.init((data) => {
        console.log('🎮 [Callback Bridge] تم اختيار المنصة:', data.platform);
        validationStates.platform = data.isValid;
        checkFormValidity();
    });

    // الحفاظ على السلوك القديم
    return platformModule;
}

// تصدير للنافذة العامة للتوافق
window.FC26PlatformModule = platformModule;

// تهيئة التطبيق
document.addEventListener('DOMContentLoaded', function () {
    // إنشاء الجسيمات المتحركة
    createParticles();

    // تهيئة جميع مستمعي الأحداث
    initializeEventListeners();

    // تحسين الأداء للهواتف
    if (window.innerWidth <= 768) {
        optimizeForMobile();
    }

    // تهيئة الميزات المتقدمة
    initializeAdvancedFeatures();
});

// إنشاء الجسيمات المتحركة للخلفية
function createParticles() {
    const container = document.getElementById('particlesBg');
    if (!container) return;

    const particleCount = window.innerWidth <= 768 ? 15 : 25;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 6) + 's';
        container.appendChild(particle);
    }
}

// تحسين للهواتف المحمولة
function optimizeForMobile() {
    // تقليل عدد الجسيمات
    const particles = document.querySelectorAll('.particle');
    particles.forEach((particle, index) => {
        if (index > 10) {
            particle.remove();
        }
    });

    // تحسين الانيميشن
    document.body.style.setProperty('--animation-duration', '0.2s');

    // معالجة لوحة المفاتيح على الهواتف
    setupMobileKeyboardHandling();
}

// معالجة لوحة المفاتيح للهواتف
function setupMobileKeyboardHandling() {
    let viewportHeight = window.innerHeight;

    window.addEventListener('resize', function () {
        const currentHeight = window.innerHeight;
        const heightDifference = viewportHeight - currentHeight;

        if (heightDifference > 150) {
            document.body.classList.add('keyboard-open');
        } else {
            document.body.classList.remove('keyboard-open');
        }
    });

    // تركيز الحقول مع تمرير سلس
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('focus', function () {
            setTimeout(() => {
                this.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }, 300);
        });
    });
}

// ============================================================================
//    (السطر - الكود المحدث):
// ============================================================================
function initializeWhatsAppIntegration() {
    // التأكد من وجود WhatsAppManager
    if (!window.whatsappManager) {
        window.whatsappManager = new WhatsAppManager();
    }

    // التأكد من التهيئة
    if (!window.whatsappManager.initialized) {
        window.whatsappManager.init();
    }

    console.log('✅ WhatsApp Manager is ready');

    // ربط التحقق مع النظام العام
    const whatsappInput = document.getElementById('whatsapp');
    if (whatsappInput) {
        // إزالة المستمعين القدامى
        whatsappInput.removeEventListener('input', handleWhatsAppValidation);
        whatsappInput.removeEventListener('blur', handleWhatsAppValidation);

        // إضافة المستمعين الجدد
        whatsappInput.addEventListener('input', handleWhatsAppValidation);
        whatsappInput.addEventListener('blur', handleWhatsAppValidation);

        console.log('🔗 WhatsApp validation listeners attached');
    }
}

// دالة معالجة التحقق من الواتساب
function handleWhatsAppValidation(event) {
    const input = event.target;
    const value = input.value.trim();

    if (window.whatsappManager) {
        // التحقق من صحة الرقم
        const isValid = window.whatsappManager.validateWhatsAppNumber(value, false);

        // تحديث حالة النظام
        validationStates.whatsapp = isValid;

        // تحديث زر الحفظ
        checkFormValidity();

        console.log('📱 WhatsApp validation:', isValid);
    }
}

// ✅✅✅ النسخة الكاملة والنهائية للدالة ✅✅✅

function initializeEventListeners() {
    console.log('🎯 بدء تهيئة جميع مستمعي الأحداث...');

    // 🔥 الخطوة 1: تهيئة وحدة المنصة الجديدة (DOM Class)
    setupPlatformSelection();
    console.log('✅ Platform Module initialized as DOM Class successfully');

    // 🔥 الخطوة 2: تهيئة باقي عناصر النموذج
    const paymentButtons = document.querySelectorAll('.payment-btn');
    const form = document.getElementById('profileForm');

    // معالجة اختيار طريقة الدفع
    setupPaymentSelection(paymentButtons);

    // تهيئة تكامل الواتساب المحسن
    initializeWhatsAppIntegration();

    // معالجة إرسال النموذج
    setupFormSubmission(form);

    // تهيئة الميزات المتقدمة
    initializeTooltips();
    initializeAnimations();

    // منع إرسال النموذج بالضغط على Enter
    setupEnterKeyHandling();


    console.log('✅ اكتملت تهيئة جميع مستمعي الأحداث بنجاح مع DOM Classes.');

    // 🔥🔥 التحديث النهائي: تطبيق إصلاحات أنظمة الدفع 🔥🔥
    // نستخدم setTimeout لضمان أن كل شيء في الصفحة قد تم تحميله بالكامل
    setTimeout(() => {
        console.log('🔧 Applying payment system fixes...');

        // استدعاء الدالة الجديدة التي تقوم بتفعيل أنظمة InstaPay و Telda المحسنة
        setupDynamicInputs();

        // فحص إضافي للتأكد من أن كل شيء يعمل بعد الإصلاحات
        setTimeout(() => {
            checkFormValidity();
            console.log('✅ All payment fixes applied successfully!');
        }, 500);

    }, 1000);
}



// إعداد اختيار طريقة الدفع
function setupPaymentSelection(paymentButtons) {
    paymentButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            paymentButtons.forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');

            const paymentType = this.dataset.type;
            const paymentValue = this.dataset.value;

            const paymentMethodInput = document.getElementById('payment_method');
            if (paymentMethodInput) {
                paymentMethodInput.value = paymentValue;
            }

            // إخفاء جميع الحقول الديناميكية
            document.querySelectorAll('.dynamic-input').forEach(input => {
                input.classList.remove('show');
                const inputField = input.querySelector('input');
                if (inputField) {
                    inputField.required = false;
                    inputField.value = '';
                }
            });

            // إخفاء رسائل الخطأ
            document.querySelectorAll('.error-message-field').forEach(error => {
                error.classList.remove('show');
            });

            // إظهار الحقل المناسب
            const targetInput = document.getElementById(paymentType + '-input');
            if (targetInput) {
                setTimeout(() => {
                    targetInput.classList.add('show');
                    const inputField = targetInput.querySelector('input');
                    if (inputField) {
                        inputField.required = true;

                        // تركيز تلقائي للهواتف
                        if (window.innerWidth <= 768) {
                            setTimeout(() => {
                                inputField.focus();
                            }, 300);
                        }
                    }
                }, 150);
            }

            // اهتزاز للهواتف
            if (navigator.vibrate) {
                navigator.vibrate(30);
            }

            // 🔥🔥 هذا هو السطر الجديد الذي يحل المشكلة 🔥🔥
            // بعد اختيار طريقة الدفع، قم بإعادة فحص النموذج بالكامل
            // لتحديث حالة زر الحفظ
            checkFormValidity();
            // 🔥 تأخير إضافي للتأكد من تحديث الحقول الديناميكية
            setTimeout(() => {
                const activeInput = document.querySelector('.dynamic-input.show input');
                if (activeInput) {
                    // تشغيل التحقق الفوري للحقل النشط
                    validatePaymentInput(activeInput);
                    checkFormValidity();
                }
            }, 300);

        });
    });
}








// ============================================================================
// ✅✅✅ النسخة النهائية والمثالية للدالة ✅✅✅
// ============================================================================
function checkFormValidity() {
    // 1. فحص المنصة (كما هو)
    validationStates.platform = !!(window.FC26PlatformModule?.getSelectedPlatform());

    // 2. فحص الواتساب (كما هو)
    const whatsappValue = document.getElementById('whatsapp')?.value;
    validationStates.whatsapp = window.whatsappManager?.validateWhatsAppNumber(whatsappValue, false) || false;

    // 3. 🔥🔥 الإصلاح النهائي: لا تقم بإعادة الفحص! 🔥🔥
    // نحن نثق الآن في أن validationStates.paymentMethod يتم تحديثها
    // بشكل صحيح من دوال التحقق الأخرى (مثل validateTeldaCardEnhanced).
    // نحن هنا فقط نقرأ القيمة النهائية.

    // الحالة النهائية
    const isFormValid = validationStates.platform &&
        validationStates.whatsapp &&
        validationStates.paymentMethod; // <-- فقط اقرأ القيمة

    // تحديث زر الحفظ
    updateSubmitButton(isFormValid);

    console.log('🔍 Form validity check:', {
        platform: validationStates.platform,
        whatsapp: validationStates.whatsapp,
        payment: validationStates.paymentMethod, // <-- اطبع القيمة الصحيحة
        overall: isFormValid
    });

    return isFormValid;
}



// تحديث زر الإرسال
function updateSubmitButton(isValid = null) {
    const submitBtn = document.getElementById('submitBtn') || document.querySelector('.submit-btn');
    if (!submitBtn) return;

    if (isValid === null) {
        isValid = validationStates.platform && validationStates.whatsapp && validationStates.paymentMethod;
    }

    submitBtn.disabled = !isValid;
    submitBtn.classList.toggle('enabled', isValid);

    // تحديث النص والأيقونة
    if (isValid) {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> إرسال البيانات';
        submitBtn.style.opacity = '1';
        submitBtn.style.transform = 'scale(1)';
    } else {
        submitBtn.innerHTML = '<i class="fas fa-lock"></i> أكمل البيانات المطلوبة';
        submitBtn.style.opacity = '0.6';
        submitBtn.style.transform = 'scale(0.98)';
    }
}

// إعداد إرسال النموذج
function setupFormSubmission(form) {
    if (!form) return;

    form.addEventListener('submit', handleFormSubmit);
}

// معالجة إرسال النموذج
async function handleFormSubmit(e) {
    e.preventDefault();

    // منع الإرسال المتكرر
    const now = Date.now();
    if (isSubmitting || (now - lastSubmitTime < 3000)) {
        showNotification('يرجى الانتظار قبل المحاولة مرة أخرى', 'error');
        return;
    }

    // التحقق النهائي من النموذج
    if (!checkFormValidity()) {
        showNotification('يرجى إكمال جميع البيانات المطلوبة', 'error');
        return;
    }

    isSubmitting = true;
    lastSubmitTime = now;

    const loading = document.getElementById('loading');
    const loadingSpinner = document.getElementById('loading-spinner');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const submitBtn = document.getElementById('submitBtn') || document.querySelector('.submit-btn');

    // إخفاء الرسائل السابقة
    if (successMessage) successMessage.classList.remove('show');
    if (errorMessage) errorMessage.classList.remove('show');

    // عرض شاشة التحميل
    if (loading) loading.classList.add('show');
    if (loadingSpinner) loadingSpinner.style.display = 'flex';

    // تحديث زر الإرسال
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الإرسال...';
    }

    // اهتزاز للهواتف
    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }

    try {
        const formData = new FormData(e.target);

        // 🔥 إصلاح بيانات الدفع قبل الإرسال
        const paymentMethod = formData.get('payment_method');
        const paymentDetailsInput = document.querySelector('.dynamic-input.show input');

        if (paymentDetailsInput) {
            let cleanedValue = paymentDetailsInput.value;

            // تنظيف رقم تيلدا من الشرطات
            if (paymentMethod === 'tilda') {
                cleanedValue = cleanedValue.replace(/[^\d]/g, '');
                formData.set('payment_details', cleanedValue);
            }
            // استخدام الرابط المستخلص لإنستا باي
            else if (paymentMethod === 'instapay') {
                const extractedLink = extractInstapayLinkEnhanced(cleanedValue);
                if (extractedLink) {
                    formData.set('payment_details', extractedLink);
                }
            }
        }


        // محاولة كلا الـ endpoints
        let response;
        try {
            response = await fetch('/update-profile', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });
        } catch (e) {
            response = await fetch('/submit_profile', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }
            });
        }

        const result = await response.json();

        // إخفاء شاشة التحميل
        if (loading) loading.classList.remove('show');
        if (loadingSpinner) loadingSpinner.style.display = 'none';

        if (response.ok && result.success) {
            // رسالة النجاح المحسنة
            let successText = '✅ تم حفظ بياناتك بنجاح!';
            if (result.data && result.data.whatsapp_info) {
                const info = result.data.whatsapp_info;
                successText += `<br><small>رقم الواتساب: ${result.data.whatsapp_number}<br>البلد: ${info.country} | الشركة: ${info.carrier}</small>`;
            }

            if (successMessage) {
                successMessage.innerHTML = successText;
                successMessage.classList.add('show');
            } else {
                showNotification('تم إرسال البيانات بنجاح! سيتم التواصل معك قريباً', 'success');
            }

            // اهتزاز نجاح
            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200]);
            }

            // إعادة تعيين النموذج بعد النجاح والتنقل لصفحة البيع
            setTimeout(() => {
                console.log('تم حفظ البيانات بنجاح:', result.data);
                // حفظ البيانات في localStorage للاستخدام في صفحة البيع
                if (result.data) {
                    localStorage.setItem('userEmail', result.data.email || '');
                    localStorage.setItem('playerName', result.data.player_name || '');
                    localStorage.setItem('telegramUsername', result.data.telegram_username || '');
                }
                // التنقل لصفحة بيع الكوينز
                window.location.href = '/sell-coins';
            }, 2000);

        } else {
            const errorText = result.message || 'حدث خطأ غير متوقع';
            if (errorMessage) {
                errorMessage.textContent = errorText;
                errorMessage.classList.add('show');
            } else {
                showNotification(errorText, 'error');
            }

            // اهتزاز خطأ
            if (navigator.vibrate) {
                navigator.vibrate([300, 100, 300, 100, 300]);
            }
        }

    } catch (error) {
        console.error('خطأ في الشبكة:', error);

        // إخفاء شاشة التحميل
        if (loading) loading.classList.remove('show');
        if (loadingSpinner) loadingSpinner.style.display = 'none';

        const errorText = 'خطأ في الاتصال، يرجى المحاولة مرة أخرى';
        if (errorMessage) {
            errorMessage.textContent = errorText;
            errorMessage.classList.add('show');
        } else {
            showNotification(errorText, 'error');
        }

        // اهتزاز خطأ شبكة
        if (navigator.vibrate) {
            navigator.vibrate([500, 200, 500]);
        }
    }

    isSubmitting = false;
    updateSubmitButton();
}

// معالجة مفتاح Enter
function setupEnterKeyHandling() {
    // منع إرسال النموذج بالضغط على Enter في الحقول
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const nextInput = getNextInput(input);
                if (nextInput) {
                    nextInput.focus();
                } else {
                    // إذا كان النموذج صحيح، قم بالإرسال
                    if (checkFormValidity()) {
                        const form = input.closest('form');
                        if (form) {
                            handleFormSubmit({ preventDefault: () => { }, target: form });
                        }
                    }
                }
            }
        });
    });
}

// الحصول على الحقل التالي
function getNextInput(currentInput) {
    const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]):not([disabled])'));
    const currentIndex = inputs.indexOf(currentInput);
    return inputs[currentIndex + 1] || null;
}

// إظهار إشعار مؤقت
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const iconClass = type === 'success' ? 'fa-check-circle' :
        type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';

    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    // تطبيق الأنماط باستخدام CSS classes
    notification.className = `notification ${type}`;
    notification.classList.add('show');

    document.body.appendChild(notification);

    // إظهار الإشعار - تم بالفعل مع إضافة الكلاس

    // إخفاء تلقائي بعد 5 ثوان
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);

    // زر الإغلاق
    notification.querySelector('.notification-close').addEventListener('click', () => {
        hideNotification(notification);
    });
}

// إخفاء الإشعار
function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// الحصول على رمز CSRF
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]') ||
        document.querySelector('input[name="csrfmiddlewaretoken"]');
    return token ? token.getAttribute('content') || token.value : '';
}

// تهيئة tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');

    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
        element.addEventListener('focus', showTooltip);
        element.addEventListener('blur', hideTooltip);
    });
}

// إظهار tooltip
function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.className = 'tooltip';

    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
    tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';

    setTimeout(() => {
        tooltip.classList.add('show');
    }, 100);

    e.target._tooltip = tooltip;
}

// إخفاء tooltip
function hideTooltip(e) {
    const tooltip = e.target._tooltip;
    if (tooltip) {
        tooltip.classList.remove('show');
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 300);
        delete e.target._tooltip;
    }
}

// تهيئة الانيميشن
function initializeAnimations() {
    // انيميشن أقسام النموذج عند التمرير
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.form-section, .form-group').forEach(section => {
        observer.observe(section);
    });

    // تمرير سلس للروابط
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// تهيئة الميزات المتقدمة
function initializeAdvancedFeatures() {
    // تهيئة tooltips والانيميشن
    initializeTooltips();
    initializeAnimations();

    // معالجة أحداث النافذة
    setupWindowEvents();

    // تحسينات اللمس للهواتف
    setupTouchOptimizations();

    // منع التكبير على iOS
    setupIOSOptimizations();

    console.log('FC 26 Profile Setup - تم تهيئة جميع الميزات المتقدمة');
}

// إعداد أحداث النافذة
function setupWindowEvents() {
    // تحسين الأداء عند تغيير حجم النافذة
    window.addEventListener('resize', debounce(function () {
        if (window.innerWidth <= 768) {
            optimizeForMobile();
        }
    }, 250));
}

// تحسينات اللمس للهواتف
function setupTouchOptimizations() {
    if ('ontouchstart' in window) {
        document.addEventListener('touchstart', function () { }, { passive: true });

        // تحسين التفاعل مع العناصر القابلة للنقر
        document.querySelectorAll('.platform-card, .payment-btn, button').forEach(element => {
            element.addEventListener('touchstart', function () {
                this.classList.add('touch-active');
            }, { passive: true });

            element.addEventListener('touchend', function () {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            }, { passive: true });
        });
    }
}

// تحسينات iOS لمنع التكبير
function setupIOSOptimizations() {
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        const viewport = document.querySelector('meta[name=viewport]');

        document.addEventListener('focusin', function (e) {
            if (e.target.matches('input, select, textarea')) {
                if (viewport) {
                    viewport.setAttribute('content',
                        'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
                    );
                }
            }
        });

        document.addEventListener('focusout', function () {
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1');
            }
        });
    }
}

// دالة تأخير التنفيذ
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================================================
// Phone Info Management - دالة مفقودة
// ============================================================================

// 🔥 إضافة هذه الدالة بعد السطر 1400
function clearPhoneInfo() {
    const phoneInfo = document.querySelector('.phone-info');
    if (phoneInfo) {
        phoneInfo.remove();
    }

    const whatsappContainer = document.querySelector('#whatsapp').closest('.form-group');
    if (whatsappContainer) {
        whatsappContainer.classList.remove('success-info');
    }
}

// إعادة تعيين حالات التحقق
function clearValidationStates() {
    validationStates = {
        whatsapp: false,
        paymentMethod: false,
        platform: false
    };

    // إزالة جميع واجهات التحقق
    document.querySelectorAll('.form-group').forEach(group => {
        group.classList.remove('valid', 'invalid');
        const errorMsg = group.querySelector('.error-message');
        const successMsg = group.querySelector('.success-message');
        if (errorMsg) errorMsg.remove();
        if (successMsg) successMsg.remove();
    });

    // إزالة معلومات الهاتف
    clearPhoneInfo();

    // تحديث زر الإرسال
    updateSubmitButton();
}

// تسجيل Service Worker للـ PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js').then(function (registration) {
            console.log('ServiceWorker تم تسجيله بنجاح');
        }, function (err) {
            console.log('فشل تسجيل ServiceWorker');
        });
    });
}

// ============================================================================
// AFTER (السطر - الكود المحدث):
// ============================================================================
// تصدير الوظائف للاستخدام الخارجي أو الاختبار
window.FC26ProfileSetup = {
    validateWhatsAppReal: validateWhatsAppReal,  // ✅ إصلاح المرجع
    validatePaymentInput: validatePaymentInput,
    showNotification: showNotification,
    clearValidationStates: clearValidationStates,
    checkFormValidity: checkFormValidity,
    updateSubmitButton: updateSubmitButton,
    whatsappManager: () => window.whatsappManager  // إضافة مرجع للمدير
};

// رسالة تأكيد التهيئة
console.log('FC 26 Profile Setup - تم تهيئة JavaScript المدمج بنجاح');



// ============================================================================
// 🔥 TelegramManager - النظام المعزول الكامل
// ============================================================================

/* ===========================
   FC26 TelegramManager (Isolated Class)
   - عزل تام لكل ما يتعلق بالتليجرام
   - صفر تداخل مع باقي الأنظمة
   =========================== */

(function () {
    'use strict';

    class TelegramManager {
        constructor() {
            // DOM references
            this.btn = document.getElementById('telegramBtn');
            this.codeResultEl = document.getElementById('telegramCodeResult');
            this.overlayEl = document.getElementById('telegramSuccessOverlay');
            this.generatedCodeEl = document.getElementById('generatedCode');

            // State management
            this.currentCode = null;
            this.botUsername = null;
            this.pollTimer = null;
            this.startedAt = 0;
            this._inited = false;

            // Bindings
            this.openAppDirect = this.openAppDirect.bind(this);
            this._onBeforeUnload = this._onBeforeUnload.bind(this);
        }

        // Helper methods
        _getPlatform() {
            try {
                if (window.FC26PlatformModule && typeof window.FC26PlatformModule.getSelectedPlatform === 'function') {
                    return window.FC26PlatformModule.getSelectedPlatform() || '';
                }
            } catch (_) { }
            const hidden = document.getElementById('platform');
            return hidden ? (hidden.value || '') : '';
        }

        _getWhatsApp() {
            const w = document.getElementById('whatsapp');
            return w ? (w.value || '').trim() : '';
        }

        _getPayment() {
            const method = document.getElementById('payment_method')?.value || '';
            const activeInput = document.querySelector('.dynamic-input.show input');
            const details = activeInput ? activeInput.value : '';
            return { method, details };
        }

        async loadBotUsername() {
            if (this.botUsername) return this.botUsername;
            try {
                const r = await fetch('/get-bot-username');
                const j = await r.json();
                this.botUsername = (j && j.bot_username) ? j.bot_username.replace(/^@/, '') : 'YourBotName_bot';
            } catch (e) {
                console.error('❌ Failed to load bot username:', e);
                this.botUsername = 'YourBotName_bot';
            }
            return this.botUsername;
        }

        init() {
            if (this._inited) return;
            this._inited = true;

            // Preload bot username
            this.loadBotUsername();

            // Bind button click
            if (this.btn && !this.btn.dataset.tmBound) {
                this.btn.addEventListener('click', (e) => {
                    try { e.preventDefault(); } catch (_) { }
                    this.generateCode();
                }, { passive: false });
                this.btn.dataset.tmBound = '1';
                console.log('✅ TelegramManager button bound successfully');
            }

            // Cleanup timers
            window.addEventListener('beforeunload', this._onBeforeUnload, { passive: false });
            console.log('✅ TelegramManager initialized');
        }

        _setBtnLoading(loading) {
            if (!this.btn) return;
            if (loading) {
                this.btn.classList.add('generating');
                this.btn.disabled = true;
                this.btn.innerHTML = `
                    <div class="telegram-btn-content">
                        <i class="fas fa-spinner fa-spin telegram-icon"></i>
                        <div class="telegram-text">
                            <span class="telegram-title">⚡ جاري إنشاء الرابط</span>
                            <span class="telegram-subtitle">انتظر لحظة...</span>
                        </div>
                    </div>
                `;
            } else {
                this.btn.classList.remove('generating');
                this.btn.disabled = false;
            }
        }

        _setBtnOpenMode() {
            if (!this.btn) return;
            this.btn.innerHTML = `
                <div class="telegram-btn-content">
                    <i class="fab fa-telegram telegram-icon"></i>
                    <div class="telegram-text">
                        <span class="telegram-title">📱 فتح التليجرام والربط</span>
                        <span class="telegram-subtitle">اضغط للربط التلقائي</span>
                    </div>
                </div>
            `;
            this.btn.onclick = this.openAppDirect;
            this.btn.disabled = false;
        }

        _renderCodeResult(code) {
            if (!this.codeResultEl) return;
            this.codeResultEl.style.display = 'block';
            this.codeResultEl.innerHTML = `
                <div class="code-container">
                    <div class="code-header">
                        <i class="fas fa-rocket"></i>
                        <span>جاهز للربط التلقائي</span>
                    </div>
                    <div class="generated-code">${code}</div>
                    <div class="telegram-actions">
                        <button type="button" class="telegram-open-btn-big" id="secondaryTelegramBtn">
                            <i class="fab fa-telegram"></i>
                            🚀 فتح التليجرام والربط الآن
                        </button>
                    </div>
                    <div class="telegram-instructions">
                        <div class="single-step">⚡ اضغط الزر وسيتم الربط التلقائي!</div>
                    </div>
                </div>
            `;
            const sec = document.getElementById('secondaryTelegramBtn');
            if (sec) sec.addEventListener('click', this.openAppDirect, { passive: false });

            setTimeout(() => {
                this.codeResultEl.classList.add('show');
                this.codeResultEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }

        async generateCode() {
            const platform = this._getPlatform();
            const whatsappNumber = this._getWhatsApp();
            if (!platform || !whatsappNumber) {
                if (typeof showNotification === 'function') {
                    showNotification('يرجى إكمال الملف الشخصي أولاً (المنصة ورقم الواتساب)', 'error');
                }
                return;
            }

            const p = this._getPayment();
            const payload = {
                platform,
                whatsapp_number: whatsappNumber,
                payment_method: p.method || '',
                payment_details: p.details || ''
            };

            try {
                this._setBtnLoading(true);
                const res = await fetch('/generate-telegram-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                this._setBtnLoading(false);

                if (!data || !data.success) {
                    if (typeof showNotification === 'function') {
                        showNotification(data.message || 'خطأ في إنشاء الكود', 'error');
                    }
                    this.resetButton();
                    return;
                }

                this.currentCode = data.code;
                this.startedAt = Date.now();
                this._setBtnOpenMode();
                this._renderCodeResult(data.code);

                if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
                if (typeof showNotification === 'function') {
                    showNotification(`✅ جاهز للربط! الكود: ${data.code}`, 'success');
                }

                this.startAutoLinking(this.currentCode);

            } catch (e) {
                console.error('Telegram generate error:', e);
                this._setBtnLoading(false);
                if (typeof showNotification === 'function') {
                    showNotification('خطأ في الاتصال، يرجى المحاولة مرة أخرى', 'error');
                }
                this.resetButton();
            }
        }

        async openAppDirect() {
            const code = this.currentCode || (this.generatedCodeEl && this.generatedCodeEl.textContent) || '';
            if (!code) {
                if (typeof showNotification === 'function') {
                    showNotification('❌ لا يوجد كود للربط', 'error');
                }
                return;
            }

            if (!this.botUsername) {
                await this.loadBotUsername();
            }

            const allButtons = document.querySelectorAll('button');
            const codeBox = this.codeResultEl;
            if (codeBox) {
                codeBox.style.opacity = '0.6';
                codeBox.style.pointerEvents = 'none';
            }
            allButtons.forEach(b => { try { b.disabled = true; b.style.opacity = '0.6'; } catch (_) { } });

            const appUrl = `tg://resolve?domain=${this.botUsername}&start=${encodeURIComponent(code)}`;
            const webUrl = `https://t.me/${this.botUsername}?start=${encodeURIComponent(code)}`;

            try {
                if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
                    const a = document.createElement('a');
                    a.href = appUrl;
                    a.style.display = 'none';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    setTimeout(() => window.open(webUrl, '_blank'), 800);
                } else {
                    window.open(webUrl, '_blank');
                }
            } catch (_) {
                window.open(webUrl, '_blank');
            }

            if (typeof showNotification === 'function') {
                showNotification('🚀 فتح التليجرام...', 'info');
                setTimeout(() => showNotification('⚡ جاري الربط التلقائي...', 'info'), 1500);
                setTimeout(() => showNotification('🔗 انتظار تأكيد الربط...', 'info'), 3000);
            }

            if (!this.pollTimer) {
                this.startAutoLinking(code);
            }
        }

        startAutoLinking(code) {
            let attempt = 0;
            const maxAttempts = 45;
            if (this.pollTimer) clearInterval(this.pollTimer);

            this.pollTimer = setInterval(async () => {
                attempt++;
                try {
                    const r = await fetch(`/check-telegram-status/${encodeURIComponent(code)}`, {
                        method: 'GET',
                        headers: { 'X-Requested-With': 'XMLHttpRequest', 'Cache-Control': 'no-cache' }
                    });
                    if (r.ok) {
                        const j = await r.json();
                        if (j.success && j.linked) {
                            clearInterval(this.pollTimer);
                            this.pollTimer = null;
                            this.showSuccess();
                            return;
                        }
                    }
                } catch (e) {
                    console.warn('AutoLink poll error:', e);
                }

                if (attempt === 5 && typeof showNotification === 'function') {
                    showNotification('📡 البحث عن الربط...', 'info');
                }
                if (attempt === 10 && typeof showNotification === 'function') {
                    showNotification('🔍 فحص حالة الاتصال...', 'info');
                }
                if (attempt === 20 && typeof showNotification === 'function') {
                    showNotification('⏳ يرجى التأكد من إرسال الكود للبوت', 'info');
                }
                if (attempt === 30 && typeof showNotification === 'function') {
                    showNotification('⚠️ تأكد من فتح التليجرام وإرسال الكود', 'info');
                }

                if (attempt >= maxAttempts) {
                    clearInterval(this.pollTimer);
                    this.pollTimer = null;
                    this.showTimeoutError();
                }
            }, 3000);
        }

        async checkAdvancedStatus(code) {
            try {
                const r = await fetch(`/check-telegram-status/${encodeURIComponent(code)}`, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'Cache-Control': 'no-cache' }
                });
                const j = await r.json();
                return j;
            } catch (e) {
                return { success: false, linked: false, error: String(e) };
            }
        }

        showSuccess() {
            const loading = document.getElementById('loading');
            const container = document.querySelector('.container');
            if (loading) loading.classList.remove('show');
            if (container) {
                container.style.opacity = '0';
                container.style.transform = 'scale(0.95)';
            }

            setTimeout(() => {
                if (this.overlayEl) {
                    this.overlayEl.classList.add('show');
                    document.body.style.overflow = 'hidden';
                    const sc = this.overlayEl.querySelector('.success-container');
                    if (sc) {
                        sc.innerHTML = `
                            <div class="success-animation">
                                <i class="fas fa-check-circle success-mega-icon"></i>
                            </div>
                            <h2 class="success-title">🎉 تم ربط حسابك بنجاح!</h2>
                            <p class="success-subtitle">
                                ✅ تم حفظ ملفك الشخصي بأمان<br>
                                💾 تم حفظ جميع معلوماتك<br>
                                🚀 مرحباً بك في عالم FC 26!
                            </p>
                            <div class="success-actions">
                                <button type="button" class="success-btn" onclick="closeSuccessOverlay()">
                                    <i class="fas fa-home"></i>
                                    العودة للرئيسية
                                </button>
                            </div>
                        `;
                    }
                    if (navigator.vibrate) navigator.vibrate([300, 100, 300, 100, 500]);
                }
            }, 800);

            if (typeof showNotification === 'function') {
                showNotification('🎉 تم الربط بنجاح!', 'success');
                setTimeout(() => showNotification('💾 تم حفظ ملفك الشخصي!', 'success'), 1200);
                setTimeout(() => showNotification('✅ تم حفظ معلوماتك بأمان!', 'success'), 2400);
                setTimeout(() => showNotification('🏆 مرحباً بك في FC 26!', 'success'), 3600);
            }

            try {
                if (typeof playSuccessSound === 'function') playSuccessSound();
            } catch (_) { }
        }

        showTimeoutError() {
            if (typeof showNotification === 'function') {
                showNotification('⏰ انتهت مهلة الربط التلقائي - يرجى المحاولة مرة أخرى', 'error');
            }

            const allButtons = document.querySelectorAll('button');
            const codeBox = this.codeResultEl;
            if (codeBox) {
                codeBox.style.opacity = '1';
                codeBox.style.pointerEvents = 'auto';
            }
            allButtons.forEach(b => {
                try {
                    b.disabled = false;
                    b.style.opacity = '1';
                } catch (_) { }
            });
            this.resetButton();
        }

        resetButton() {
            if (!this.btn) return;
            this.btn.innerHTML = `
                <div class="telegram-btn-content">
                    <i class="fab fa-telegram telegram-icon"></i>
                    <div class="telegram-text">
                        <span class="telegram-title">📱 ربط مع التليجرام</span>
                        <span class="telegram-subtitle">احصل على كود فوري وادخل للبوت</span>
                    </div>
                </div>
            `;
            this.btn.onclick = () => this.generateCode();
            this.btn.disabled = false;
            this.btn.classList.remove('generating');
        }

        closeSuccessOverlay() {
            if (this.overlayEl) {
                this.overlayEl.classList.remove('show');
                document.body.style.overflow = '';
                const container = document.querySelector('.container');
                if (container) {
                    container.style.opacity = '1';
                    container.style.transform = 'scale(1)';
                }
            }
            // التنقل لصفحة بيع الكوينز بدلاً من إعادة التحميل
            setTimeout(() => {
                window.location.href = '/sell-coins';
            }, 500);
        }

        cleanup() {
            if (this.pollTimer) {
                clearInterval(this.pollTimer);
                this.pollTimer = null;
            }
        }

        _onBeforeUnload() {
            this.cleanup();
        }
    }

    // Instance + Auto-Boot
    window.telegramManager = window.telegramManager || new TelegramManager();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => window.telegramManager.init());
    } else {
        window.telegramManager.init();
    }

    // Compatibility Bridge (الجسر للحفاظ على الدوال القديمة)
    window.loadBotUsername = function () {
        return window.telegramManager.loadBotUsername();
    };
    window.generateTelegramCode = function () {
        return window.telegramManager.generateCode();
    };
    window.openTelegramAppDirect = function () {
        return window.telegramManager.openAppDirect();
    };
    window.startAutoTelegramLinking = function (code) {
        return window.telegramManager.startAutoLinking(code);
    };
    window.showUltimateSuccess = function () {
        return window.telegramManager.showSuccess();
    };
    window.showTimeoutError = function () {
        return window.telegramManager.showTimeoutError();
    };
    window.resetTelegramButton = function () {
        return window.telegramManager.resetButton();
    };
    window.closeSuccessOverlay = function () {
        return window.telegramManager.closeSuccessOverlay();
    };
    window.checkAdvancedTelegramStatus = function (code) {
        return window.telegramManager.checkAdvancedStatus(code);
    };

})();


// ============================================================================
// 🔥 TelegramManager - 🔥 الناهية 🔥 المعزول 🔥  الكامل 🔥🔥🔥
// ============================================================================




// تشغيل صوت النجاح المطور
function playSuccessSound() {
    try {
        // نغمة نجاح قصيرة
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
        oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
        oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);

    } catch (e) {
        console.log('Sound not supported');
    }
}





// ============================================================================
// 🏰 EmailManager - النظام المعزول بالكامل (IIFE + Class Pattern)
// ============================================================================

(function() {
    'use strict';

    /**
     * 🏰 EmailManager Class - نظام إدارة البريد الإلكتروني المعزول تماماً
     * 
     * ✅ عزل مطلق: كل شيء داخل IIFE
     * ✅ إدارة حالة داخلية: الكلاس هو المصدر الوحيد للحقيقة
     * ✅ صفر تبعيات خارجية: مكتفي ذاتياً 100%
     * ✅ واجهة برمجية نظيفة: Clean API للتواصل مع الخارج
     * ✅ حماية مطلقة: لا يتأثر بأي تغييرات خارجية
     */
    class EmailManager {
        constructor() {
            // 🔒 الحالة الداخلية المحمية
            this.state = {
                emails: [],
                maxEmails: 6,
                initialized: false,
                isProcessing: false
            };

            // 🎯 مراجع DOM المحمية
            this.elements = {
                container: null,
                newEmailInput: null,
                emailAddressesInput: null,
                addEmailButton: null
            };

            // 🛡️ إعدادات الحماية
            this.config = {
                maxEmails: 6,
                notificationDuration: 5000,
                animationDelay: 400,
                validEmailRegex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                vibratePatterns: {
                    success: [50, 50, 100],
                    error: [100, 50, 100, 50, 100],
                    delete: [30, 30, 30]
                }
            };

            // 🔗 ربط السياق للـ methods
            this.addNewEmail = this.addNewEmail.bind(this);
            this.removeEmail = this.removeEmail.bind(this);
            this.handleKeyPress = this.handleKeyPress.bind(this);
            this.handleInputChange = this.handleInputChange.bind(this);
        }

        /**
         * 🚀 تهيئة النظام
         */
        init() {
            if (this.state.initialized) {
                console.warn('⚠️ EmailManager: النظام مُهيأ بالفعل');
                return false;
            }

            try {
                // 🔍 البحث عن العناصر المطلوبة
                this.elements.container = document.getElementById('emailsContainer');
                this.elements.newEmailInput = document.getElementById('newEmailInput');
                this.elements.emailAddressesInput = document.getElementById('emailAddressesInput');
                this.elements.addEmailButton = document.querySelector('.add-email-btn');

                // 🚫 التحقق من وجود العناصر الأساسية
                if (!this.validateElements()) {
                    console.error('❌ EmailManager: عناصر DOM المطلوبة غير موجودة');
                    return false;
                }

                // 🔗 ربط الأحداث
                this.bindEvents();

                // 🎨 تهيئة الواجهة
                this.initializeUI();

                // ✅ تحديث الحالة
                this.state.initialized = true;
                console.log('✅ EmailManager: تم التهيئة بنجاح');
                
                return true;

            } catch (error) {
                console.error('❌ EmailManager: خطأ في التهيئة:', error);
                return false;
            }
        }

        /**
         * 🔍 التحقق من وجود العناصر المطلوبة
         */
        validateElements() {
            return !!(this.elements.container && 
                     this.elements.newEmailInput && 
                     this.elements.addEmailButton);
        }

        /**
         * 🔗 ربط الأحداث
         */
        bindEvents() {
            // زر الإضافة
            if (this.elements.addEmailButton) {
                this.elements.addEmailButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.addNewEmail();
                });
            }

            // حقل الإدخال
            if (this.elements.newEmailInput) {
                // Enter key
                this.elements.newEmailInput.addEventListener('keypress', this.handleKeyPress);
                
                // تحديث حالة الزر عند الكتابة
                this.elements.newEmailInput.addEventListener('input', this.handleInputChange);
            }
        }

        /**
         * ⌨️ معالجة ضغط المفاتيح
         */
        handleKeyPress(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.addNewEmail();
            }
        }

        /**
         * 📝 معالجة تغيير المدخلات
         */
        handleInputChange() {
            this.updateAddButton();
        }

        /**
         * 🎨 تهيئة الواجهة
         */
        initializeUI() {
            // إضافة رسالة فارغة إذا لزم
            if (this.state.emails.length === 0) {
                this.showEmptyMessage();
            }

            // تحديث حالة الزر
            this.updateAddButton();

            // تحديث الحقل المخفي
            this.updateHiddenInput();
        }

        /**
         * ✅ التحقق من صحة البريد الإلكتروني
         */
        isValidEmail(email) {
            if (!email || typeof email !== 'string') {
                return false;
            }

            const cleanEmail = email.trim().toLowerCase();
            
            // التحقق الأساسي
            if (!this.config.validEmailRegex.test(cleanEmail)) {
                return false;
            }

            // فحوص إضافية
            if (cleanEmail.length > 254) return false;
            if (cleanEmail.includes('..')) return false;
            if (cleanEmail.startsWith('.') || cleanEmail.endsWith('.')) return false;
            
            // التحقق من الجزء المحلي والنطاق
            const [localPart, domain] = cleanEmail.split('@');
            if (localPart.length > 64) return false;
            if (domain.length > 253) return false;

            return true;
        }

        /**
         * 📧 إضافة بريد إلكتروني جديد
         */
        addNewEmail() {
            // منع المعالجة المتزامنة
            if (this.state.isProcessing) return false;
            
            this.state.isProcessing = true;

            const input = this.elements.newEmailInput;
            if (!input) {
                this.state.isProcessing = false;
                return false;
            }

            const email = input.value.trim();

            // التحققات
            if (!email) {
                this.showNotification('يرجى إدخال البريد الإلكتروني', 'error');
                input.focus();
                this.state.isProcessing = false;
                return false;
            }

            if (!this.isValidEmail(email)) {
                this.showNotification('البريد الإلكتروني غير صحيح', 'error');
                input.focus();
                this.state.isProcessing = false;
                return false;
            }

            const normalizedEmail = email.toLowerCase();

            if (this.state.emails.includes(normalizedEmail)) {
                this.showNotification('هذا البريد مضاف بالفعل', 'error');
                input.focus();
                this.state.isProcessing = false;
                return false;
            }

            if (this.state.emails.length >= this.config.maxEmails) {
                this.showNotification(`لا يمكن إضافة أكثر من ${this.config.maxEmails} عناوين بريد`, 'error');
                this.state.isProcessing = false;
                return false;
            }

            // ✅ إضافة البريد
            this.state.emails.push(normalizedEmail);
            
            // إزالة رسالة الفراغ
            this.removeEmptyMessage();
            
            // إنشاء العنصر
            this.createEmailElement(normalizedEmail, this.state.emails.length);
            
            // تنظيف وتحديث
            input.value = '';
            input.focus();
            this.updateHiddenInput();
            this.updateAddButton();
            
            // إشعار النجاح
            this.showNotification(`تم إضافة البريد رقم ${this.state.emails.length}`, 'success');
            
            // اهتزاز
            this.vibrate('success');
            
            this.state.isProcessing = false;
            return true;
        }

        /**
         * 🏗️ إنشاء عنصر البريد الإلكتروني
         */
        createEmailElement(email, number) {
            if (!this.elements.container) return;

            const emailDiv = document.createElement('div');
            emailDiv.className = `email-item email-${number}`;
            emailDiv.setAttribute('data-email', email);
            emailDiv.style.opacity = '0';
            emailDiv.style.transform = 'translateY(20px)';

            // محتوى آمن
            const safeEmail = this.escapeHtml(email);
            
            emailDiv.innerHTML = `
                <div class="email-number">${number}</div>
                <div class="email-text">${safeEmail}</div>
                <button type="button" class="delete-email-btn" title="حذف البريد">
                    <i class="fas fa-times"></i>
                </button>
            `;

            // ربط حدث الحذف
            const deleteBtn = emailDiv.querySelector('.delete-email-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.removeEmail(email);
                });
            }

            // إضافة للحاوية
            this.elements.container.appendChild(emailDiv);

            // انيميشن الظهور
            requestAnimationFrame(() => {
                emailDiv.style.transition = 'all 0.3s ease';
                emailDiv.style.opacity = '1';
                emailDiv.style.transform = 'translateY(0)';
            });
        }

        /**
         * 🗑️ حذف بريد إلكتروني
         */
        removeEmail(email) {
            if (this.state.isProcessing) return false;
            
            this.state.isProcessing = true;

            const element = this.elements.container?.querySelector(`[data-email="${email}"]`);
            if (!element) {
                this.state.isProcessing = false;
                return false;
            }

            // انيميشن الحذف
            element.style.transition = 'all 0.3s ease';
            element.style.opacity = '0';
            element.style.transform = 'translateX(-100%)';

            setTimeout(() => {
                // إزالة من الحالة
                const index = this.state.emails.indexOf(email);
                if (index > -1) {
                    this.state.emails.splice(index, 1);
                }

                // إزالة العنصر
                element.remove();

                // إعادة الترقيم
                this.renumberEmails();

                // التحديثات
                this.updateHiddenInput();
                this.updateAddButton();

                // رسالة فارغة إذا لزم
                if (this.state.emails.length === 0) {
                    this.showEmptyMessage();
                }

                // إشعار
                this.showNotification('تم حذف البريد الإلكتروني', 'success');
                
                // اهتزاز
                this.vibrate('delete');
                
                this.state.isProcessing = false;

            }, this.config.animationDelay);

            return true;
        }

        /**
         * 🔢 إعادة ترقيم الإيميلات
         */
        renumberEmails() {
            const items = this.elements.container?.querySelectorAll('.email-item');
            if (!items) return;

            items.forEach((item, index) => {
                const newNumber = index + 1;
                const numberEl = item.querySelector('.email-number');
                
                if (numberEl) {
                    numberEl.textContent = newNumber;
                }
                
                item.className = `email-item email-${newNumber}`;
            });
        }

        /**
         * 📝 عرض رسالة الفراغ
         */
        showEmptyMessage() {
            if (!this.elements.container) return;
            
            // تحقق من عدم وجود رسالة مسبقاً
            if (this.elements.container.querySelector('.emails-empty')) return;

            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'emails-empty';
            emptyDiv.innerHTML = '<i class="fas fa-envelope-open"></i> لم تتم إضافة أي عناوين بريد إلكتروني';
            this.elements.container.appendChild(emptyDiv);
        }

        /**
         * 🗑️ إزالة رسالة الفراغ
         */
        removeEmptyMessage() {
            const emptyMsg = this.elements.container?.querySelector('.emails-empty');
            if (emptyMsg) {
                emptyMsg.remove();
            }
        }

        /**
         * 💾 تحديث الحقل المخفي
         */
        updateHiddenInput() {
            if (this.elements.emailAddressesInput) {
                this.elements.emailAddressesInput.value = JSON.stringify(this.state.emails);
            }
        }

        /**
         * 🔘 تحديث زر الإضافة
         */
        updateAddButton() {
            const button = this.elements.addEmailButton;
            if (!button) return;

            const inputValue = this.elements.newEmailInput?.value.trim() || '';
            const hasInput = inputValue.length > 0;
            const hasReachedLimit = this.state.emails.length >= this.config.maxEmails;

            if (hasReachedLimit) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-check"></i> تم الوصول للحد الأقصى';
            } else if (hasInput) {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-plus"></i> إضافة بريد إلكتروني';
            } else {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-plus"></i> إضافة بريد إلكتروني';
            }
        }

        /**
         * 🔔 عرض الإشعارات
         */
        showNotification(message, type = 'info') {
            // إنشاء عنصر الإشعار
            const notification = document.createElement('div');
            notification.className = `email-notification ${type}`;
            
            const icons = {
                success: 'fa-check-circle',
                error: 'fa-exclamation-circle',
                info: 'fa-info-circle'
            };

            const colors = {
                success: '#10B981',
                error: '#DC2626',
                info: '#3B82F6'
            };

            notification.innerHTML = `
                <div class="notification-content">
                    <i class="fas ${icons[type] || icons.info}"></i>
                    <span>${this.escapeHtml(message)}</span>
                </div>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
            `;

            // استخدام CSS classes بدلاً من inline styles
            notification.className = `email-notification ${type}`;

            document.body.appendChild(notification);

            // إظهار
            requestAnimationFrame(() => {
                notification.classList.add('show');
            });

            // زر الإغلاق
            const closeBtn = notification.querySelector('.notification-close');
            if (closeBtn) {
                closeBtn.className = 'notification-close';
                
                closeBtn.addEventListener('click', () => {
                    this.hideNotification(notification);
                });
            }

            // إخفاء تلقائي
            setTimeout(() => {
                this.hideNotification(notification);
            }, this.config.notificationDuration);
        }

        /**
         * 🙈 إخفاء الإشعار
         */
        hideNotification(notification) {
            if (!notification) return;
            
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }

        /**
         * 📱 الاهتزاز
         */
        vibrate(type = 'default') {
            if (!navigator.vibrate) return;
            
            const pattern = this.config.vibratePatterns[type] || [50];
            
            try {
                navigator.vibrate(pattern);
            } catch (error) {
                // تجاهل الأخطاء
            }
        }

        /**
         * 🛡️ حماية من XSS
         */
        escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return String(text).replace(/[&<>"']/g, (m) => map[m]);
        }

        /**
         * 📊 الحصول على الحالة
         */
        getState() {
            return {
                emails: [...this.state.emails],
                count: this.state.emails.length,
                maxEmails: this.config.maxEmails,
                hasReachedLimit: this.state.emails.length >= this.config.maxEmails,
                isInitialized: this.state.initialized
            };
        }

        /**
         * 🔄 إعادة تعيين
         */
        reset() {
            this.state.emails = [];
            this.updateHiddenInput();
            this.updateAddButton();
            
            // مسح العناصر
            if (this.elements.container) {
                this.elements.container.innerHTML = '';
                this.showEmptyMessage();
            }
            
            this.showNotification('تم مسح جميع عناوين البريد', 'info');
        }

        /**
         * 📥 تحديد إيميلات من الخارج
         */
        setEmails(emails) {
            if (!Array.isArray(emails)) {
                console.error('❌ EmailManager: المدخل يجب أن يكون مصفوفة');
                return false;
            }

            // مسح الحالي
            this.reset();

            // إضافة الجديد
            emails.forEach(email => {
                if (this.isValidEmail(email) && this.state.emails.length < this.config.maxEmails) {
                    const normalizedEmail = email.toLowerCase();
                    if (!this.state.emails.includes(normalizedEmail)) {
                        this.state.emails.push(normalizedEmail);
                        this.createEmailElement(normalizedEmail, this.state.emails.length);
                    }
                }
            });

            // التحديثات
            this.updateHiddenInput();
            this.updateAddButton();

            if (this.state.emails.length > 0) {
                this.removeEmptyMessage();
            }

            return true;
        }

        /**
         * 🔧 تحديث الإعدادات
         */
        updateConfig(newConfig) {
            if (typeof newConfig === 'object') {
                Object.assign(this.config, newConfig);
                this.updateAddButton();
            }
        }

        /**
         * 🧹 تنظيف الموارد
         */
        destroy() {
            // إزالة الأحداث
            if (this.elements.addEmailButton) {
                this.elements.addEmailButton.removeEventListener('click', this.addNewEmail);
            }
            
            if (this.elements.newEmailInput) {
                this.elements.newEmailInput.removeEventListener('keypress', this.handleKeyPress);
                this.elements.newEmailInput.removeEventListener('input', this.handleInputChange);
            }

            // مسح المراجع
            this.elements = {};
            this.state.emails = [];
            this.state.initialized = false;
            
            console.log('🧹 EmailManager: تم التنظيف');
        }
    }

    // ============================================================================
    // 🌐 التفعيل والتصدير
    // ============================================================================

    /**
     * 🎯 إنشاء المثيل الوحيد
     */
    const emailManager = new EmailManager();

    /**
     * 🚀 التهيئة التلقائية عند تحميل DOM
     */
    function autoInit() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => emailManager.init(), 100);
            });
        } else {
            setTimeout(() => emailManager.init(), 100);
        }
    }

    // بدء التهيئة التلقائية
    autoInit();

    // ============================================================================
    // 🌐 الواجهة البرمجية العامة (Public API)
    // ============================================================================

    /**
     * 🔒 تصدير محدود وآمن للنطاق العالمي
     */
    if (typeof window !== 'undefined') {
        window.EmailManagerAPI = {
            // الوظائف الأساسية
            init: () => emailManager.init(),
            addEmail: () => emailManager.addNewEmail(),
            removeEmail: (email) => emailManager.removeEmail(email),
            reset: () => emailManager.reset(),
            
            // القراءة
            getState: () => emailManager.getState(),
            getEmails: () => [...emailManager.state.emails],
            getCount: () => emailManager.state.emails.length,
            isInitialized: () => emailManager.state.initialized,
            
            // التحديث
            setEmails: (emails) => emailManager.setEmails(emails),
            updateConfig: (config) => emailManager.updateConfig(config),
            
            // معلومات النظام
            version: '2.0.0 - Fully Isolated',
            
            // للتطوير فقط (يمكن حذفها في الإنتاج)
            debug: {
                manager: emailManager,
                checkElements: () => ({
                    container: !!emailManager.elements.container,
                    input: !!emailManager.elements.newEmailInput,
                    button: !!emailManager.elements.addEmailButton
                })
            }
        };

        console.log('🌐 EmailManagerAPI: متاح عالمياً مع عزل كامل');
    }

})(); // نهاية IIFE - العزل المطلق

// ============================================================================
// 🔄 جسر التوافقية (Compatibility Bridge)
// ============================================================================

/**
 * دوال التوافق مع الكود القديم
 * يمكن حذفها بعد تحديث كل الأماكن التي تستخدمها
 */

// دالة addNewEmail القديمة
if (typeof addNewEmail === 'undefined') {
    window.addNewEmail = function() {
        if (window.EmailManagerAPI) {
            return window.EmailManagerAPI.addEmail();
        }
        console.warn('⚠️ EmailManager غير متاح');
        return false;
    };
}

// دالة removeEmail القديمة  
if (typeof removeEmail === 'undefined') {
    window.removeEmail = function(email) {
        if (window.EmailManagerAPI) {
            return window.EmailManagerAPI.removeEmail(email);
        }
        console.warn('⚠️ EmailManager غير متاح');
        return false;
    };
}

console.log('🏰 EmailManager: النظام المعزول جاهز للاستخدام!');



// ============================================================================
// 🏰🏰🏰 EmailManager - النظام 🏰 المعزول بالكامل 🏰 النهاي 🏰ة 🏰 (IIFE + Class Pattern)
// ============================================================================



// ═══════════════════════════════════════════════════════════════
// 🔗 نظام استخلاص روابط InstaPay الذكي - إضافة جديدة
// ═══════════════════════════════════════════════════════════════

// التحقق والاستخلاص الفوري لروابط InstaPay
function validateInstapayInput(input) {
    const text = input.value.trim();
    const container = input.closest('.form-group');

    // إزالة المعاينة السابقة
    const existingPreview = container.querySelector('.instapay-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    if (!text) {
        updateValidationUI(input, true, '');
        return true;
    }

    // محاولة استخلاص الرابط
    const extractedLink = extractInstapayLink(text);

    if (extractedLink) {
        // إنشاء معاينة الرابط
        createInstapayPreview(container, extractedLink, text);
        updateValidationUI(input, true, '✓ تم استخلاص رابط InstaPay');
        return true;
    } else {
        updateValidationUI(input, false, 'لم يتم العثور على رابط InstaPay صحيح');
        return false;
    }
}

// استخلاص رابط InstaPay من النص (JavaScript)
function extractInstapayLink(text) {
    const patterns = [
        /https?:\/\/(?:www\.)?ipn\.eg\/S\/[^\/\s]+\/instapay\/[A-Za-z0-9]+/gi,
        /https?:\/\/(?:www\.)?instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?app\.instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?instapay\.app\/[^\s<>"{}|\\^`\[\]]+/gi,
        /https?:\/\/(?:www\.)?ipn\.eg\/[^\s<>"{}|\\^`\[\]]+/gi,
    ];

    for (const pattern of patterns) {
        const matches = text.match(pattern);
        if (matches && matches.length > 0) {
            // تنظيف الرابط من العلامات في النهاية
            let link = matches[0].replace(/[.,;!?]+$/, '');
            if (isValidInstapayUrl(link)) {
                return link;
            }
        }
    }

    return null;
}

// التحقق من صحة رابط InstaPay (JavaScript)
function isValidInstapayUrl(url) {
    if (!url || (!url.startsWith('http://') && !url.startsWith('https://'))) {
        return false;
    }

    const validDomains = ['ipn.eg', 'instapay.com.eg', 'app.instapay.com.eg', 'instapay.app'];
    const lowerUrl = url.toLowerCase();

    return validDomains.some(domain => lowerUrl.includes(domain)) && url.length >= 20;
}

// إنشاء معاينة الرابط المستخلص
function createInstapayPreview(container, extractedLink, originalText) {
    const previewDiv = document.createElement('div');
    previewDiv.className = 'instapay-preview';

    previewDiv.innerHTML = `
        <div class="preview-header">
            <i class="fas fa-link"></i>
            <span>تم استخلاص رابط InstaPay</span>
        </div>
        <div class="extracted-link">
            <div class="link-label">الرابط المستخلص:</div>
            <div class="link-url">${extractedLink}</div>
        </div>
        <div class="preview-actions">
            <button type="button" class="test-link-btn" onclick="testInstapayLink('${extractedLink}')">
                <i class="fas fa-external-link-alt"></i>
                اختبار الرابط
            </button>
            <button type="button" class="copy-link-btn" onclick="copyInstapayLink('${extractedLink}')">
                <i class="fas fa-copy"></i>
                نسخ الرابط
            </button>
        </div>
    `;

    container.appendChild(previewDiv);

    // انيميشن الظهور
    setTimeout(() => {
        previewDiv.classList.add('show');
    }, 100);
}

// اختبار رابط InstaPay
function testInstapayLink(url) {
    window.open(url, '_blank');
    showNotification('تم فتح الرابط في تبويب جديد', 'info');
}

// نسخ رابط InstaPay
async function copyInstapayLink(url) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(url);
        } else {
            // طريقة احتياطية
            const textArea = document.createElement('textarea');
            textArea.value = url;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }

        showNotification('تم نسخ الرابط بنجاح!', 'success');

        if (navigator.vibrate) {
            navigator.vibrate([50, 50, 50]);
        }

    } catch (error) {
        showNotification('فشل في نسخ الرابط', 'error');
    }
}





// ============================================================================
// 🔥 إصلاح نظام التحقق من الواتساب
// ============================================================================

// إصلاح التحقق الفعلي من الواتساب
async function performWhatsAppValidation(phoneNumber) {
    if (!phoneNumber || phoneNumber.length < 10) {
        return { is_valid: false, error: 'رقم قصير جداً' };
    }

    try {
        const response = await fetch('/validate-whatsapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                phone: phoneNumber,
                phone_number: phoneNumber
            })
        });

        if (!response.ok) {
            throw new Error('Server error');
        }

        const result = await response.json();
        return result;

    } catch (error) {
        console.error('WhatsApp validation error:', error);

        // Fallback للتحقق المحلي
        const cleanNumber = phoneNumber.replace(/[^\d]/g, '');
        const isValid = /^01[0125]\d{8}$/.test(cleanNumber);

        return {
            is_valid: isValid,
            error: isValid ? null : 'رقم غير صحيح',
            fallback: true
        };
    }
}

// تحديث معالج الواتساب
function enhanceWhatsAppValidation() {
    const whatsappInput = document.getElementById('whatsapp');
    if (!whatsappInput) return;

    let validationTimer = null;

    whatsappInput.addEventListener('input', function (e) {
        const value = e.target.value.trim();

        // إلغاء التحقق السابق
        if (validationTimer) {
            clearTimeout(validationTimer);
        }

        // تحقق محلي سريع
        const cleanNumber = value.replace(/[^\d+]/g, '');
        const quickValid = cleanNumber.length >= 10;

        if (!quickValid) {
            validationStates.whatsapp = false;
            checkFormValidity();
            return;
        }

        // إضافة مؤشر تحميل
        e.target.classList.add('validating');

        // تحقق من الخادم بعد توقف الكتابة
        validationTimer = setTimeout(async () => {
            const result = await performWhatsAppValidation(value);

            e.target.classList.remove('validating');

            if (result.is_valid) {
                e.target.classList.add('valid');
                e.target.classList.remove('invalid');
                validationStates.whatsapp = true;

                // عرض رسالة نجاح
                showWhatsAppSuccess(e.target, result);
            } else {
                e.target.classList.add('invalid');
                e.target.classList.remove('valid');
                validationStates.whatsapp = false;

                // عرض رسالة خطأ
                showWhatsAppError(e.target, result.error);
            }

            checkFormValidity();

        }, 800); // انتظار 800ms
    });
}

// عرض نجاح الواتساب
function showWhatsAppSuccess(input, result) {
    const container = input.closest('.form-group');
    if (!container) return;

    // إزالة رسائل سابقة
    const oldMsg = container.querySelector('.whatsapp-validation-msg');
    if (oldMsg) oldMsg.remove();

    const successMsg = document.createElement('div');
    successMsg.className = 'whatsapp-validation-msg success';
    successMsg.innerHTML = `
        <i class="fas fa-check-circle"></i>
        رقم صحيح ${result.carrier ? `- ${result.carrier}` : ''}
    `;
    successMsg.className = 'whatsapp-validation-msg success';
    container.appendChild(successMsg);
}

// عرض خطأ الواتساب
function showWhatsAppError(input, error) {
    const container = input.closest('.form-group');
    if (!container) return;

    // إزالة رسائل سابقة
    const oldMsg = container.querySelector('.whatsapp-validation-msg');
    if (oldMsg) oldMsg.remove();

    const errorMsg = document.createElement('div');
    errorMsg.className = 'whatsapp-validation-msg error';
    errorMsg.innerHTML = `<i class="fas fa-times-circle"></i> ${error}`;
    errorMsg.className = 'whatsapp-validation-msg error';
    container.appendChild(errorMsg);
}


// ============================================================================
// 🔥 نظام الدفع المحسن (إصلاحات InstaPay و Telda)
// ============================================================================


// إصلاح دالة ربط InstaPay - استبدال الموجود
function initializeInstapayListener() {
    const instapayInputs = ['payment-link', 'instapay_link'];

    instapayInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            console.log(`🔗 Setting up InstaPay listener for: ${inputId}`);

            // إزالة المستمعين القدامى
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);

            // إضافة مستمعين جدد محسنين
            newInput.addEventListener('input', function (e) {
                validateInstapayInputEnhanced(e.target);
            });

            newInput.addEventListener('paste', function (e) {
                setTimeout(() => {
                    validateInstapayInputEnhanced(e.target);
                }, 100);
            });

            newInput.addEventListener('blur', function (e) {
                validateInstapayInputEnhanced(e.target, true);
            });
        }
    });
}

// دالة محسنة للتحقق من InstaPay
function validateInstapayInputEnhanced(input, showError = false) {
    const text = input.value.trim();
    const container = input.closest('.form-group') || input.closest('.dynamic-input');

    // إزالة المعاينة السابقة
    const existingPreview = container.querySelector('.instapay-preview');
    if (existingPreview) {
        existingPreview.remove();
    }

    if (!text) {
        clearPaymentValidation(input);
        updatePaymentState(input.id, false);
        checkFormValidity(); // 🔥 إضافة مهمة
        return true;
    }

    // محاولة استخلاص الرابط بطرق متعددة
    const extractedLink = extractInstapayLinkEnhanced(text);

    if (extractedLink) {
        // إنشاء معاينة الرابط
        createInstapayPreview(container, extractedLink, text);
        showPaymentSuccess(input);
        updatePaymentState(input.id, true);

        // تحديث قيمة الحقل للرابط المستخلص
        if (input.value !== extractedLink) {
            input.value = extractedLink;
        }

        console.log(`✅ InstaPay link extracted: ${extractedLink}`);
        checkFormValidity(); // 🔥 إضافة مهمة
        return true;

    } else if (showError) {
        showPaymentError(input, 'لم يتم العثور على رابط InstaPay صحيح');
        updatePaymentState(input.id, false);
        checkFormValidity(); // 🔥 إضافة مهمة
        return false;
    }

    updatePaymentState(input.id, false);
    checkFormValidity(); // 🔥 إضافة مهمة
    return false;
}

// تحسين دالة استخلاص روابط InstaPay
function extractInstapayLinkEnhanced(text) {
    // أنماط محسنة مع ترتيب أولوية
    const patterns = [
        // النمط الأساسي الأكثر شيوعاً
        /https?:\/\/(?:www\.)?ipn\.eg\/S\/[^\/\s]+\/instapay\/[A-Za-z0-9]+/gi,
        // أنماط إضافية
        /https?:\/\/(?:www\.)?instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]']+/gi,
        /https?:\/\/(?:www\.)?app\.instapay\.com\.eg\/[^\s<>"{}|\\^`\[\]']+/gi,
        /https?:\/\/(?:www\.)?instapay\.app\/[^\s<>"{}|\\^`\[\]']+/gi,
        /https?:\/\/(?:www\.)?ipn\.eg\/[^\s<>"{}|\\^`\[\]']+/gi,
        // نمط عام للـ InstaPay
        /https?:\/\/[^\s<>"{}|\\^`\[\]']*instapay[^\s<>"{}|\\^`\[\]']*/gi,
    ];

    // البحث بكل الأنماط
    for (const pattern of patterns) {
        const matches = text.match(pattern);
        if (matches && matches.length > 0) {
            for (const match of matches) {
                // تنظيف الرابط
                let link = match.trim();
                // إزالة العلامات من النهاية
                link = link.replace(/[.,;!?\)]+$/, '');

                // التحقق من صحة الرابط
                if (isValidInstapayUrlEnhanced(link)) {
                    return link;
                }
            }
        }
    }

    return null;
}

// تحسين دالة التحقق من صحة الرابط
function isValidInstapayUrlEnhanced(url) {
    if (!url || (!url.startsWith('http://') && !url.startsWith('https://'))) {
        return false;
    }

    const validDomains = [
        'ipn.eg',
        'instapay.com.eg',
        'app.instapay.com.eg',
        'instapay.app',
        'pay.instapay.com.eg'
    ];

    const lowerUrl = url.toLowerCase();
    const domainMatch = validDomains.some(domain => lowerUrl.includes(domain));
    const lengthValid = url.length >= 15; // تقليل الحد الأدنى قليلاً

    return domainMatch && lengthValid;
}

// إصلاح نظام تيلدا - استبدال الموجود
function initializeTeldaCardSystem() {
    const teldaInputs = ['telda_card', 'card-number'];

    teldaInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (!input) return;

        console.log(`💳 Setting up Telda system for: ${inputId}`);

        // إزالة المستمعين القدامى
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);

        // إضافة نظام التنسيق المحسن
        newInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/[^\d]/g, ''); // أرقام فقط
            let formattedValue = '';

            // تنسيق بصيغة 1234-5678-9012-3456
            for (let i = 0; i < value.length; i += 4) {
                if (i > 0) formattedValue += '-';
                formattedValue += value.substr(i, 4);
            }

            // تحديد طول مناسب (16 رقم + 3 شرطات = 19 حرف)
            if (formattedValue.length <= 19) {
                e.target.value = formattedValue;
            }

            // التحقق والتحديث
            validateTeldaCardEnhanced(e.target);
            updateTeldaProgress(e.target, value.length);
        });

        // معالجة اللصق
        newInput.addEventListener('paste', function (e) {
            e.preventDefault();
            let pastedText = (e.clipboardData || window.clipboardData).getData('text');
            let numbers = pastedText.replace(/[^\d]/g, '');

            if (numbers.length <= 16) {
                // تنسيق الأرقام الملصقة
                let formatted = '';
                for (let i = 0; i < numbers.length; i += 4) {
                    if (i > 0) formatted += '-';
                    formatted += numbers.substr(i, 4);
                }
                this.value = formatted;

                // تشغيل التحقق
                validateTeldaCardEnhanced(this);
                updateTeldaProgress(this, numbers.length);
            }
        });

        // معالجة التركيز
        newInput.addEventListener('focus', function () {
            this.parentNode.classList.add('telda-focused');
        });

        newInput.addEventListener('blur', function () {
            this.parentNode.classList.remove('telda-focused');
            validateTeldaCardEnhanced(this, true);
        });
    });
}

// دالة التحقق المحسنة لتيلدا
function validateTeldaCardEnhanced(input, showError = false) {
    const value = input.value;
    const numbersOnly = value.replace(/[^\d]/g, '');
    const container = input.closest('.form-group') || input.closest('.dynamic-input');

    if (numbersOnly.length === 0) {
        clearPaymentValidation(input);
        updatePaymentState(input.id, false);
        checkFormValidity(); // 🔥 إضافة مهمة
        return;
    }

    if (numbersOnly.length < 16) {
        if (container) {
            container.classList.remove('valid', 'invalid');
            container.classList.add('partial');
        }
        if (!showError) {
            showTeldaStatus(input, `جاري الكتابة... (${numbersOnly.length}/16)`, 'partial');
        }
        updatePaymentState(input.id, false);
        checkFormValidity(); // 🔥 إضافة مهمة

    } else if (numbersOnly.length === 16) {
        showPaymentSuccess(input);
        showTeldaStatus(input, '✅ رقم كارت صحيح', 'valid');
        updatePaymentState(input.id, true);
        checkFormValidity(); // 🔥 إضافة مهمة

        if (navigator.vibrate) {
            navigator.vibrate([50, 30, 50]);
        }

    } else {
        if (showError) {
            showPaymentError(input, '❌ رقم طويل جداً');
        }
        showTeldaStatus(input, '❌ رقم طويل جداً', 'invalid');
        updatePaymentState(input.id, false);
        checkFormValidity(); // 🔥 إضافة مهمة
    }
}

// إضافة شريط التقدم لتيلدا
function updateTeldaProgress(input, length) {
    const container = input.parentNode;
    let progressBar = container.querySelector('.telda-progress');

    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.className = 'telda-progress';
        progressBar.innerHTML = '<div class="telda-progress-fill"></div>';
        // CSS classes will handle styling
        container.appendChild(progressBar);
    }

    const progressFill = progressBar.querySelector('.telda-progress-fill');
    if (!progressFill.classList.contains('telda-progress-fill')) {
        progressFill.className = 'telda-progress-fill';
    }

    const percentage = Math.min((length / 16) * 100, 100);
    progressFill.style.width = percentage + '%';

    // ألوان مختلفة حسب التقدم باستخدام CSS classes
    progressFill.className = 'telda-progress-fill';
    if (percentage < 25) {
        progressFill.classList.add('stage-1');
    } else if (percentage < 50) {
        progressFill.classList.add('stage-2');
    } else if (percentage < 75) {
        progressFill.classList.add('stage-3');
    } else if (percentage < 100) {
        progressFill.classList.add('stage-4');
    } else {
        progressFill.classList.add('stage-complete');
    }
}

// دالة عرض حالة تيلدا
function showTeldaStatus(input, message, type) {
    const container = input.parentNode;
    let statusDiv = container.querySelector('.telda-status');

    if (statusDiv) {
        statusDiv.remove();
    }

    if (!message) return;

    statusDiv = document.createElement('div');
    statusDiv.className = `telda-status telda-${type}`;
    statusDiv.textContent = message;
    statusDiv.className = `telda-status telda-${type}`;

    // إضافة كلاس حسب النوع
    if (type === 'valid') {
        statusDiv.classList.add('telda-valid');
    } else if (type === 'invalid') {
        statusDiv.classList.add('telda-invalid');
    } else {
        statusDiv.classList.add('telda-partial');
    }

    container.appendChild(statusDiv);

    setTimeout(() => {
        statusDiv.classList.add('show');
    }, 100);

    // إزالة تلقائية للرسائل الجزئية
    if (type === 'partial') {
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.classList.remove('show');
                setTimeout(() => statusDiv.remove(), 300);
            }
        }, 2000);
    }
}

// إصلاح التحقق الشامل من طرق الدفع - استبدال الموجود
function validatePaymentInput(input) {
    const value = input.value.trim();
    const inputId = input.id;
    let isValid = false;
    let errorMessage = '';

    // إذا كان الحقل فارغاً
    if (!value) {
        clearPaymentValidation(input);
        updatePaymentState(inputId, false);
        checkFormValidity(); // 🔥 إضافة مهمة
        return false;
    }

    // التحقق من المحافظ الإلكترونية (11 رقم)
    if (['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_pay', 'mobile-number'].includes(inputId)) {
        const cleanNumber = value.replace(/[^\d]/g, '');
        isValid = /^01[0125][0-9]{8}$/.test(cleanNumber) && cleanNumber.length === 11;
        errorMessage = 'رقم المحفظة يجب أن يكون 11 رقم (010/011/012/015)';
    }
    // التحقق من كارت تيلدا (16 رقم)
    else if (['telda_card', 'card-number'].includes(inputId)) {
        const numbersOnly = value.replace(/[^\d]/g, '');
        isValid = /^\d{16}$/.test(numbersOnly) && numbersOnly.length === 16;
        errorMessage = `رقم كارت تيلدا يجب أن يكون 16 رقم (تم إدخال ${numbersOnly.length} رقم)`;
    }
    // التحقق من رابط إنستا باي
    else if (['instapay_link', 'payment-link'].includes(inputId)) {
        const extractedLink = extractInstapayLinkEnhanced(value);
        isValid = !!extractedLink;
        errorMessage = 'لم يتم العثور على رابط InstaPay صحيح';

        if (isValid && extractedLink !== value) {
            input.value = extractedLink;
        }
    }

    // تحديث الواجهة والحالة
    if (isValid) {
        showPaymentSuccess(input);
    } else {
        showPaymentError(input, errorMessage);
    }

    updatePaymentState(inputId, isValid);
    checkFormValidity(); // 🔥 إضافة مهمة

    return isValid;
}

// تحديث setupDynamicInputs لضمان تشغيل جميع الإصلاحات
function setupDynamicInputs() {
    // جميع حقول طرق الدفع
    const paymentInputs = [
        'vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_pay',
        'fawry', 'aman', 'masary', 'bee', 'mobile-number',
        'telda_card', 'card-number', 'instapay_link', 'payment-link'
    ];

    paymentInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            // إزالة المستمعين القدامى
            const newInput = input.cloneNode(true);
            input.parentNode.replaceChild(newInput, input);

            // إضافة مستمع واحد فقط
            newInput.addEventListener('input', function () {
                validatePaymentInput(this);
            });

            newInput.addEventListener('blur', function () {
                validatePaymentInput(this);
            });
        }
    });

    // 🔥 تفعيل أنظمة الدفع المحسنة
    console.log('💳 Initializing enhanced payment systems...');

    // تشغيل نظام تيلدا المحسن
    setTimeout(() => {
        initializeTeldaCardSystem();
        console.log('✅ Telda system initialized');
    }, 100);

    // تشغيل نظام InstaPay المحسن
    setTimeout(() => {
        initializeInstapayListener();
        console.log('✅ InstaPay system initialized');
    }, 200);
}




// ============================================================================
// 🔥 نهاية قسم الإصلاحات
// ============================================================================


// ============================================================================
// ✅✅✅ الدوال المساعدة الموحدة لنظام الدفع ✅✅✅
// ============================================================================

// ✅✅✅ النسخة الجديدة والمبسطة ✅✅✅
function updatePaymentState(inputId, isValid) {
    validationStates.paymentMethod = isValid;
    console.log(`💳 Payment state for [${inputId}] is now ${isValid}`);
    // لا تقم باستدعاء checkFormValidity من هنا
}

function showPaymentSuccess(input) {
    const container = input.closest('.form-group') || input.closest('.dynamic-input');
    if (!container) return;

    container.classList.remove('invalid', 'partial');
    container.classList.add('valid');

    const oldMsg = container.querySelector('.payment-validation-msg');
    if (oldMsg) oldMsg.remove();

    const successMsg = document.createElement('div');
    successMsg.className = 'payment-validation-msg success-msg';
    successMsg.innerHTML = '<i class="fas fa-check-circle"></i> البيانات صحيحة';
    // CSS classes will handle styling
    container.appendChild(successMsg);
}

function showPaymentError(input, message) {
    const container = input.closest('.form-group') || input.closest('.dynamic-input');
    if (!container) return;

    container.classList.remove('valid', 'partial');
    container.classList.add('invalid');

    const oldMsg = container.querySelector('.payment-validation-msg');
    if (oldMsg) oldMsg.remove();

    const errorMsg = document.createElement('div');
    errorMsg.className = 'payment-validation-msg error-msg';
    errorMsg.innerHTML = `<i class="fas fa-times-circle"></i> ${message}`;
    // CSS classes will handle styling
    container.appendChild(errorMsg);
}

function clearPaymentValidation(input) {
    const container = input.closest('.form-group') || input.closest('.dynamic-input');
    if (!container) return;

    container.classList.remove('valid', 'invalid', 'partial');

    const msg = container.querySelector('.payment-validation-msg');
    if (msg) msg.remove();
}


// ============================================================================
// 🚀 التفعيل النهائي
// ============================================================================



// ============================================================================
// ✅✅✅ ستايل بداية من اول هنا ✅✅✅
// ============================================================================

// CSS styles moved to external CSS file - no longer needed here

// ============================================================================
// 2222222
// ============================================================================


// WhatsApp enhanced styles moved to external CSS file - no longer needed here



// ============================================================================
// 111111111
// ============================================================================

// Validation styles moved to external CSS file - no longer needed here
