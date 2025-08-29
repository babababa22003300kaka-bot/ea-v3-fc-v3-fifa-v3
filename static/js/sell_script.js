// sell_script.js - القلاع JavaScript المعزولة لصفحة بيع الكوينز - 6 أقسام
/**
 * 🏰 قلاع بيع الكوينز - FC 26 Profile System
 * ==========================================
 * نظام معزول تماماً مع 6 قلاع منفصلة
 * كل قلعة تعمل بشكل مستقل ولا تؤثر على الأخرى
 */

// ============================================================================
// 🏰 القلعة الأولى: TransferTypeHandler - معالج نوع التحويل
// ============================================================================

class TransferTypeHandler {
    constructor() {
        this.selectedType = 'normal';
        this.rates = {
            instant: 0.85,
            normal: 1.0
        };
        this.cards = null;
        this.init();
    }

    init() {
        this.cards = document.querySelectorAll('.transfer-card');
        this.setupListeners();
        console.log('🏰 TransferTypeHandler initialized');
    }

    setupListeners() {
        this.cards.forEach(card => {
            card.addEventListener('click', (e) => this.handleSelection(e, card));
        });
    }

    handleSelection(event, card) {
        // إزالة التحديد من جميع البطاقات
        this.cards.forEach(c => c.classList.remove('selected'));

        // تحديد البطاقة المختارة
        card.classList.add('selected');
        this.selectedType = card.dataset.type;

        // إرسال حدث للقلاع الأخرى
        window.dispatchEvent(new CustomEvent('transferTypeChanged', {
            detail: { type: this.selectedType, rate: this.rates[this.selectedType] }
        }));

        // اهتزاز للهواتف
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    }

    getSelectedType() {
        return this.selectedType;
    }

    getRate() {
        return this.rates[this.selectedType];
    }
}

// ============================================================================
// 🏰 القلعة الثانية: CoinsQuantityHandler - معالج كمية الكوينز مع تنسيق ذكي
// ============================================================================

class CoinsQuantityHandler {
    constructor() {
        this.minCoins = 100;
        this.maxCoins = 20000; // زيادة الحد الأقصى إلى 5 ملايين
        this.currentAmount = 0;
        this.input = null;
        this.lastValidValue = '';
        this.init();
    }

    init() {
        this.input = document.getElementById('coinsAmount');
        if (this.input) {
            this.setupListener();
        }
        console.log('🏰 CoinsQuantityHandler initialized');
    }

