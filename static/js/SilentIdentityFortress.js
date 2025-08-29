// SilentIdentityFortress.js - قلعة الهوية الصامتة المعزولة
/**
 * 🏰 قلعة الهوية الصامتة - FC 26 Silent Identity System
 * ======================================================
 * نظام IIFE معزول تماماً لإدارة الهويات الصامتة
 */

(function SilentIdentityFortressIIFE() {
    'use strict';

    // ============================================================================
    // 🛡️ حارس القلعة - منع الوصول غير المصرح
    // ============================================================================
    const FORTRESS_CONFIG = {
        NAME: 'SilentIdentityFortress',
        VERSION: '1.0.0',
        SECURITY_LEVEL: 'STEALTH',
        STORAGE_KEY: 'fc26_silent_identity',
        IDENTITY_LENGTH: 32,
        DEBUG: false
    };

    // ============================================================================
    // 🕵️ مدير الهوية الصامتة
    // ============================================================================
    class SilentIdentityManager {
        constructor() {
            this.currentIdentity = null;
            this.sessionData = null;
            this.storageAvailable = this.checkStorageSupport();
            this.initialized = false;
            this.cryptoAPI = null;
        }

        // التحقق من دعم التخزين المحلي
        checkStorageSupport() {
            try {
                const test = '__storage_test__';
                localStorage.setItem(test, test);
                localStorage.removeItem(test);
                return true;
            } catch (error) {
                this.log('⚠️ التخزين المحلي غير متاح');
                return false;
            }
        }

        // تهيئة مدير الهوية
        async init() {
            if (this.initialized) return true;

            // انتظار تهيئة قلعة التشفير
            if (window.CryptoFortressAPI) {
                await window.CryptoFortressAPI.initialize();
                this.cryptoAPI = window.CryptoFortressAPI;
            }

            try {
                await this.loadOrCreateIdentity();
                await this.initializeSession();
                
                this.initialized = true;
                this.log('🎯 مدير الهوية الصامتة جاهز');
                return true;
            } catch (error) {
                this.log(`❌ خطأ في تهيئة الهوية: ${error.message}`);
                return false;
            }
        }

        // تحميل أو إنشاء هوية
        async loadOrCreateIdentity() {
            let identity = await this.loadStoredIdentity();
            
            if (!identity) {
                identity = await this.createNewIdentity();
                await this.saveIdentity(identity);
            }

            this.currentIdentity = identity;
            this.log(`🆔 الهوية الحالية: ${identity.id.substring(0, 8)}...`);
        }

        // تحميل الهوية المحفوظة
        async loadStoredIdentity() {
            if (!this.storageAvailable) return null;

            try {
                const storedData = localStorage.getItem(FORTRESS_CONFIG.STORAGE_KEY);
                if (!storedData) return null;

                return JSON.parse(storedData);
            } catch (error) {
                this.log(`⚠️ فشل تحميل الهوية: ${error.message}`);
                return null;
            }
        }

        // إنشاء هوية جديدة
        async createNewIdentity() {
            const fingerprint = await this.generateDeviceFingerprint();
            const timestamp = Date.now();
            
            const identity = {
                id: this.generateUniqueId(),
                deviceFingerprint: fingerprint,
                createdAt: timestamp,
                lastActive: timestamp,
                version: FORTRESS_CONFIG.VERSION,
                metadata: {
                    browser: this.getBrowserInfo(),
                    screen: this.getScreenInfo(),
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    language: navigator.language
                }
            };

            this.log('🆕 تم إنشاء هوية صامتة جديدة');
            return identity;
        }

        // حفظ الهوية
        async saveIdentity(identity) {
            if (!this.storageAvailable) return false;

            try {
                identity.lastActive = Date.now();
                const dataToStore = JSON.stringify(identity);
                localStorage.setItem(FORTRESS_CONFIG.STORAGE_KEY, dataToStore);
                this.log('💾 تم حفظ الهوية بنجاح');
                return true;
            } catch (error) {
                this.log(`❌ فشل حفظ الهوية: ${error.message}`);
                return false;
            }
        }

        // توليد معرف فريد
        generateUniqueId() {
            const timestamp = Date.now().toString(36);
            const randomPart = Math.random().toString(36).substring(2);
            return (timestamp + randomPart).substring(0, FORTRESS_CONFIG.IDENTITY_LENGTH);
        }

        // توليد بصمة الجهاز
        async generateDeviceFingerprint() {
            const components = [
                navigator.userAgent,
                navigator.language,
                screen.width + 'x' + screen.height,
                navigator.platform,
                Intl.DateTimeFormat().resolvedOptions().timeZone
            ];

            const fingerprint = components.join('|');
            
            if (this.cryptoAPI) {
                return await this.cryptoAPI.hash(fingerprint);
            } else {
                // hash بسيط بدون قلعة التشفير
                let hash = 0;
                for (let i = 0; i < fingerprint.length; i++) {
                    const char = fingerprint.charCodeAt(i);
                    hash = ((hash << 5) - hash) + char;
                    hash = hash & hash;
                }
                return Math.abs(hash).toString(36);
            }
        }

        // تهيئة بيانات الجلسة
        async initializeSession() {
            const sessionId = this.generateSessionId();
            const session = {
                id: sessionId,
                identityId: this.currentIdentity.id,
                startTime: Date.now(),
                lastActivity: Date.now(),
                events: []
            };

            this.sessionData = session;
            this.trackPageView();
            this.log(`📊 جلسة جديدة: ${sessionId.substring(0, 8)}...`);
        }

        // توليد معرف الجلسة
        generateSessionId() {
            const timestamp = Date.now().toString(36);
            const random = Math.random().toString(36).substring(2, 10);
            return timestamp + '_' + random;
        }

        // تتبع مشاهدة الصفحة
        trackPageView() {
            const pageView = {
                url: window.location.href,
                title: document.title,
                timestamp: Date.now()
            };

            this.sessionData.events.push({
                type: 'page_view',
                data: pageView,
                timestamp: Date.now()
            });
            
            this.log(`👁️ مشاهدة صفحة: ${pageView.title}`);
        }

        // تتبع حدث
        trackEvent(eventType, data = {}) {
            const event = {
                type: eventType,
                timestamp: Date.now(),
                data: data
            };

            this.sessionData.events.push(event);
            this.sessionData.lastActivity = Date.now();
        }

        // الحصول على معلومات المتصفح
        getBrowserInfo() {
            const ua = navigator.userAgent;
            let browserName = 'Unknown';

            if (ua.includes('Chrome')) browserName = 'Chrome';
            else if (ua.includes('Firefox')) browserName = 'Firefox';
            else if (ua.includes('Safari')) browserName = 'Safari';
            else if (ua.includes('Edge')) browserName = 'Edge';

            return { name: browserName };
        }

        // الحصول على معلومات الشاشة
        getScreenInfo() {
            return {
                width: screen.width,
                height: screen.height
            };
        }

        // سجل الأحداث
        log(message) {
            if (FORTRESS_CONFIG.DEBUG) {
                console.log(`🕵️ ${FORTRESS_CONFIG.NAME}: ${message}`);
            }
        }
    }

    // ============================================================================
    // 🚀 تهيئة القلعة وإنشاء واجهة عامة محدودة
    // ============================================================================
    
    // إنشاء المكونات الأساسية
    const identityManager = new SilentIdentityManager();

    // تهيئة القلعة
    let fortressInitialized = false;

    async function initializeFortress() {
        if (fortressInitialized) return true;

        const success = await identityManager.init();
        if (success) {
            fortressInitialized = true;
            identityManager.log('🎯 قلعة الهوية الصامتة جاهزة ومحمية');
        }

        return success;
    }

    // ============================================================================
    // 🌐 الواجهة العامة المحدودة (فقط للاستخدام الخارجي الآمن)
    // ============================================================================
    
    // كشف واجهة محدودة للنظام الخارجي
    window.SilentIdentityAPI = Object.freeze({
        // تهيئة القلعة
        async initialize() {
            return await initializeFortress();
        },

        // الحصول على الهوية الحالية (معلومات محدودة)
        getCurrentIdentity() {
            if (!fortressInitialized || !identityManager.currentIdentity) {
                return null;
            }

            return {
                id: identityManager.currentIdentity.id,
                createdAt: identityManager.currentIdentity.createdAt,
                lastActive: identityManager.currentIdentity.lastActive,
                sessionId: identityManager.sessionData?.id || null
            };
        },

        // تتبع حدث مخصص
        trackEvent(eventType, data = {}) {
            if (fortressInitialized && identityManager.sessionData) {
                identityManager.trackEvent(eventType, data);
                return true;
            }
            return false;
        },

        // معلومات القلعة
        getInfo() {
            return {
                name: FORTRESS_CONFIG.NAME,
                version: FORTRESS_CONFIG.VERSION,
                initialized: fortressInitialized,
                storageSupported: identityManager.storageAvailable
            };
        }
    });

    // تهيئة تلقائية عند تحميل الصفحة
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFortress);
    } else {
        initializeFortress();
    }

    // إشارة جاهزية القلعة
    console.log('🕵️ قلعة الهوية الصامتة FC26 محملة ومعزولة بأمان');

})(); // انتهاء IIFE المعزول