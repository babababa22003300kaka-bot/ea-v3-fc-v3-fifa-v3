/**
 * 🕵️ SilentIdentity - نظام الهوية الصامتة
 * يدير هوية المستخدم بشكل آمن وصامت
 */

(function(window, undefined) {
    'use strict';

    class SilentIdentity {
        constructor() {
            this.version = '2.0.0';
            this.storageKey = 'fc26_silent_identity';
            this.identity = null;
            this.deviceFingerprint = null;
            
            // Initialize identity
            this.init();
            console.log('🕵️ SilentIdentity initialized');
        }

        /**
         * تهيئة الهوية
         */
        init() {
            // Load existing identity or create new one
            this.identity = this.loadIdentity() || this.createNewIdentity();
            
            // Generate device fingerprint
            this.deviceFingerprint = this.generateDeviceFingerprint();
            
            // Validate identity
            if (!this.validateIdentity()) {
                console.warn('⚠️ Identity validation failed, creating new identity');
                this.identity = this.createNewIdentity();
            }
            
            // Save identity
            this.saveIdentity();
        }

        /**
         * إنشاء هوية جديدة
         */
        createNewIdentity() {
            const now = Date.now();
            return {
                id: this.generateUniqueId(),
                created: now,
                lastSeen: now,
                trustScore: 50,
                sessions: [],
                deviceFingerprint: this.generateDeviceFingerprint(),
                metadata: {
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    platform: navigator.platform,
                    screenResolution: `${screen.width}x${screen.height}`,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
                }
            };
        }

        /**
         * توليد معرف فريد
         */
        generateUniqueId() {
            const timestamp = Date.now().toString(36);
            const randomStr = Math.random().toString(36).substr(2, 9);
            const browserEntropy = this.getBrowserEntropy();
            return `${timestamp}${randomStr}${browserEntropy}`;
        }

        /**
         * الحصول على entropy من المتصفح
         */
        getBrowserEntropy() {
            let entropy = '';
            
            // Collect various browser properties
            const props = [
                navigator.hardwareConcurrency,
                navigator.maxTouchPoints,
                screen.colorDepth,
                new Date().getTimezoneOffset()
            ];
            
            props.forEach(prop => {
                if (prop !== undefined) {
                    entropy += prop.toString();
                }
            });
            
            // Hash the entropy
            let hash = 0;
            for (let i = 0; i < entropy.length; i++) {
                const char = entropy.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32bit integer
            }
            
            return Math.abs(hash).toString(36);
        }

        /**
         * توليد بصمة الجهاز
         */
        generateDeviceFingerprint() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            // Create canvas fingerprint
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('FC26 Identity 🔐', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('FC26 Identity 🔐', 4, 17);
            
            // Get canvas data
            const canvasData = canvas.toDataURL();
            
            // Combine with system properties
            const fingerprint = {
                canvas: this.hashString(canvasData),
                screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
                timezone: new Date().getTimezoneOffset(),
                languages: navigator.languages.join(','),
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency || 0,
                memory: navigator.deviceMemory || 0,
                touchPoints: navigator.maxTouchPoints || 0
            };
            
            return this.hashString(JSON.stringify(fingerprint));
        }

        /**
         * hash سلسلة نصية
         */
        hashString(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                const char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            return Math.abs(hash).toString(16);
        }

        /**
         * التحقق من صحة الهوية
         */
        validateIdentity() {
            if (!this.identity) return false;
            
            // Check if identity has required fields
            const requiredFields = ['id', 'created', 'deviceFingerprint'];
            for (const field of requiredFields) {
                if (!this.identity[field]) return false;
            }
            
            // Check if device fingerprint matches
            if (this.identity.deviceFingerprint !== this.deviceFingerprint) {
                console.warn('⚠️ Device fingerprint mismatch');
                // Allow some flexibility for minor changes
                // return false;
            }
            
            // Check if identity is not too old (30 days)
            const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
            if (this.identity.created < thirtyDaysAgo) {
                console.warn('⚠️ Identity is too old');
                return false;
            }
            
            return true;
        }

        /**
         * تحديث نقاط الثقة
         */
        updateTrustScore(delta) {
            if (!this.identity) return;
            
            this.identity.trustScore = Math.max(0, Math.min(100, 
                (this.identity.trustScore || 50) + delta
            ));
            
            this.saveIdentity();
        }

        /**
         * إضافة جلسة جديدة
         */
        addSession(sessionData) {
            if (!this.identity) return;
            
            this.identity.sessions = this.identity.sessions || [];
            this.identity.sessions.push({
                ...sessionData,
                timestamp: Date.now()
            });
            
            // Keep only last 10 sessions
            if (this.identity.sessions.length > 10) {
                this.identity.sessions = this.identity.sessions.slice(-10);
            }
            
            this.identity.lastSeen = Date.now();
            this.saveIdentity();
        }

        /**
         * حفظ الهوية
         */
        saveIdentity() {
            if (!this.identity) return;
            
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(this.identity));
                console.log('✅ Identity saved');
            } catch (error) {
                console.error('❌ Failed to save identity:', error);
            }
        }

        /**
         * تحميل الهوية
         */
        loadIdentity() {
            try {
                const stored = localStorage.getItem(this.storageKey);
                if (stored) {
                    const identity = JSON.parse(stored);
                    console.log('✅ Identity loaded');
                    return identity;
                }
            } catch (error) {
                console.error('❌ Failed to load identity:', error);
            }
            return null;
        }

        /**
         * الحصول على الهوية الحالية
         */
        getIdentity() {
            return {
                id: this.identity?.id,
                trustScore: this.identity?.trustScore || 0,
                deviceFingerprint: this.deviceFingerprint,
                isValid: this.validateIdentity()
            };
        }

        /**
         * مسح الهوية
         */
        clearIdentity() {
            this.identity = null;
            localStorage.removeItem(this.storageKey);
            console.log('🗑️ Identity cleared');
        }

        /**
         * التحقق من الجهاز
         */
        verifyDevice(fingerprint) {
            return fingerprint === this.deviceFingerprint;
        }
    }

    // Export to global scope
    window.SilentIdentity = SilentIdentity;
    
    // Auto-initialize
    window.silentIdentity = new SilentIdentity();
    console.log('🕵️ SilentIdentity fortress loaded and ready');

})(window);