    setupListener() {
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));

        // منع الأحرف غير المرغوب فيها
        this.input.addEventListener('keypress', (e) => this.handleKeyPress(e));
    }

    handleInput(event) {
        const inputValue = event.target.value;

        // تحسين 4: تطبيق فواصل الآلاف في الوقت الفعلي
        const cleanValue = this.parseSmartInput(inputValue);

        if (cleanValue !== null && cleanValue > 0) {
            // تطبيق فواصل الآلاف تلقائياً أثناء الكتابة
            const formattedValue = this.formatNumberWithCommas(cleanValue);
            if (formattedValue !== inputValue) {
                const cursorPos = event.target.selectionStart;
                event.target.value = formattedValue;
                // إعادة وضع المؤشر في الموضع الصحيح
                const newPos = this.adjustCursorPosition(inputValue, formattedValue, cursorPos);
                event.target.setSelectionRange(newPos, newPos);
            }
        }

        if (cleanValue === null) {
            // قيمة غير صحيحة - عرض رسالة خطأ مؤقتة
            this.showTemporaryError('تنسيق غير صحيح - استخدم أرقام فقط أو k/m');
            return;
        }

        // التحقق من الحدود
        if (cleanValue > this.maxCoins) {
            this.showError(`الحد الأقصى ${this.formatNumberDisplay(this.maxCoins)} كوين`);
            event.target.value = this.lastValidValue;
            return;
        }

        if (cleanValue > 0 && cleanValue < this.minCoins) {
            this.showError(`الحد الأدنى ${this.formatNumberDisplay(this.minCoins)} كوين`);
            return;
        }

        // حفظ القيمة الصحيحة
        this.currentAmount = cleanValue;
        this.lastValidValue = event.target.value; // حفظ القيمة المنسقة


        // 🔥 عرض K/M لحظي أثناء الكتابة
        if (cleanValue > 0 && !event.target.matches(':focus')) {
            // إذا الحقل مش مُركز، اعرض التنسيق
            event.target.value = this.formatCoinsKM(cleanValue);
        }

        // إرسال حدث للقلاع الأخرى
        window.dispatchEvent(new CustomEvent('coinsAmountChanged', {
            detail: {
                amount: this.currentAmount,
                isValid: cleanValue >= this.minCoins,
                formattedDisplay: this.formatCoinsKM(cleanValue)  // 🔥 التطبيق الأول
            }
        }));
        // 🔥 عرض K/M في الحقل مباشرة بعد فترة قصيرة
        setTimeout(() => {
            if (this.currentAmount > 0 && !this.input.matches(':focus')) {
                this.input.value = this.formatCoinsKM(this.currentAmount);
            }
        }, 100);
    }

    showError(message) {
        const errorElement = document.getElementById('errorText');
        const errorMessage = document.getElementById('errorMessage');

        if (errorElement && errorMessage) {
            errorElement.textContent = message;
            errorMessage.style.display = 'block';

            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        }
    }

    handleBlur(event) {
        // 🔥 تنسيق القيمة عند فقدان التركيز بتنسيق K/M
        if (this.currentAmount > 0) {
            event.target.value = this.formatCoinsKM(this.currentAmount);  // 🔥 الإصلاح هنا
        }
    }

    handleFocus(event) {
        // إظهار القيمة الخام عند التركيز
        if (this.currentAmount > 0) {
            event.target.value = this.currentAmount.toString();
        }
    }

    handleKeyPress(event) {
        const char = event.key;
        const isNumber = /[0-9]/.test(char);
        const isKM = /[kmKM]/.test(char);
        const isDot = char === '.';
        const isComma = char === ',';
        const isBackspace = char === 'Backspace';
        const isDelete = char === 'Delete';
        const isArrow = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(char);
        const isTab = char === 'Tab';

        if (!isNumber && !isKM && !isDot && !isComma && !isBackspace && !isDelete && !isArrow && !isTab && char !== 'Enter') {
            event.preventDefault();
        }
    }

    parseSmartInput(input) {
        if (!input || input.trim() === '') return 0;

        // تنظيف المدخلات - تحسين 4: قبول فواصل الآلاف
        let clean = input.toString().toLowerCase().trim();

        // إزالة الفواصل والمسافات (مع الاحتفاظ بالرقم)
        clean = clean.replace(/[,\s]/g, '');

        // معالجة تنسيق K/M
        if (clean.includes('k')) {
            const num = parseFloat(clean.replace('k', ''));
            if (isNaN(num)) return null;
            return Math.floor(num * 1000);
        }

        if (clean.includes('m')) {
            const num = parseFloat(clean.replace('m', ''));
            if (isNaN(num)) return null;
            return Math.floor(num * 1000000);
        }

        // رقم عادي
        const num = parseFloat(clean);
        if (isNaN(num)) return null;
        return Math.floor(num);
    }

    formatNumberDisplay(number) {
        if (number === 0) return '0';

        // تحسين 4: تنسيق بالفواصل الإنجليزية مع فواصل آلاف تلقائية
        return Math.round(number).toLocaleString('en-US');
    }

    // 🔥 الدالة الجديدة: تنسيق K/M حسب المطلوب
    formatCoinsKM(number) {
        if (number === 0) return '0';

        const rounded = Math.round(number);

        // قاعدة التنسيق الجديدة
        if (rounded < 1000) {
            return `${rounded.toLocaleString('en-US')} K`;
        } else {
            return `${rounded.toLocaleString('en-US')} M`;
        }
    }

    formatNumberWithCommas(number) {
        // تحسين 4: تطبيق فواصل الآلاف تلقائياً
        return Math.round(number).toLocaleString('en-US');
    }

    adjustCursorPosition(oldValue, newValue, oldPos) {
        // حساب الموضع الجديد للمؤشر بعد تطبيق فواصل الآلاف
        const commasBefore = (oldValue.substring(0, oldPos).match(/,/g) || []).length;
        const commasAfter = (newValue.substring(0, oldPos).match(/,/g) || []).length;
        return oldPos + (commasAfter - commasBefore);
    }

    showTemporaryError(message) {
        // عرض رسالة خطأ مؤقتة لمدة ثانية واحدة
        const errorElement = document.getElementById('errorText');
        const errorMessage = document.getElementById('errorMessage');

        if (errorElement && errorMessage) {
            errorElement.textContent = message;
            errorMessage.style.display = 'block';

            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 1000);
        }
    }

    getAmount() {
        return this.currentAmount;
    }

    isValid() {
        return this.currentAmount >= this.minCoins && this.currentAmount <= this.maxCoins;
    }
}

// ============================================================================
// 🏰 القلعة الثالثة: PriceDisplayHandler - معالج عرض السعر
// ============================================================================

class PriceDisplayHandler {
    constructor() {
        this.coinPrice = 0.10; // السعر بالجنيه
        this.container = null;
        this.elements = {};
        this.init();
    }

    init() {
        this.container = document.querySelector('.price-display-fortress');
        this.cacheElements();
        this.setupListeners();
        console.log('🏰 PriceDisplayHandler initialized');
    }

    cacheElements() {
        this.elements = {
            basePrice: document.getElementById('basePrice'),
            discountCard: document.getElementById('discountCard'),
            discountAmount: document.getElementById('discountAmount'),
            finalPrice: document.getElementById('finalPriceDisplay'),
            instantPrice: document.querySelector('#instantPrice .price-amount'),
            normalPrice: document.querySelector('#normalPrice .price-amount')
        };
    }

