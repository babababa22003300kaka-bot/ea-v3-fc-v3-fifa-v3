// FC26_Integration_Bridge.js - جسر التكامل بين النظام القديم والجديد
/**
 * 🌉 جسر التكامل FC26 - Bridge System
 * ====================================
 * نظام ربط متقدم بين النظام الحالي والقلاع المعزولة الجديدة
 */

(function FC26IntegrationBridge() {
    'use strict';

    // ============================================================================
    // 🌉 إعدادات الجسر
    // ============================================================================
    const BRIDGE_CONFIG = {
        NAME: 'FC26_Integration_Bridge',
        VERSION: '1.0.0',
        AUTO_INIT: true,
        DEBUG: false,
        API_BASE_URL: '/api/identity'
    };

    // ============================================================================
    // 🔗 مدير التكامل الرئيسي
    // ============================================================================
    class IntegrationManager {
        constructor() {
            this.initialized = false;
            this.currentIdentity = null;
            this.currentSession = null;
            this.cryptoReady = false;
            this.identityReady = false;
            this.eventQueue = [];
        }

        // تهيئة مدير التكامل
        async initialize() {
            if (this.initialized) return true;

            try {
                this.log('🚀 بدء تهيئة جسر التكامل...');

                // انتظار جاهزية القلاع
                await this.waitForFortresses();

                // توليد أو استرجاع الهوية الصامتة
                await this.setupSilentIdentity();

                // إنشاء الجلسة
                await this.createSession();

                // بدء تتبع الأحداث
                this.startEventTracking();

                this.initialized = true;
                this.log('✅ جسر التكامل جاهز وعامل');

                // إشعار النظام القديم بالجاهزية
                this.notifySystemReady();

                return true;

            } catch (error) {
                this.log(`❌ خطأ في التهيئة: ${error.message}`);
                return false;
            }
        }

        // انتظار جاهزية القلاع
        async waitForFortresses() {
            const maxWait = 5000; // 5 ثوان
            const checkInterval = 100;
            let waited = 0;

            return new Promise((resolve, reject) => {
                const checkReady = () => {
                    // فحص قلعة التشفير
                    if (window.CryptoFortressAPI && window.CryptoFortressAPI.isSupported()) {
                        this.cryptoReady = true;
                    }

                    // فحص قلعة الهوية
                    if (window.SilentIdentityAPI) {
                        this.identityReady = true;
                    }

                    if (this.cryptoReady && this.identityReady) {
                        this.log('🏰 جميع القلاع جاهزة');
                        resolve();
                        return;
                    }

                    waited += checkInterval;
                    if (waited >= maxWait) {
                        // مستمرين حتى لو لم تكن القلاع جاهزة
                        this.log('⚠️ انتهت مهلة انتظار القلاع - مستمرين بدونها');
                        resolve();
                        return;
                    }

                    setTimeout(checkReady, checkInterval);
                };

                checkReady();
            });
        }

        // إعداد الهوية الصامتة
        async setupSilentIdentity() {
            try {
                // تهيئة قلعة الهوية
                if (window.SilentIdentityAPI) {
                    await window.SilentIdentityAPI.initialize();
                    this.currentIdentity = window.SilentIdentityAPI.getCurrentIdentity();
                }

                if (this.currentIdentity) {
                    this.log(`🆔 الهوية الصامتة: ${this.currentIdentity.id.substring(0, 8)}...`);
                    
                    // طلب تسجيل الهوية في الخادم
                    await this.registerIdentityWithServer();
                } else {
                    this.log('⚠️ لم يتم الحصول على هوية صامتة');
                }

            } catch (error) {
                this.log(`⚠️ خطأ في إعداد الهوية: ${error.message}`);
            }
        }

        // تسجيل الهوية في الخادم
        async registerIdentityWithServer() {
            try {
                // توليد بصمة الجهاز
                const deviceFingerprint = await this.generateDeviceFingerprint();
                
                // معلومات إضافية
                const metadata = {
                    browser: this.getBrowserInfo(),
                    screen: this.getScreenInfo(),
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    language: navigator.language,
                    timestamp: Date.now()
                };

                // طلب من الخادم
                const response = await fetch(`${BRIDGE_CONFIG.API_BASE_URL}/request`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        device_fingerprint: deviceFingerprint,
                        metadata: metadata
                    })
                });

                const result = await response.json();

                if (result.success) {
                    this.log(`📡 تم تسجيل الهوية في الخادم: ${result.action}`);
                    return result;
                } else {
                    throw new Error(result.error || 'فشل تسجيل الهوية');
                }

            } catch (error) {
                this.log(`⚠️ خطأ في التسجيل: ${error.message}`);
                return null;
            }
        }

        // إنشاء جلسة جديدة
        async createSession() {
            try {
                if (!this.currentIdentity) {
                    this.log('⚠️ لا توجد هوية صالحة للجلسة');
                    return null;
                }

                const sessionData = {
                    page: window.location.pathname,
                    referrer: document.referrer || null,
                    userAgent: navigator.userAgent,
                    timestamp: Date.now()
                };

                // طلب إنشاء جلسة من الخادم
                const response = await fetch(`${BRIDGE_CONFIG.API_BASE_URL}/session`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        identity_id: this.currentIdentity.id,
                        session_data: sessionData
                    })
                });

                const result = await response.json();

                if (result.success) {
                    this.currentSession = result.session;
                    this.log(`📊 جلسة جديدة: ${this.currentSession.id.substring(0, 8)}...`);
                    return result;
                } else {
                    throw new Error(result.error || 'فشل في إنشاء الجلسة');
                }

            } catch (error) {
                this.log(`⚠️ خطأ في الجلسة: ${error.message}`);
                return null;
            }
        }

        // بدء تتبع الأحداث
        startEventTracking() {
            // تتبع النقرات
            document.addEventListener('click', (event) => {
                this.trackEvent('click', {
                    element: event.target.tagName,
                    id: event.target.id || null,
                    text: event.target.textContent?.substring(0, 50) || null
                });
            }, true);

            // تتبع إرسال النماذج
            document.addEventListener('submit', (event) => {
                const form = event.target;
                if (form.tagName === 'FORM') {
                    this.trackEvent('form_submit', {
                        formId: form.id || 'unknown',
                        action: form.action || window.location.href
                    });
                }
            });

            this.log('👁️ تم تفعيل تتبع الأحداث');
        }

        // تتبع حدث مخصص
        trackEvent(eventType, eventData = {}) {
            try {
                const event = {
                    type: eventType,
                    data: eventData,
                    timestamp: Date.now(),
                    url: window.location.href
                };

                // إضافة للقائمة المحلية
                this.eventQueue.push(event);

                // تتبع في قلعة الهوية أيضاً
                if (window.SilentIdentityAPI) {
                    window.SilentIdentityAPI.trackEvent(eventType, eventData);
                }

                // إرسال للخادم إذا كانت الجلسة متاحة
                if (this.currentSession) {
                    this.sendEventToServer(event);
                }

                this.log(`📝 حدث جديد: ${eventType}`);

            } catch (error) {
                this.log(`❌ خطأ في تتبع الحدث: ${error.message}`);
            }
        }

        // إرسال حدث للخادم
        async sendEventToServer(event) {
            try {
                const response = await fetch(`${BRIDGE_CONFIG.API_BASE_URL}/track-event`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: this.currentSession.id,
                        event_type: event.type,
                        event_data: event.data
                    })
                });

                const result = await response.json();
                
                if (!result.success) {
                    throw new Error(result.error || 'فشل إرسال الحدث');
                }

            } catch (error) {
                this.log(`⚠️ خطأ في إرسال الحدث: ${error.message}`);
            }
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
            
            if (this.cryptoReady && window.CryptoFortressAPI) {
                return await window.CryptoFortressAPI.hash(fingerprint);
            } else {
                // hash بسيط
                let hash = 0;
                for (let i = 0; i < fingerprint.length; i++) {
                    const char = fingerprint.charCodeAt(i);
                    hash = ((hash << 5) - hash) + char;
                    hash = hash & hash;
                }
                return Math.abs(hash).toString(36);
            }
        }

        // معلومات المتصفح
        getBrowserInfo() {
            const ua = navigator.userAgent;
            const match = ua.match(/(Chrome|Firefox|Safari|Edge)\/([0-9.]+)/);
            return match ? { name: match[1], version: match[2] } : { name: 'Unknown', version: 'Unknown' };
        }

        // معلومات الشاشة
        getScreenInfo() {
            return {
                width: screen.width,
                height: screen.height
            };
        }

        // إشعار النظام بالجاهزية
        notifySystemReady() {
            // إشارة للنظام القديم أن التكامل جاهز
            window.FC26_IDENTITY_READY = true;
            
            // إرسال event مخصص
            window.dispatchEvent(new CustomEvent('FC26IdentityReady', {
                detail: {
                    identity: this.currentIdentity,
                    session: this.currentSession,
                    bridgeVersion: BRIDGE_CONFIG.VERSION
                }
            }));

            this.log('📢 تم إشعار النظام بجاهزية التكامل');
        }

        // سجل الأحداث
        log(message) {
            if (BRIDGE_CONFIG.DEBUG) {
                console.log(`🌉 ${BRIDGE_CONFIG.NAME}: ${message}`);
            }
        }
    }

    // ============================================================================
    // 🚀 تهيئة وتفعيل الجسر
    // ============================================================================
    
    const integrationManager = new IntegrationManager();

    // تهيئة تلقائية
    if (BRIDGE_CONFIG.AUTO_INIT) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                integrationManager.initialize();
            });
        } else {
            integrationManager.initialize();
        }
    }

    // واجهة محدودة للنظام الخارجي
    window.FC26IntegrationBridge = Object.freeze({
        // تهيئة يدوية
        async initialize() {
            return await integrationManager.initialize();
        },

        // تتبع حدث مخصص
        trackEvent(eventType, eventData = {}) {
            integrationManager.trackEvent(eventType, eventData);
        },

        // الحصول على معلومات الهوية
        getIdentityInfo() {
            return {
                identity: integrationManager.currentIdentity,
                session: integrationManager.currentSession,
                ready: integrationManager.initialized
            };
        },

        // معلومات الجسر
        getInfo() {
            return {
                name: BRIDGE_CONFIG.NAME,
                version: BRIDGE_CONFIG.VERSION,
                initialized: integrationManager.initialized
            };
        }
    });

    console.log('🌉 جسر التكامل FC26 محمل ومعزول بأمان');

})(); // انتهاء IIFE المعزول