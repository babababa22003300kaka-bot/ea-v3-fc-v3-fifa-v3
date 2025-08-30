/**
 * 🌉 Integration Bridge - جسر التكامل بين جميع المكونات
 * يربط بين جميع أنظمة الحماية والمكونات
 */

(function(window, undefined) {
    'use strict';

    class IntegrationBridge {
        constructor() {
            this.version = '2.0.0';
            this.components = new Map();
            this.initialized = false;
            this.config = {
                autoConnect: true,
                retryAttempts: 3,
                retryDelay: 1000
            };
            
            // Initialize after DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        /**
         * تهيئة الجسر
         */
        async init() {
            console.log('🌉 Initializing Integration Bridge...');
            
            // Wait for components to load
            await this.waitForComponents();
            
            // Register components
            this.registerComponents();
            
            // Setup inter-component communication
            this.setupCommunication();
            
            // Validate integration
            const validation = this.validateIntegration();
            
            if (validation.success) {
                this.initialized = true;
                console.log('✅ Integration Bridge initialized successfully');
                this.dispatchEvent('bridgeReady', { components: Array.from(this.components.keys()) });
            } else {
                console.error('❌ Integration Bridge initialization failed:', validation.errors);
                this.dispatchEvent('bridgeError', { errors: validation.errors });
            }
            
            return validation;
        }

        /**
         * انتظار تحميل المكونات
         */
        async waitForComponents() {
            const maxWaitTime = 10000; // 10 seconds
            const checkInterval = 100; // Check every 100ms
            const startTime = Date.now();
            
            while (Date.now() - startTime < maxWaitTime) {
                // Check if all required components are loaded
                const requiredComponents = [
                    'CryptoEngine',
                    'SilentIdentity',
                    'Dashboard'
                ];
                
                const allLoaded = requiredComponents.every(comp => window[comp] || window[comp.toLowerCase()]);
                
                if (allLoaded) {
                    console.log('✅ All required components loaded');
                    return true;
                }
                
                // Wait before next check
                await new Promise(resolve => setTimeout(resolve, checkInterval));
            }
            
            console.warn('⚠️ Timeout waiting for components');
            return false;
        }

        /**
         * تسجيل المكونات
         */
        registerComponents() {
            // Register CryptoEngine
            if (window.CryptoEngine || window.cryptoEngine) {
                const crypto = window.cryptoEngine || new window.CryptoEngine();
                this.components.set('crypto', crypto);
                console.log('✅ CryptoEngine registered');
            } else {
                console.warn('⚠️ CryptoEngine not found');
            }
            
            // Register SilentIdentity
            if (window.SilentIdentity || window.silentIdentity) {
                const identity = window.silentIdentity || new window.SilentIdentity();
                this.components.set('identity', identity);
                console.log('✅ SilentIdentity registered');
            } else {
                console.warn('⚠️ SilentIdentity not found');
            }
            
            // Register Dashboard
            if (window.Dashboard || window.dashboard) {
                const dashboard = window.dashboard || new window.Dashboard();
                this.components.set('dashboard', dashboard);
                console.log('✅ Dashboard registered');
            } else {
                console.warn('⚠️ Dashboard not found');
            }
            
            // Register Advanced Security if available
            if (window.advancedSecurity) {
                this.components.set('security', window.advancedSecurity);
                console.log('✅ AdvancedSecurity registered');
            }
            
            // Register FortressSecurity if available
            if (window.FortressSecurityV2) {
                this.components.set('fortress', window.FortressSecurityV2);
                console.log('✅ FortressSecurity registered');
            }
        }

        /**
         * إعداد الاتصال بين المكونات
         */
        setupCommunication() {
            // Setup event-based communication
            this.setupEventBridge();
            
            // Setup API bridges
            this.setupAPIBridges();
            
            // Setup data synchronization
            this.setupDataSync();
        }

        /**
         * إعداد جسر الأحداث
         */
        setupEventBridge() {
            // Forward security events to dashboard
            window.addEventListener('securityThreat', (event) => {
                const dashboard = this.components.get('dashboard');
                if (dashboard) {
                    dashboard.logThreat(event.detail);
                }
            });
            
            // Forward identity changes
            window.addEventListener('identityChanged', (event) => {
                const security = this.components.get('security');
                if (security) {
                    security.updateIdentity(event.detail);
                }
            });
            
            // Forward session events
            window.addEventListener('sessionCreated', (event) => {
                const identity = this.components.get('identity');
                if (identity) {
                    identity.addSession(event.detail);
                }
            });
        }

        /**
         * إعداد جسور API
         */
        setupAPIBridges() {
            // Create unified API
            window.FC26IntegrationBridge = {
                // Crypto operations
                encrypt: async (data, password) => {
                    const crypto = this.components.get('crypto');
                    if (crypto) {
                        return await crypto.encrypt(data, password);
                    }
                    throw new Error('CryptoEngine not available');
                },
                
                decrypt: async (data, password) => {
                    const crypto = this.components.get('crypto');
                    if (crypto) {
                        return await crypto.decrypt(data, password);
                    }
                    throw new Error('CryptoEngine not available');
                },
                
                // Identity operations
                getIdentity: () => {
                    const identity = this.components.get('identity');
                    if (identity) {
                        return identity.getIdentity();
                    }
                    throw new Error('SilentIdentity not available');
                },
                
                verifyDevice: (fingerprint) => {
                    const identity = this.components.get('identity');
                    if (identity) {
                        return identity.verifyDevice(fingerprint);
                    }
                    throw new Error('SilentIdentity not available');
                },
                
                // Dashboard operations
                getSecurityStats: () => {
                    const dashboard = this.components.get('dashboard');
                    if (dashboard) {
                        return dashboard.getSecurityStats();
                    }
                    throw new Error('Dashboard not available');
                },
                
                // Security operations
                secureRequest: async (url, options) => {
                    const security = this.components.get('security') || this.components.get('fortress');
                    if (security && security.secureRequest) {
                        return await security.secureRequest(url, options);
                    }
                    // Fallback to regular fetch
                    return await fetch(url, options);
                },
                
                // Bridge operations
                getComponents: () => {
                    return Array.from(this.components.keys());
                },
                
                isReady: () => {
                    return this.initialized;
                },
                
                getVersion: () => {
                    return this.version;
                }
            };
            
            console.log('✅ API bridges established');
        }

        /**
         * إعداد مزامنة البيانات
         */
        setupDataSync() {
            // Sync identity trust score with security
            setInterval(() => {
                const identity = this.components.get('identity');
                const security = this.components.get('security');
                
                if (identity && security) {
                    const identityData = identity.getIdentity();
                    if (security.updateTrustScore) {
                        security.updateTrustScore(identityData.trustScore);
                    }
                }
            }, 5000);
        }

        /**
         * التحقق من صحة التكامل
         */
        validateIntegration() {
            const errors = [];
            const warnings = [];
            
            // Check required components
            const requiredComponents = ['crypto', 'identity', 'dashboard'];
            requiredComponents.forEach(comp => {
                if (!this.components.has(comp)) {
                    errors.push(`Required component missing: ${comp}`);
                }
            });
            
            // Check component initialization
            this.components.forEach((component, name) => {
                if (component && component.initialized === false) {
                    warnings.push(`Component not initialized: ${name}`);
                }
            });
            
            // Check API availability
            if (!window.FC26IntegrationBridge) {
                errors.push('Integration API not established');
            }
            
            return {
                success: errors.length === 0,
                errors,
                warnings,
                components: Array.from(this.components.keys())
            };
        }

        /**
         * إرسال حدث مخصص
         */
        dispatchEvent(eventName, detail) {
            window.dispatchEvent(new CustomEvent(eventName, {
                detail,
                bubbles: true,
                cancelable: true
            }));
        }

        /**
         * الحصول على مكون
         */
        getComponent(name) {
            return this.components.get(name);
        }

        /**
         * تشغيل اختبار التكامل
         */
        async runIntegrationTest() {
            console.log('🧪 Running integration test...');
            const results = {
                passed: [],
                failed: []
            };
            
            // Test crypto
            try {
                const testData = { test: 'data' };
                const encrypted = await window.FC26IntegrationBridge.encrypt(testData, 'testpass');
                const decrypted = await window.FC26IntegrationBridge.decrypt(encrypted, 'testpass');
                
                if (JSON.stringify(testData) === JSON.stringify(decrypted)) {
                    results.passed.push('Crypto encryption/decryption');
                } else {
                    results.failed.push('Crypto encryption/decryption');
                }
            } catch (error) {
                results.failed.push(`Crypto: ${error.message}`);
            }
            
            // Test identity
            try {
                const identity = window.FC26IntegrationBridge.getIdentity();
                if (identity && identity.id) {
                    results.passed.push('Identity retrieval');
                } else {
                    results.failed.push('Identity retrieval');
                }
            } catch (error) {
                results.failed.push(`Identity: ${error.message}`);
            }
            
            // Test dashboard
            try {
                const stats = window.FC26IntegrationBridge.getSecurityStats();
                if (stats) {
                    results.passed.push('Dashboard stats');
                } else {
                    results.failed.push('Dashboard stats');
                }
            } catch (error) {
                results.failed.push(`Dashboard: ${error.message}`);
            }
            
            // Calculate success rate
            const total = results.passed.length + results.failed.length;
            const successRate = total > 0 ? (results.passed.length / total) * 100 : 0;
            
            console.log(`✅ Passed: ${results.passed.length}`);
            console.log(`❌ Failed: ${results.failed.length}`);
            console.log(`📊 Success rate: ${successRate.toFixed(2)}%`);
            
            return {
                ...results,
                successRate,
                timestamp: Date.now()
            };
        }

        /**
         * تدمير الجسر
         */
        destroy() {
            this.components.clear();
            this.initialized = false;
            delete window.FC26IntegrationBridge;
            console.log('🗑️ Integration Bridge destroyed');
        }
    }

    // Export to global scope
    window.IntegrationBridge = IntegrationBridge;
    
    // Auto-initialize
    window.integrationBridge = new IntegrationBridge();
    console.log('🌉 Integration Bridge loaded');

})(window);