    setupListeners() {
        // الاستماع لتغيير الكوينز
        window.addEventListener('coinsAmountChanged', (e) => {
            this.updatePrices(e.detail.amount, e.detail.isValid);
        });

        // الاستماع لتغيير نوع التحويل
        window.addEventListener('transferTypeChanged', (e) => {
            this.updateDiscount(e.detail.type, e.detail.rate);
        });
    }

    updatePrices(amount, isValid) {
        if (!isValid || amount === 0) {
            this.hide();
            return;
        }

        const basePrice = amount * this.coinPrice;
        const instantPrice = basePrice * 0.85;
        const normalPrice = basePrice * 1.0;

        // === التعديل المطلوب هنا: تقريب جميع المبالغ قبل عرضها ===

        // تحديث الأسعار الأساسية مع تنسيق إنجليزي (بعد التقريب)
        if (this.elements.basePrice) {
            this.elements.basePrice.textContent = `${this.formatCurrency(Math.round(basePrice))} جنيه`;
        }

        // تحديث أسعار البطاقات (بعد التقريب)
        if (this.elements.instantPrice) {
            this.elements.instantPrice.textContent = `${this.formatCurrency(Math.round(instantPrice))} جنيه`;
        }

        if (this.elements.normalPrice) {
            this.elements.normalPrice.textContent = `${this.formatCurrency(Math.round(normalPrice))} جنيه`;
        }

        // إظهار القسم
        this.show();

        // تحديث السعر النهائي (سيتم تقريبه أيضاً داخل هذه الدالة)
        this.updateFinalPrice();
    }

    updateDiscount(type, rate) {
        const coinsAmount = window.coinsQuantityHandler?.getAmount() || 0;
        if (coinsAmount === 0) return;

        const basePrice = coinsAmount * this.coinPrice;
        const finalPrice = basePrice * rate;
        const discount = basePrice - finalPrice;

        // تحسين 2: إخفاء بطاقة الخصم نهائياً
        if (this.elements.discountCard) {
            this.elements.discountCard.style.display = 'none';
        }

        if (this.elements.finalPrice) {
            this.elements.finalPrice.textContent = `${this.formatCurrency(finalPrice)} جنيه`;
        }
    }

    updateFinalPrice() {
        const type = window.transferTypeHandler?.getSelectedType() || 'normal';
        const rate = window.transferTypeHandler?.getRate() || 1.0;
        this.updateDiscount(type, rate);
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
        }
    }

    formatCurrency(amount) {
        // تحسين 1: تنسيق العملة بدون كسور عشرية + تحسين 4: فواصل آلاف تلقائية
        return Math.round(amount).toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }
}

// ============================================================================
// 🏰 القلعة الرابعة: EAAccountHandler - معالج حساب EA
// ============================================================================

class EAAccountHandler {
    constructor() {
        this.data = {
            email: '',
            password: '',
            recoveryCodes: []
        };
        this.inputMode = 'separate';
        this.elements = {};
        this.init();
    }

    init() {
        this.cacheElements();
        this.setupListeners();
        console.log('🏰 EAAccountHandler initialized');
    }

    cacheElements() {
        this.elements = {
            email: document.getElementById('eaEmail'),
            password: document.getElementById('eaPassword'),
            passwordToggle: document.getElementById('passwordToggleIcon'),
            separateInputs: document.getElementById('separateCodesInput'),
            bulkInput: document.getElementById('bulkCodesInput'),
            bulkTextarea: document.getElementById('bulkCodesTextarea'),
            codeInputs: document.querySelectorAll('.recovery-code-input'),
            optionButtons: document.querySelectorAll('.option-btn')
        };
    }

    setupListeners() {
        // Email و Password with Real-time Validation
        if (this.elements.email) {
            this.elements.email.addEventListener('input', (e) => {
                this.data.email = e.target.value;
                this.performRealtimeEmailValidation(e.target.value, e.target);
                this.validateAndNotify();
            });

            // إضافة مستمع blur للتحقق النهائي
            this.elements.email.addEventListener('blur', (e) => {
                this.performAdvancedEmailValidation(e.target.value, e.target);
            });
        }

        if (this.elements.password) {
            this.elements.password.addEventListener('input', (e) => {
                this.data.password = e.target.value;
                this.validateAndNotify();
            });
        }

        // أكواد الاسترداد المنفصلة
        this.elements.codeInputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 8);
                e.target.value = value;

                // الانتقال التلقائي للحقل التالي
                if (value.length === 8 && index < this.elements.codeInputs.length - 1) {
                    this.elements.codeInputs[index + 1].focus();
                }

