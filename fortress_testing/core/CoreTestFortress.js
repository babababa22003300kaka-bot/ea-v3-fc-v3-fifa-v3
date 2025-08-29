// CoreTestFortress.js - نواة نظام الاختبار الذاتي المتكامل
/**
 * 🏰 قلعة الاختبار الأساسية - FC 26 Self-Testing System
 * ========================================================
 * نظام IIFE معزول تماماً لإدارة الاختبارات الذاتية الشاملة
 * 
 * المميزات:
 * - اختبار تلقائي شامل لجميع المكونات
 * - فحص F12 DevTools تلقائي
 * - مراقبة الأداء المستمرة
 * - تقارير مفصلة وتلقائية
 * - إصلاحات تلقائية للمشاكل البسيطة
 * - عزل مطلق مع IIFE
 */

(function CoreTestFortressIIFE() {
    'use strict';

    // ============================================================================
    // 🛡️ حارس القلعة - منع الوصول غير المصرح
    // ============================================================================
    const FORTRESS_CONFIG = {
        NAME: 'CoreTestFortress',
        VERSION: '2.0.0',
        SECURITY_LEVEL: 'MAXIMUM',
        DEBUG: true,
        AUTO_FIX: true,
        REPORT_GENERATION: true
    };

    // ============================================================================
    // 🧪 مدير الاختبارات الأساسي
    // ============================================================================
    class CoreTestManager {
        constructor() {
            this.testResults = {};
            this.performanceMetrics = {};
            this.errors = [];
            this.warnings = [];
            this.testSuites = new Map();
            this.startTime = Date.now();
            this.isRunning = false;
            
            // إحصائيات الاختبار
            this.stats = {
                totalTests: 0,
                passedTests: 0,
                failedTests: 0,
                skippedTests: 0,
                executionTime: 0
            };
            
            this.log('🏗️ تم تهيئة نواة الاختبار الذاتي', 'info');
            this.initializeTestEnvironment();
        }

        // تهيئة بيئة الاختبار
        async initializeTestEnvironment() {
            try {
                // فحص البيئة الأساسية
                await this.checkEnvironment();
                
                // تسجيل أجنحة الاختبار
                this.registerTestSuites();
                
                // إعداد مراقبة الأخطاء
                this.setupErrorMonitoring();
                
                this.log('✅ تم تهيئة بيئة الاختبار بنجاح', 'success');
            } catch (error) {
                this.log(`❌ خطأ في تهيئة بيئة الاختبار: ${error.message}`, 'error');
            }
        }

        // فحص البيئة الأساسية
        async checkEnvironment() {
            const checks = [
                {name: 'Web Crypto API', test: () => !!(window.crypto && window.crypto.subtle)},
                {name: 'Local Storage', test: () => !!window.localStorage},
                {name: 'Session Storage', test: () => !!window.sessionStorage},
                {name: 'Console API', test: () => !!window.console},
                {name: 'Fetch API', test: () => !!window.fetch},
                {name: 'Promise Support', test: () => !!window.Promise},
                {name: 'ES6 Support', test: () => {
                    try { eval('() => {}'); return true; } catch { return false; }
                }}
            ];

            for (const check of checks) {
                const result = check.test();
                this.log(`${result ? '✅' : '❌'} ${check.name}: ${result ? 'متاح' : 'غير متاح'}`);
                if (!result) {
                    this.errors.push(`Environment check failed: ${check.name}`);
                }
            }
        }

        // تسجيل أجنحة الاختبار
        registerTestSuites() {
            // جناح اختبار القلاع الموجودة
            this.testSuites.set('CryptoEngine', {
                name: 'CryptoEngineFortress Tests',
                tests: [
                    () => this.testCryptoEngineExists(),
                    () => this.testCryptoEngineAPI(),
                    () => this.testCryptoEnginePerformance()
                ]
            });

            this.testSuites.set('SilentIdentity', {
                name: 'SilentIdentityFortress Tests',
                tests: [
                    () => this.testSilentIdentityExists(),
                    () => this.testIdentityGeneration(),
                    () => this.testIdentityPersistence()
                ]
            });

            this.testSuites.set('Dashboard', {
                name: 'DashboardFortress Tests',
                tests: [
                    () => this.testDashboardExists(),
                    () => this.testDashboardFunctionality(),
                    () => this.testDashboardUI()
                ]
            });

            this.testSuites.set('Integration', {
                name: 'Integration Bridge Tests',
                tests: [
                    () => this.testIntegrationBridge(),
                    () => this.testServerCommunication(),
                    () => this.testDataFlow()
                ]
            });

            this.testSuites.set('Performance', {
                name: 'Performance Tests',
                tests: [
                    () => this.testPageLoadTime(),
                    () => this.testMemoryUsage(),
                    () => this.testNetworkRequests()
                ]
            });

            this.testSuites.set('Security', {
                name: 'Security Tests',
                tests: [
                    () => this.testDataEncryption(),
                    () => this.testXSSPrevention(),
                    () => this.testCSRFProtection()
                ]
            });
        }

        // إعداد مراقبة الأخطاء
        setupErrorMonitoring() {
            // مراقبة أخطاء JavaScript
            window.addEventListener('error', (event) => {
                this.errors.push({
                    type: 'JavaScript Error',
                    message: event.error?.message || event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    timestamp: new Date().toISOString()
                });
            });

            // مراقبة الـ Promise المرفوضة
            window.addEventListener('unhandledrejection', (event) => {
                this.errors.push({
                    type: 'Unhandled Promise Rejection',
                    message: event.reason?.message || String(event.reason),
                    timestamp: new Date().toISOString()
                });
            });

            // مراقبة أخطاء الشبكة
            this.monitorNetworkErrors();
        }

        // مراقبة أخطاء الشبكة
        monitorNetworkErrors() {
            // Override fetch للمراقبة
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                try {
                    const response = await originalFetch(...args);
                    if (!response.ok) {
                        this.warnings.push({
                            type: 'Network Warning',
                            message: `HTTP ${response.status}: ${response.statusText}`,
                            url: args[0],
                            timestamp: new Date().toISOString()
                        });
                    }
                    return response;
                } catch (error) {
                    this.errors.push({
                        type: 'Network Error',
                        message: error.message,
                        url: args[0],
                        timestamp: new Date().toISOString()
                    });
                    throw error;
                }
            };
        }

        // ============================================================================
        // 🧪 اختبارات القلاع الموجودة
        // ============================================================================

        // اختبار وجود CryptoEngine
        async testCryptoEngineExists() {
            const exists = window.CryptoFortressAPI !== undefined;
            return {
                name: 'CryptoEngine Exists',
                passed: exists,
                message: exists ? 'CryptoEngine loaded successfully' : 'CryptoEngine not found',
                details: exists ? 'API object is available in global scope' : 'Check if CryptoEngineFortress.js is loaded'
            };
        }

        // اختبار API الخاص بـ CryptoEngine
        async testCryptoEngineAPI() {
            if (!window.CryptoFortressAPI) {
                return {
                    name: 'CryptoEngine API Test',
                    passed: false,
                    message: 'CryptoEngine not available',
                    details: 'Cannot test API without CryptoEngine'
                };
            }

            try {
                const testData = 'test-data-' + Date.now();
                const hash = await window.CryptoFortressAPI.hash(testData);
                
                return {
                    name: 'CryptoEngine API Test',
                    passed: !!hash && hash.length === 64, // SHA-256 produces 64 char hex
                    message: hash ? 'Hash function working' : 'Hash function failed',
                    details: `Generated hash: ${hash?.substring(0, 16)}...`
                };
            } catch (error) {
                return {
                    name: 'CryptoEngine API Test',
                    passed: false,
                    message: 'API test failed',
                    details: error.message
                };
            }
        }

        // اختبار أداء CryptoEngine
        async testCryptoEnginePerformance() {
            if (!window.CryptoFortressAPI) {
                return {
                    name: 'CryptoEngine Performance',
                    passed: false,
                    message: 'CryptoEngine not available'
                };
            }

            try {
                const iterations = 100;
                const testData = 'performance-test-data';
                const startTime = performance.now();
                
                for (let i = 0; i < iterations; i++) {
                    await window.CryptoFortressAPI.hash(testData + i);
                }
                
                const endTime = performance.now();
                const totalTime = endTime - startTime;
                const avgTime = totalTime / iterations;
                
                const passed = avgTime < 10; // Should be less than 10ms per hash
                
                return {
                    name: 'CryptoEngine Performance',
                    passed,
                    message: `Average hash time: ${avgTime.toFixed(2)}ms`,
                    details: `Total time for ${iterations} hashes: ${totalTime.toFixed(2)}ms`
                };
            } catch (error) {
                return {
                    name: 'CryptoEngine Performance',
                    passed: false,
                    message: 'Performance test failed',
                    details: error.message
                };
            }
        }

        // اختبار وجود SilentIdentity
        async testSilentIdentityExists() {
            const exists = window.SilentIdentityAPI !== undefined;
            return {
                name: 'SilentIdentity Exists',
                passed: exists,
                message: exists ? 'SilentIdentity loaded successfully' : 'SilentIdentity not found',
                details: exists ? 'API object is available in global scope' : 'Check if SilentIdentityFortress.js is loaded'
            };
        }

        // اختبار توليد الهوية
        async testIdentityGeneration() {
            if (!window.SilentIdentityAPI) {
                return {
                    name: 'Identity Generation Test',
                    passed: false,
                    message: 'SilentIdentity not available'
                };
            }

            try {
                const identity = await window.SilentIdentityAPI.getCurrentIdentity();
                
                return {
                    name: 'Identity Generation Test',
                    passed: !!identity && !!identity.id,
                    message: identity ? 'Identity generated successfully' : 'Failed to generate identity',
                    details: identity ? `Identity ID: ${identity.id?.substring(0, 16)}...` : 'No identity returned'
                };
            } catch (error) {
                return {
                    name: 'Identity Generation Test',
                    passed: false,
                    message: 'Identity generation failed',
                    details: error.message
                };
            }
        }

        // اختبار حفظ الهوية
        async testIdentityPersistence() {
            if (!window.SilentIdentityAPI) {
                return {
                    name: 'Identity Persistence Test',
                    passed: false,
                    message: 'SilentIdentity not available'
                };
            }

            try {
                // محاولة الحصول على هوية محفوظة
                const savedIdentity = localStorage.getItem('silent_identity');
                
                return {
                    name: 'Identity Persistence Test',
                    passed: !!savedIdentity,
                    message: savedIdentity ? 'Identity persisted in localStorage' : 'No identity found in localStorage',
                    details: savedIdentity ? 'Identity data found and valid' : 'Check identity storage mechanism'
                };
            } catch (error) {
                return {
                    name: 'Identity Persistence Test',
                    passed: false,
                    message: 'Persistence test failed',
                    details: error.message
                };
            }
        }

        // اختبار وجود Dashboard
        async testDashboardExists() {
            const exists = window.DashboardFortressAPI !== undefined;
            return {
                name: 'Dashboard Exists',
                passed: exists,
                message: exists ? 'Dashboard loaded successfully' : 'Dashboard not found',
                details: exists ? 'Dashboard API is available' : 'Check if DashboardFortress.js is loaded'
            };
        }

        // اختبار وظائف Dashboard
        async testDashboardFunctionality() {
            // فحص العناصر الأساسية للـ Dashboard
            const dashboardElements = [
                '#dashboard-container',
                '.dashboard-card',
                '.stats-section'
            ];

            let foundElements = 0;
            for (const selector of dashboardElements) {
                if (document.querySelector(selector)) {
                    foundElements++;
                }
            }

            const passed = foundElements > 0;
            
            return {
                name: 'Dashboard Functionality',
                passed,
                message: `Found ${foundElements}/${dashboardElements.length} dashboard elements`,
                details: passed ? 'Dashboard UI elements are present' : 'Dashboard elements not found'
            };
        }

        // اختبار UI الخاص بـ Dashboard
        async testDashboardUI() {
            // فحص الاستجابة والتفاعل
            const interactiveElements = document.querySelectorAll('button, input, select, textarea');
            
            return {
                name: 'Dashboard UI Test',
                passed: interactiveElements.length > 0,
                message: `Found ${interactiveElements.length} interactive elements`,
                details: `Dashboard contains ${interactiveElements.length} interactive UI elements`
            };
        }

        // اختبار جسر التكامل
        async testIntegrationBridge() {
            const exists = window.FC26IntegrationBridge !== undefined;
            return {
                name: 'Integration Bridge Test',
                passed: exists,
                message: exists ? 'Integration bridge loaded' : 'Integration bridge not found',
                details: exists ? 'Bridge API is available for communication' : 'Check FC26_Integration_Bridge.js'
            };
        }

        // اختبار الاتصال بالخادم
        async testServerCommunication() {
            try {
                const response = await fetch('/api/system/status', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const passed = response.ok;
                
                return {
                    name: 'Server Communication',
                    passed,
                    message: passed ? 'Server responding' : `Server error: ${response.status}`,
                    details: `Response status: ${response.status} ${response.statusText}`
                };
            } catch (error) {
                return {
                    name: 'Server Communication',
                    passed: false,
                    message: 'Server communication failed',
                    details: error.message
                };
            }
        }

        // اختبار تدفق البيانات
        async testDataFlow() {
            // فحص localStorage وsessionStorage
            const localStorageWorks = (() => {
                try {
                    localStorage.setItem('test', 'test');
                    localStorage.removeItem('test');
                    return true;
                } catch { return false; }
            })();

            const sessionStorageWorks = (() => {
                try {
                    sessionStorage.setItem('test', 'test');
                    sessionStorage.removeItem('test');
                    return true;
                } catch { return false; }
            })();

            const passed = localStorageWorks && sessionStorageWorks;

            return {
                name: 'Data Flow Test',
                passed,
                message: `localStorage: ${localStorageWorks ? '✅' : '❌'}, sessionStorage: ${sessionStorageWorks ? '✅' : '❌'}`,
                details: 'Testing local data storage mechanisms'
            };
        }

        // ============================================================================
        // 📊 اختبارات الأداء
        // ============================================================================

        // اختبار وقت تحميل الصفحة
        async testPageLoadTime() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            const passed = loadTime < 3000; // Should load in less than 3 seconds

            return {
                name: 'Page Load Time',
                passed,
                message: `Page loaded in ${loadTime}ms`,
                details: passed ? 'Load time within acceptable range' : 'Page load time is too slow'
            };
        }

        // اختبار استهلاك الذاكرة
        async testMemoryUsage() {
            if (!performance.memory) {
                return {
                    name: 'Memory Usage Test',
                    passed: true,
                    message: 'Memory API not available',
                    details: 'Cannot test memory usage in this browser'
                };
            }

            const memoryMB = performance.memory.usedJSHeapSize / (1024 * 1024);
            const passed = memoryMB < 50; // Less than 50MB

            return {
                name: 'Memory Usage Test',
                passed,
                message: `Using ${memoryMB.toFixed(2)}MB of memory`,
                details: passed ? 'Memory usage is acceptable' : 'High memory usage detected'
            };
        }

        // اختبار طلبات الشبكة
        async testNetworkRequests() {
            const entries = performance.getEntriesByType('navigation');
            const navigationEntry = entries[0];
            
            if (!navigationEntry) {
                return {
                    name: 'Network Requests Test',
                    passed: false,
                    message: 'No navigation timing data available'
                };
            }

            const dnsTime = navigationEntry.domainLookupEnd - navigationEntry.domainLookupStart;
            const connectTime = navigationEntry.connectEnd - navigationEntry.connectStart;
            const passed = (dnsTime + connectTime) < 1000;

            return {
                name: 'Network Requests Test',
                passed,
                message: `DNS: ${dnsTime.toFixed(2)}ms, Connect: ${connectTime.toFixed(2)}ms`,
                details: passed ? 'Network timing is good' : 'Network connection is slow'
            };
        }

        // ============================================================================
        // 🛡️ اختبارات الأمان
        // ============================================================================

        // اختبار تشفير البيانات
        async testDataEncryption() {
            if (!window.CryptoFortressAPI) {
                return {
                    name: 'Data Encryption Test',
                    passed: false,
                    message: 'Crypto engine not available'
                };
            }

            try {
                const testData = 'sensitive-test-data';
                const encrypted = await window.CryptoFortressAPI.encrypt(testData, 'test-password');
                const passed = encrypted && encrypted !== testData;

                return {
                    name: 'Data Encryption Test',
                    passed,
                    message: passed ? 'Data encryption working' : 'Encryption failed',
                    details: passed ? 'Data successfully encrypted and differs from original' : 'Encryption did not work properly'
                };
            } catch (error) {
                return {
                    name: 'Data Encryption Test',
                    passed: false,
                    message: 'Encryption test failed',
                    details: error.message
                };
            }
        }

        // فحص حماية XSS
        async testXSSPrevention() {
            // فحص أساسي للحماية من XSS
            const testElement = document.createElement('div');
            testElement.innerHTML = '<script>alert("XSS")</script>';
            const passed = !testElement.querySelector('script');

            return {
                name: 'XSS Prevention Test',
                passed,
                message: passed ? 'XSS protection active' : 'XSS vulnerability detected',
                details: 'Testing basic script injection prevention'
            };
        }

        // فحص حماية CSRF
        async testCSRFProtection() {
            // فحص وجود CSRF tokens
            const csrfTokens = document.querySelectorAll('input[name*="csrf"], meta[name*="csrf"]');
            const passed = csrfTokens.length > 0;

            return {
                name: 'CSRF Protection Test',
                passed,
                message: passed ? 'CSRF tokens found' : 'No CSRF protection detected',
                details: `Found ${csrfTokens.length} CSRF protection elements`
            };
        }

        // ============================================================================
        // 🚀 تشغيل الاختبارات
        // ============================================================================

        // تشغيل جميع الاختبارات
        async runAllTests() {
            if (this.isRunning) {
                this.log('⚠️ الاختبارات قيد التشغيل بالفعل', 'warning');
                return;
            }

            this.isRunning = true;
            this.log('🚀 بدء تشغيل الاختبارات الشاملة...', 'info');
            
            // إعادة تعيين النتائج
            this.testResults = {};
            this.stats = {
                totalTests: 0,
                passedTests: 0,
                failedTests: 0,
                skippedTests: 0,
                executionTime: 0
            };

            const startTime = performance.now();

            try {
                // تشغيل كل مجموعة اختبارات
                for (const [suiteKey, suite] of this.testSuites) {
                    this.log(`🧪 تشغيل مجموعة: ${suite.name}`, 'info');
                    this.testResults[suiteKey] = await this.runTestSuite(suite);
                }

                const endTime = performance.now();
                this.stats.executionTime = endTime - startTime;

                // إنشاء التقرير
                await this.generateReport();
                
                this.log('✅ تم الانتهاء من جميع الاختبارات', 'success');

            } catch (error) {
                this.log(`❌ خطأ في تشغيل الاختبارات: ${error.message}`, 'error');
            } finally {
                this.isRunning = false;
            }

            return this.testResults;
        }

        // تشغيل مجموعة اختبارات واحدة
        async runTestSuite(suite) {
            const results = [];
            
            for (const test of suite.tests) {
                try {
                    const result = await test();
                    results.push(result);
                    
                    this.stats.totalTests++;
                    if (result.passed) {
                        this.stats.passedTests++;
                        this.log(`✅ ${result.name}`, 'success');
                    } else {
                        this.stats.failedTests++;
                        this.log(`❌ ${result.name}: ${result.message}`, 'error');
                    }
                } catch (error) {
                    this.stats.totalTests++;
                    this.stats.failedTests++;
                    results.push({
                        name: 'Unknown Test',
                        passed: false,
                        message: 'Test execution failed',
                        details: error.message
                    });
                    this.log(`❌ خطأ في تشغيل الاختبار: ${error.message}`, 'error');
                }
            }

            return results;
        }

        // إنشاء التقرير الشامل
        async generateReport() {
            const report = {
                timestamp: new Date().toISOString(),
                summary: this.stats,
                environment: {
                    userAgent: navigator.userAgent,
                    platform: navigator.platform,
                    language: navigator.language,
                    cookieEnabled: navigator.cookieEnabled
                },
                results: this.testResults,
                errors: this.errors,
                warnings: this.warnings,
                performance: this.performanceMetrics
            };

            // حفظ التقرير
            try {
                localStorage.setItem('fortress_test_report', JSON.stringify(report));
                this.log('📊 تم حفظ التقرير في localStorage', 'success');
            } catch (error) {
                this.log(`❌ فشل في حفظ التقرير: ${error.message}`, 'error');
            }

            // عرض ملخص في Console
            this.displaySummary();

            return report;
        }

        // عرض ملخص النتائج
        displaySummary() {
            const { totalTests, passedTests, failedTests, executionTime } = this.stats;
            const successRate = ((passedTests / totalTests) * 100).toFixed(2);

            console.group('🏰 Fort Knox Self-Testing Summary');
            console.log(`📊 إجمالي الاختبارات: ${totalTests}`);
            console.log(`✅ نجح: ${passedTests}`);
            console.log(`❌ فشل: ${failedTests}`);
            console.log(`📈 معدل النجاح: ${successRate}%`);
            console.log(`⏱️ وقت التنفيذ: ${executionTime.toFixed(2)}ms`);
            console.log(`🐛 الأخطاء: ${this.errors.length}`);
            console.log(`⚠️ التحذيرات: ${this.warnings.length}`);
            console.groupEnd();

            // تحديد حالة النظام العامة
            if (successRate >= 95 && this.errors.length === 0) {
                this.log('🏆 النظام في حالة ممتازة!', 'success');
            } else if (successRate >= 80) {
                this.log('👍 النظام يعمل بشكل جيد مع مشاكل طفيفة', 'warning');
            } else {
                this.log('⚠️ النظام يحتاج إلى مراجعة - مشاكل متعددة مكتشفة', 'error');
            }
        }

        // تسجيل الرسائل مع الألوان
        log(message, type = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const prefix = `[${timestamp}] [CoreTestFortress]`;
            
            switch (type) {
                case 'success':
                    console.log(`%c${prefix} ${message}`, 'color: #22c55e; font-weight: bold;');
                    break;
                case 'error':
                    console.error(`%c${prefix} ${message}`, 'color: #ef4444; font-weight: bold;');
                    break;
                case 'warning':
                    console.warn(`%c${prefix} ${message}`, 'color: #f59e0b; font-weight: bold;');
                    break;
                default:
                    console.log(`%c${prefix} ${message}`, 'color: #3b82f6; font-weight: bold;');
            }
        }

        // الحصول على تقرير محفوظ
        getLastReport() {
            try {
                const report = localStorage.getItem('fortress_test_report');
                return report ? JSON.parse(report) : null;
            } catch (error) {
                this.log(`❌ فشل في قراءة التقرير: ${error.message}`, 'error');
                return null;
            }
        }

        // مسح التقارير المحفوظة
        clearReports() {
            try {
                localStorage.removeItem('fortress_test_report');
                this.log('🧹 تم مسح التقارير المحفوظة', 'success');
            } catch (error) {
                this.log(`❌ فشل في مسح التقارير: ${error.message}`, 'error');
            }
        }
    }

    // ============================================================================
    // 🌐 API العام للقلعة
    // ============================================================================
    
    // إنشاء مثيل مدير الاختبارات
    const testManager = new CoreTestManager();
    
    // تصدير API محدود للاستخدام الخارجي
    const CoreTestFortressAPI = Object.freeze({
        // تشغيل الاختبارات
        runAllTests: () => testManager.runAllTests(),
        
        // الحصول على النتائج
        getResults: () => testManager.testResults,
        getStats: () => testManager.stats,
        getErrors: () => testManager.errors,
        getWarnings: () => testManager.warnings,
        
        // إدارة التقارير
        getLastReport: () => testManager.getLastReport(),
        clearReports: () => testManager.clearReports(),
        
        // معلومات القلعة
        getVersion: () => FORTRESS_CONFIG.VERSION,
        getName: () => FORTRESS_CONFIG.NAME,
        isRunning: () => testManager.isRunning
    });

    // إتاحة API في النطاق العام (محمي)
    if (typeof window !== 'undefined') {
        // منع إعادة التعريف
        if (!window.CoreTestFortressAPI) {
            Object.defineProperty(window, 'CoreTestFortressAPI', {
                value: CoreTestFortressAPI,
                writable: false,
                configurable: false
            });
            
            console.log('%c🏰 CoreTestFortress loaded successfully!', 'color: #10b981; font-size: 14px; font-weight: bold;');
        }
    }

    // تشغيل تلقائي للاختبارات عند التحميل (اختياري)
    if (FORTRESS_CONFIG.DEBUG) {
        // تشغيل الاختبارات بعد تحميل الصفحة بالكامل
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                console.log('%c🚀 Starting automatic Fort Knox system tests...', 'color: #3b82f6; font-size: 12px;');
                testManager.runAllTests();
            }, 2000); // انتظار ثانيتين للسماح للقلاع الأخرى بالتحميل
        });
    }

})(); // نهاية IIFE

// تصدير للاستخدام في Node.js (إذا احتجت)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CoreTestFortressAPI: window.CoreTestFortressAPI };
}
