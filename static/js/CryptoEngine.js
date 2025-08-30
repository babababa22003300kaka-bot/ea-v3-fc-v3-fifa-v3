/**
 * 🔐 CryptoEngine - محرك التشفير المتقدم
 * نسخة محدثة من GitHub مع إصلاحات الأمان
 */

(function(window, undefined) {
    'use strict';

    class CryptoEngine {
        constructor() {
            this.version = '3.0.0';
            this.initialized = false;
            this.keySize = 256;
            this.iterations = 100000;
            
            // Initialize Web Crypto API
            this.crypto = window.crypto || window.msCrypto;
            if (!this.crypto || !this.crypto.subtle) {
                console.error('❌ Web Crypto API غير متاح');
                return;
            }
            
            this.initialized = true;
            console.log('✅ CryptoEngine initialized successfully');
        }

        /**
         * تشفير البيانات باستخدام AES-256-GCM
         */
        async encrypt(data, password) {
            if (!this.initialized) return null;
            
            try {
                // Convert data to ArrayBuffer
                const encoder = new TextEncoder();
                const dataBuffer = encoder.encode(JSON.stringify(data));
                
                // Generate salt and IV
                const salt = this.crypto.getRandomValues(new Uint8Array(16));
                const iv = this.crypto.getRandomValues(new Uint8Array(12));
                
                // Derive key from password
                const key = await this.deriveKey(password, salt);
                
                // Encrypt
                const encryptedData = await this.crypto.subtle.encrypt(
                    { name: 'AES-GCM', iv: iv },
                    key,
                    dataBuffer
                );
                
                // Combine salt, iv, and encrypted data
                const combined = new Uint8Array(salt.length + iv.length + encryptedData.byteLength);
                combined.set(salt, 0);
                combined.set(iv, salt.length);
                combined.set(new Uint8Array(encryptedData), salt.length + iv.length);
                
                // Convert to base64
                return btoa(String.fromCharCode(...combined));
            } catch (error) {
                console.error('❌ خطأ في التشفير:', error);
                return null;
            }
        }

        /**
         * فك تشفير البيانات
         */
        async decrypt(encryptedData, password) {
            if (!this.initialized) return null;
            
            try {
                // Convert from base64
                const combined = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
                
                // Extract salt, iv, and encrypted data
                const salt = combined.slice(0, 16);
                const iv = combined.slice(16, 28);
                const data = combined.slice(28);
                
                // Derive key from password
                const key = await this.deriveKey(password, salt);
                
                // Decrypt
                const decryptedData = await this.crypto.subtle.decrypt(
                    { name: 'AES-GCM', iv: iv },
                    key,
                    data
                );
                
                // Convert back to string
                const decoder = new TextDecoder();
                return JSON.parse(decoder.decode(decryptedData));
            } catch (error) {
                console.error('❌ خطأ في فك التشفير:', error);
                return null;
            }
        }

        /**
         * اشتقاق مفتاح من كلمة المرور
         */
        async deriveKey(password, salt) {
            const encoder = new TextEncoder();
            const passwordBuffer = encoder.encode(password);
            
            // Import password as key
            const passwordKey = await this.crypto.subtle.importKey(
                'raw',
                passwordBuffer,
                'PBKDF2',
                false,
                ['deriveKey']
            );
            
            // Derive AES key
            return await this.crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: salt,
                    iterations: this.iterations,
                    hash: 'SHA-256'
                },
                passwordKey,
                { name: 'AES-GCM', length: this.keySize },
                false,
                ['encrypt', 'decrypt']
            );
        }

        /**
         * توليد hash آمن
         */
        async hash(data) {
            if (!this.initialized) return null;
            
            try {
                const encoder = new TextEncoder();
                const dataBuffer = encoder.encode(data);
                const hashBuffer = await this.crypto.subtle.digest('SHA-256', dataBuffer);
                const hashArray = Array.from(new Uint8Array(hashBuffer));
                return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            } catch (error) {
                console.error('❌ خطأ في الـ hashing:', error);
                return null;
            }
        }

        /**
         * توليد مفتاح عشوائي آمن
         */
        generateRandomKey(length = 32) {
            const array = new Uint8Array(length);
            this.crypto.getRandomValues(array);
            return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
        }

        /**
         * التحقق من قوة كلمة المرور
         */
        checkPasswordStrength(password) {
            let strength = 0;
            
            if (password.length >= 8) strength++;
            if (password.length >= 12) strength++;
            if (/[a-z]/.test(password)) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^a-zA-Z0-9]/.test(password)) strength++;
            
            return {
                score: strength,
                level: strength < 3 ? 'ضعيف' : strength < 5 ? 'متوسط' : 'قوي',
                isAcceptable: strength >= 3
            };
        }
    }

    // Export to global scope
    window.CryptoEngine = CryptoEngine;
    
    // Auto-initialize
    window.cryptoEngine = new CryptoEngine();
    console.log('🔐 CryptoEngine fortress loaded and ready');

})(window);