                this.updateRecoveryCodes();
            });
        });

        // حقل اللصق الشامل مع Smart Clipboard
        if (this.elements.bulkTextarea) {
            this.elements.bulkTextarea.addEventListener('input', (e) => {
                this.extractCodesFromBulk(e.target.value);
            });

            // 🔥 SMART ENHANCEMENT: Smart Clipboard Paste Button
            this.addSmartClipboardButton();
        }
    }

    switchMode(mode) {
        this.inputMode = mode;

        // تحديث الأزرار
        this.elements.optionButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // إظهار/إخفاء الحقول
        if (mode === 'separate') {
            this.elements.separateInputs.style.display = 'grid';
            this.elements.bulkInput.style.display = 'none';
        } else {
            this.elements.separateInputs.style.display = 'none';
            this.elements.bulkInput.style.display = 'block';
        }
    }

    extractCodesFromBulk(text) {
        // استخراج جميع الأرقام من 8 خانات
        const codes = text.match(/\d{8}/g) || [];
        this.data.recoveryCodes = codes.slice(0, 6); // أخذ أول 6 أكواد فقط

        // تحديث الحقول المنفصلة إذا وجدت أكواد
        if (this.data.recoveryCodes.length > 0) {
            this.elements.codeInputs.forEach((input, index) => {
                input.value = this.data.recoveryCodes[index] || '';
            });
        }

        this.validateAndNotify();
    }

    updateRecoveryCodes() {
        this.data.recoveryCodes = [];
        this.elements.codeInputs.forEach(input => {
            if (input.value.length === 8) {
                this.data.recoveryCodes.push(input.value);
            }
        });

        this.validateAndNotify();
    }

    togglePasswordVisibility() {
        const passwordInput = this.elements.password;
        const icon = this.elements.passwordToggle;

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    }

    validateAndNotify() {
        const isValid = this.isValid();

        // إرسال حدث للقلاع الأخرى
        window.dispatchEvent(new CustomEvent('eaAccountChanged', {
            detail: {
                isValid: isValid,
                data: this.data
            }
        }));
    }

    // 🔥 SMART ENHANCEMENT: Real-time Email Validation
    performRealtimeEmailValidation(email, inputElement) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const commonProviders = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com'];

        // إزالة الرسائل السابقة
        this.clearEmailFeedback(inputElement);

        if (email.length === 0) {
            this.setEmailFeedback(inputElement, '', 'neutral');
            return;
        }

        if (email.length < 5) {
            this.setEmailFeedback(inputElement, 'البريد الإلكتروني قصير جداً', 'warning');
            return;
        }

        if (!email.includes('@')) {
            this.setEmailFeedback(inputElement, 'يجب أن يحتوي على @', 'error');
            return;
        }

        if (emailRegex.test(email)) {
            const domain = email.split('@')[1].toLowerCase();
            if (commonProviders.includes(domain)) {
                this.setEmailFeedback(inputElement, '✅ بريد إلكتروني صحيح', 'success');
            } else {
                this.setEmailFeedback(inputElement, '⚠️ نطاق غير مألوف - تأكد من صحته', 'warning');
            }
        } else {
            this.setEmailFeedback(inputElement, '❌ تنسيق البريد الإلكتروني غير صحيح', 'error');
        }
    }

    // 🔥 SMART ENHANCEMENT: Advanced Email Validation
    performAdvancedEmailValidation(email, inputElement) {
        if (!email || email.length === 0) return;

        const eaProviders = ['hotmail.com', 'outlook.com', 'live.com', 'xbox.com', 'ea.com'];
        const domain = email.includes('@') ? email.split('@')[1].toLowerCase() : '';

        if (eaProviders.includes(domain)) {
            this.setEmailFeedback(inputElement, '🎮 مزود خدمة متوافق مع EA', 'success');
        } else if (domain) {
            this.setEmailFeedback(inputElement, '⚠️ تأكد من أن هذا البريد مربوط بحساب EA', 'warning');
        }
    }

    // 🔥 SMART ENHANCEMENT: Email Feedback System
    setEmailFeedback(inputElement, message, type) {
        // تحديث لون الحدود
        inputElement.classList.remove('email-success', 'email-warning', 'email-error', 'email-neutral');
        inputElement.classList.add(`email-${type}`);

        // إنشاء أو تحديث رسالة التغذية الراجعة
        let feedbackElement = inputElement.parentNode.querySelector('.email-feedback');
        if (!feedbackElement) {
            feedbackElement = document.createElement('div');
            feedbackElement.className = 'email-feedback';
            inputElement.parentNode.appendChild(feedbackElement);
        }

        feedbackElement.textContent = message;
        feedbackElement.className = `email-feedback feedback-${type}`;

        // إضافة تأثير بصري
        if (type === 'success' && navigator.vibrate) {
            navigator.vibrate(50);
        } else if (type === 'error' && navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
    }

    // 🔥 SMART ENHANCEMENT: Clear Email Feedback
    clearEmailFeedback(inputElement) {
        const feedbackElement = inputElement.parentNode.querySelector('.email-feedback');
        if (feedbackElement) {
            feedbackElement.textContent = '';
        }
        inputElement.classList.remove('email-success', 'email-warning', 'email-error', 'email-neutral');
    }

    isValid() {
        return this.data.email.includes('@') &&
            this.data.password.length >= 6 &&
            this.data.recoveryCodes.length >= 1;
    }

    getData() {
        return this.data;
    }

    // 🔥 SMART ENHANCEMENT: Smart Clipboard Functionality
    addSmartClipboardButton() {
        const bulkContainer = this.elements.bulkInput;
        if (!bulkContainer || bulkContainer.querySelector('.smart-paste-btn')) return;

        const pasteButton = document.createElement('button');
        pasteButton.type = 'button';
        pasteButton.className = 'smart-paste-btn';
        pasteButton.innerHTML = '<i class="fas fa-paste"></i> لصق ذكي من الحافظة';

        pasteButton.addEventListener('click', async () => {
            await this.performSmartClipboardPaste();
        });

        // إدراج الزر قبل textarea
        bulkContainer.insertBefore(pasteButton, this.elements.bulkTextarea);
    }

    // 🔥 SMART ENHANCEMENT: Smart Clipboard Paste Implementation
    async performSmartClipboardPaste() {
        try {
            // التحقق من دعم Clipboard API
            if (!navigator.clipboard || !navigator.clipboard.readText) {
                this.showClipboardError('متصفحك لا يدعم الوصول للحافظة');
                return;
            }

            // قراءة النص من الحافظة
            const clipboardText = await navigator.clipboard.readText();

            if (!clipboardText || clipboardText.trim().length === 0) {
                this.showClipboardError('الحافظة فارغة');
                return;
            }

            // استخراج الأكواد بذكاء
            const extractedCodes = this.intelligentCodeExtraction(clipboardText);

            if (extractedCodes.length === 0) {
                this.showClipboardError('لم يتم العثور على أكواد صالحة (8 أرقام)');
                return;
            }

            // تطبيق الأكواد
            this.elements.bulkTextarea.value = extractedCodes.join('\n');
            this.extractCodesFromBulk(this.elements.bulkTextarea.value);

            // إظهار رسالة نجاح
            this.showClipboardSuccess(`تم استخراج ${extractedCodes.length} كود بنجاح`);

            // اهتزاز نجاح
            if (navigator.vibrate) {
                navigator.vibrate([50, 100, 50]);
            }

        } catch (error) {
            console.error('Clipboard paste error:', error);
            this.showClipboardError('فشل في قراءة الحافظة - تأكد من الأذونات');
        }
    }

    // 🔥 SMART ENHANCEMENT: Intelligent Code Extraction
    intelligentCodeExtraction(text) {
        // البحث عن أكواد 8 أرقام مع دعم التنسيقات المختلفة
        const patterns = [
            /\b\d{8}\b/g,                    // 8 أرقام منفصلة
            /\d{4}[\s-]\d{4}/g,             // 4-4 format
            /\d{2}[\s-]\d{2}[\s-]\d{2}[\s-]\d{2}/g, // 2-2-2-2 format
        ];

        let allCodes = [];

        patterns.forEach(pattern => {
            const matches = text.match(pattern) || [];
            matches.forEach(match => {
                // تنظيف الكود (إزالة المسافات والشرطات)
                const cleanCode = match.replace(/[^\d]/g, '');
                if (cleanCode.length === 8 && !allCodes.includes(cleanCode)) {
                    allCodes.push(cleanCode);
                }
            });
        });

        // إرجاع أول 6 أكواد
        return allCodes.slice(0, 6);
    }

    // 🔥 SMART ENHANCEMENT: Clipboard Feedback
    showClipboardSuccess(message) {
        this.showClipboardFeedback(message, 'success');
    }

    showClipboardError(message) {
        this.showClipboardFeedback(message, 'error');
    }

    showClipboardFeedback(message, type) {
        let feedbackElement = this.elements.bulkInput.querySelector('.clipboard-feedback');
        if (!feedbackElement) {
            feedbackElement = document.createElement('div');
            feedbackElement.className = 'clipboard-feedback';
            this.elements.bulkInput.appendChild(feedbackElement);
        }

        feedbackElement.textContent = message;
        feedbackElement.className = `clipboard-feedback feedback-${type}`;

        // إزالة الرسالة بعد 3 ثواني
        setTimeout(() => {
            if (feedbackElement.parentNode) {
                feedbackElement.textContent = '';
            }
        }, 3000);
    }
}

// ============================================================================
// 🏰 القلعة الخامسة: NotesHandler - معالج الملاحظات
// ============================================================================

class NotesHandler {
    constructor() {
        this.maxLength = 500;
        this.content = '';
        this.elements = {};
        this.init();
    }

    init() {
        this.cacheElements();
        this.setupListener();
        console.log('🏰 NotesHandler initialized');
    }

    cacheElements() {
        this.elements = {
            textarea: document.getElementById('sellNotes'),
            counter: document.getElementById('notesCount')
        };
    }

    setupListener() {
        if (this.elements.textarea) {
            this.elements.textarea.addEventListener('input', (e) => this.handleInput(e));
        }
    }

    handleInput(event) {
        const value = event.target.value;
        const length = value.length;

        // تحديث العداد
        if (this.elements.counter) {
            this.elements.counter.textContent = length;
        }

        // حفظ المحتوى
        this.content = value;

        // إرسال حدث
        window.dispatchEvent(new CustomEvent('notesChanged', {
            detail: { content: this.content, length: length }
        }));
    }

    getContent() {
        return this.content;
    }
}

// ============================================================================
// 🏰 القلعة السادسة: OrderConfirmationHandler - معالج تأكيد الطلب
// ============================================================================

class OrderConfirmationHandler {
    constructor() {
        this.elements = {};
        this.isReady = false;
        this.init();
    }

    init() {
        this.cacheElements();
        this.setupListeners();
        console.log('🏰 OrderConfirmationHandler initialized');
    }

    cacheElements() {
        this.elements = {
            section: document.getElementById('summarySection'),
            confirmBtn: document.getElementById('confirmBtn'),

            // عناصر الملخص
            summaryCoins: document.getElementById('summaryCoins'),
            summaryType: document.getElementById('summaryType'),
            summaryBase: document.getElementById('summaryBase'),
            summaryDiscount: document.getElementById('summaryDiscount'),
            summaryTotal: document.getElementById('summaryTotal'),
            discountRow: document.getElementById('discountRow'),

            // ملخص EA
            eaSummary: document.getElementById('eaSummary'),
            summaryEaEmail: document.getElementById('summaryEaEmail'),
            summaryRecoveryCodes: document.getElementById('summaryRecoveryCodes'),

            // شاشة التحميل
            loading: document.getElementById('loading')
        };
    }

    setupListeners() {
        // الاستماع لجميع التغييرات
        window.addEventListener('coinsAmountChanged', (e) => this.updateSummary());
        window.addEventListener('transferTypeChanged', (e) => this.updateSummary());
        window.addEventListener('eaAccountChanged', (e) => this.updateEaSummary(e.detail));

        // زر التأكيد
        if (this.elements.confirmBtn) {
            this.elements.confirmBtn.addEventListener('click', () => this.handleConfirm());
        }
    }

    updateSummary() {
        const coinsAmount = window.coinsQuantityHandler?.getAmount() || 0;
        const isValid = window.coinsQuantityHandler?.isValid() || false;

        if (!isValid) {
            this.hide();
            return;
        }

        const transferType = window.transferTypeHandler?.getSelectedType() || 'normal';
        const rate = window.transferTypeHandler?.getRate() || 1.0;
        const coinPrice = 0.10;
        const basePrice = coinsAmount * coinPrice;
        const finalPrice = basePrice * rate;

        this.elements.summaryCoins.textContent = this.formatCoinsKM(coinsAmount);  // 🔥 التطبيق الثاني
        this.elements.summaryType.textContent = transferType === 'instant' ? 'فوري (خلال ساعة)' : 'عادي (خلال 24 ساعة)';
        this.elements.summaryBase.textContent = `${this.formatCurrency(basePrice)} جنيه`;
        this.elements.summaryTotal.textContent = `${this.formatCurrency(finalPrice)} جنيه`;

        this.show();
        this.checkReadiness();
    }


    updateEaSummary(detail) {
        if (!detail.isValid) {
            if (this.elements.eaSummary) {
                this.elements.eaSummary.style.display = 'none';
            }
            return;
        }

        const data = detail.data;

        if (this.elements.eaSummary) {
            this.elements.eaSummary.style.display = 'block';
        }

        if (this.elements.summaryEaEmail) {
            this.elements.summaryEaEmail.textContent = data.email || '-';
        }

        if (this.elements.summaryRecoveryCodes) {
            const codesText = data.recoveryCodes.length > 0 ?
                `${data.recoveryCodes.length} أكواد مدخلة` : 'غير مدخلة';
            this.elements.summaryRecoveryCodes.textContent = codesText;
        }

        this.checkReadiness();
    }

    checkReadiness() {
        const coinsValid = window.coinsQuantityHandler?.isValid() || false;
        const eaValid = window.eaAccountHandler?.isValid() || false;

        this.isReady = coinsValid && eaValid;

        if (this.elements.confirmBtn) {
            this.elements.confirmBtn.disabled = !this.isReady;
        }
    }

    async handleConfirm() {
        if (!this.isReady) return;

        this.showLoading();

        try {
            // جمع البيانات من جميع القلاع
            const requestData = {
                coins_amount: window.coinsQuantityHandler.getAmount(),
                transfer_type: window.transferTypeHandler.getSelectedType(),
                notes: window.notesHandler?.getContent() || '',
                ea_account: window.eaAccountHandler.getData(),
                user_id: document.getElementById('userId')?.value || 'guest',
                whatsapp_number: document.getElementById('userWhatsapp')?.value || '',
                platform: document.getElementById('userPlatform')?.value || ''
            };

            // إرسال الطلب
            const response = await fetch('/api/sell-coins', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            this.hideLoading();

            if (result.success) {
                this.showSuccessModal(result.request_id);

                // اهتزاز نجاح
                if (navigator.vibrate) {
                    navigator.vibrate([200, 100, 200]);
                }

                // 🔥 إضافة: التوجيه إلى لوحة التحكم بعد 3 ثوان
                if (result.redirect_url) {
                    setTimeout(() => {
                        window.location.href = result.redirect_url;
                    }, 3000); // 3 ثوان عشان يشوف رقم الطلب
                }
            } else {
                this.showError(result.error || 'حدث خطأ في إرسال الطلب');
            }

        } catch (error) {
            console.error('خطأ في إرسال الطلب:', error);
            this.hideLoading();
            this.showError('خطأ في الاتصال، يرجى المحاولة مرة أخرى');
        }
    }

    showLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.add('show');
        }
    }

    hideLoading() {
        if (this.elements.loading) {
            this.elements.loading.classList.remove('show');
        }
    }

    showSuccessModal(requestId) {
        const modal = document.getElementById('successOverlay');
        const idElement = document.getElementById('requestId');

        if (idElement) {
            idElement.textContent = requestId;
        }

        if (modal) {
            modal.style.display = 'flex';

            // 🔥 إضافة: إضافة زر لوحة التحكم إذا لم يكن موجود
            let dashboardBtn = modal.querySelector('.dashboard-btn');
            if (!dashboardBtn) {
                dashboardBtn = document.createElement('button');
                dashboardBtn.className = 'dashboard-btn';
                dashboardBtn.textContent = 'انتقال إلى لوحة التحكم';
                dashboardBtn.style.cssText = `
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    cursor: pointer;
                    margin: 10px;
                    font-size: 16px;
                `;
                dashboardBtn.onclick = () => {
                    window.location.href = '/dashboard';
                };
                modal.appendChild(dashboardBtn);
            }
        }
    }

    showError(message) {
        const errorText = document.getElementById('errorText');
        const errorMessage = document.getElementById('errorMessage');

        if (errorText) {
            errorText.textContent = message;
        }

        if (errorMessage) {
            errorMessage.style.display = 'block';

            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 5000);
        }

        // اهتزاز خطأ
        if (navigator.vibrate) {
            navigator.vibrate([300, 100, 300]);
        }
    }

    show() {
        if (this.elements.section) {
            this.elements.section.style.display = 'block';
        }
    }

    formatNumber(number) {
        // تنسيق الأرقام بالإنجليزية مع فواصل الآلاف
        return number.toLocaleString('en-US');
    }

    formatCurrency(amount) {
        // *** الحل النهائي والمثالي هنا ***
        // 1. نقوم بتقريب الرقم إلى أقرب عدد صحيح
        const roundedAmount = Math.round(amount);

        // 2. نستخدم 'en-US' لعرض الأرقام بالشكل الإنجليزي مع فواصل الآلاف
        return roundedAmount.toLocaleString('en-US');
    }



    hide() {
        if (this.elements.section) {
            this.elements.section.style.display = 'none';
        }
    }
    formatCurrency(amount) {
        // *** الحل النهائي والمثالي هنا ***
        // 1. نقوم بتقريب الرقم إلى أقرب عدد صحيح
        const roundedAmount = Math.round(amount);

        // 2. نستخدم 'en-US' لعرض الأرقام بالشكل الإنجليزي مع فواصل الآلاف
        return roundedAmount.toLocaleString('en-US');
    }

    // 🔥 إضافة دالة K/M للملخص
    formatCoinsKM(number) {
        if (number === 0) return '0';

        const rounded = Math.round(number);

        // قاعدة التنسيق الجديدة
        if (rounded < 1000) {
            return `${rounded.toLocaleString('en-US')} K`;
        } else {
            return `${rounded.toLocaleString('en-US')} M`;
        }
    }
}

// ============================================================================
// 🚀 التهيئة الرئيسية - إنشاء القلاع المعزولة
// ============================================================================

// متغيرات عامة للقلاع
window.transferTypeHandler = null;
window.coinsQuantityHandler = null;
window.priceDisplayHandler = null;
window.eaAccountHandler = null;
window.notesHandler = null;
window.orderConfirmationHandler = null;

document.addEventListener('DOMContentLoaded', function () {
    console.log('🏰 بدء تهيئة القلاع المعزولة...');

    // إنشاء القلاع الست
    window.transferTypeHandler = new TransferTypeHandler();
    window.coinsQuantityHandler = new CoinsQuantityHandler();
    window.priceDisplayHandler = new PriceDisplayHandler();
    window.eaAccountHandler = new EAAccountHandler();
    window.notesHandler = new NotesHandler();
    window.orderConfirmationHandler = new OrderConfirmationHandler();

    // إنشاء الجسيمات المتحركة
    createSellParticles();

    console.log('✅ جميع القلاع جاهزة للعمل!');
});

// ============================================================================
// 🎨 دوال مساعدة عامة
// ============================================================================

/**
 * إنشاء الجسيمات المتحركة
 */
function createSellParticles() {
    const container = document.getElementById('particlesBg');
    if (!container) return;

    const particleCount = window.innerWidth <= 768 ? 10 : 20;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 6) + 's';
        container.appendChild(particle);
    }
}

/**
 * تبديل رؤية كلمة المرور
 */
function togglePasswordVisibility() {
    if (window.eaAccountHandler) {
        window.eaAccountHandler.togglePasswordVisibility();
    }
}

/**
 * تبديل وضع إدخال أكواد الاسترداد
 */
function switchRecoveryMode(mode) {
    if (window.eaAccountHandler) {
        window.eaAccountHandler.switchMode(mode);
    }
}

/**
 * إغلاق نافذة النجاح
 */
function closeSuccessModal() {
    const overlay = document.getElementById('successOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }

    // العودة للرئيسية
    window.location.href = '/';
}

/**
 * 🔥 NEW: Perform Smart Paste - دالة اللصق الذكي الموحدة
 */
async function performSmartPaste() {
    try {
        // التحقق من دعم Clipboard API
        if (!navigator.clipboard || !navigator.clipboard.readText) {
            showSmartPasteError('متصفحك لا يدعم الوصول للحافظة');
            return;
        }

        // قراءة النص من الحافظة
        const clipboardText = await navigator.clipboard.readText();

        if (!clipboardText || clipboardText.trim().length === 0) {
            showSmartPasteError('الحافظة فارغة');
            return;
        }

        // استخراج الأكواد بذكاء
        const extractedCodes = intelligentCodeExtraction(clipboardText);

        if (extractedCodes.length === 0) {
            showSmartPasteError('لم يتم العثور على أكواد صالحة (8 أرقام)');
            return;
        }

        // تطبيق الأكواد على الحقول المنفصلة
        const codeInputs = document.querySelectorAll('.recovery-code-input');
        codeInputs.forEach((input, index) => {
            input.value = extractedCodes[index] || '';
        });

        // تحديث البيانات في EAAccountHandler
        if (window.eaAccountHandler) {
            window.eaAccountHandler.data.recoveryCodes = extractedCodes;
            window.eaAccountHandler.validateAndNotify();
        }

        // إظهار رسالة نجاح
        showSmartPasteSuccess(`تم استخراج ${extractedCodes.length} كود بنجاح`);

        // اهتزاز نجاح
        if (navigator.vibrate) {
            navigator.vibrate([50, 100, 50]);
        }

    } catch (error) {
        console.error('Smart paste error:', error);
        showSmartPasteError('فشل في قراءة الحافظة - تأكد من الأذونات');
    }
}

/**
 * استخراج ذكي للأكواد من النص
 */
function intelligentCodeExtraction(text) {
    // البحث عن أكواد 8 أرقام مع دعم التنسيقات المختلفة
    const patterns = [
        /\b\d{8}\b/g,                    // 8 أرقام منفصلة
        /\d{4}[\s-]\d{4}/g,             // 4-4 format
        /\d{2}[\s-]\d{2}[\s-]\d{2}[\s-]\d{2}/g, // 2-2-2-2 format
    ];

    let allCodes = [];

    patterns.forEach(pattern => {
        const matches = text.match(pattern) || [];
        matches.forEach(match => {
            // تنظيف الكود (إزالة المسافات والشرطات)
            const cleanCode = match.replace(/[^\d]/g, '');
            if (cleanCode.length === 8 && !allCodes.includes(cleanCode)) {
                allCodes.push(cleanCode);
            }
        });
    });

    // إرجاع أول 6 أكواد
    return allCodes.slice(0, 6);
}

/**
 * إظهار رسالة نجاح اللصق الذكي
 */
function showSmartPasteSuccess(message) {
    showSmartPasteFeedback(message, 'success');
}

/**
 * إظهار رسالة خطأ اللصق الذكي
 */
function showSmartPasteError(message) {
    showSmartPasteFeedback(message, 'error');
}

/**
 * إظهار رسالة تغذية راجعة للصق الذكي
 */
function showSmartPasteFeedback(message, type) {
    const container = document.querySelector('.recovery-input-options').parentNode;

    let feedbackElement = container.querySelector('.smart-paste-feedback');
    if (!feedbackElement) {
        feedbackElement = document.createElement('div');
        feedbackElement.className = 'smart-paste-feedback';
        container.appendChild(feedbackElement);
    }

    feedbackElement.textContent = message;
    feedbackElement.className = `smart-paste-feedback feedback-${type}`;

    // إزالة الرسالة بعد 3 ثواني
    setTimeout(() => {
        if (feedbackElement.parentNode) {
            feedbackElement.textContent = '';
        }
    }, 3000);
}

// ============================================================================
// 🌐 تصدير للاستخدام الخارجي
// ============================================================================


window.togglePasswordVisibility = togglePasswordVisibility;
window.switchRecoveryMode = switchRecoveryMode;
window.closeSuccessModal = closeSuccessModal;
window.performSmartPaste = performSmartPaste;
