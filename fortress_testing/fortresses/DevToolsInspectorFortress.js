// DevToolsInspectorFortress.js - قلعة فحص أدوات المطور F12
/**
 * 🔍 قلعة فحص أدوات المطور - FC 26 DevTools Inspector
 * ========================================================
 * نظام IIFE معزول تماماً لمراقبة وفحص أدوات المطور تلقائياً
 * 
 * المميزات:
 * - مراقبة Console للأخطاء والتحذيرات
 * - فحص Network tabs لحالة الطلبات
 * - مراقبة Application storage
 * - فحص Performance وMemory
 * - تتبع تلقائي للمشاكل
 * - تقارير مفصلة لحالة F12
 */

(function DevToolsInspectorFortressIIFE() {
    'use strict';

    // ============================================================================
    // 🛡️ حارس القلعة - منع الوصول غير المصرح
    // ============================================================================
    const FORTRESS_CONFIG = {
        NAME: 'DevToolsInspectorFortress',
        VERSION: '1.0.0',
        SECURITY_LEVEL: 'MAXIMUM',
        DEBUG: true,
        MONITORING_INTERVAL: 5000, // 5 ثوانِ
        MAX_LOG_ENTRIES: 1000
    };

    // ============================================================================
    // 🔍 مدير فحص أدوات المطور
    // ============================================================================
    class DevToolsInspector {
        constructor() {
            this.isMonitoring = false;
            this.monitoringInterval = null;
            this.logs = {
                console: [],
                network: [],
                storage: [],
                performance: [],
                errors: []
            };
            
            // إحصائيات المراقبة
            this.stats = {
                totalErrors: 0,
                totalWarnings: 0,
                totalRequests: 0,
                failedRequests: 0,
                storageUsage: 0,
                memoryUsage: 0
            };

            this.log('🔍 تم تهيئة مفتش أدوات المطور', 'info');
            this.initializeInspector();
        }

        // تهيئة المفتش
        async initializeInspector() {
            try {
                // إعداد مراقبة Console
                this.setupConsoleMonitoring();
                
                // إعداد مراقبة Network
                this.setupNetworkMonitoring();
                
                // إعداد مراقبة Storage
                this.setupStorageMonitoring();
                
                // إعداد مراقبة Performance
                this.setupPerformanceMonitoring();
                
                this.log('✅ تم تهيئة جميع أنظمة المراقبة', 'success');
            } catch (error) {
                this.log(`❌ خطأ في تهيئة المفتش: ${error.message}`, 'error');
            }
        }

        // ============================================================================
        // 🖥️ مراقبة Console
        // ============================================================================

        setupConsoleMonitoring() {
            // احتفاظ بالدوال الأصلية
            const originalConsole = {
                log: console.log,
                warn: console.warn,
                error: console.error,
                info: console.info,
                debug: console.debug
            };

            // إعادة تعريف console methods للمراقبة
            console.log = (...args) => {
                this.addConsoleEntry('log', args);
                originalConsole.log.apply(console, args);
            };

            console.warn = (...args) => {
                this.addConsoleEntry('warn', args);
                this.stats.totalWarnings++;
                originalConsole.warn.apply(console, args);
            };

            console.error = (...args) => {
                this.addConsoleEntry('error', args);
                this.stats.totalErrors++;
                originalConsole.error.apply(console, args);
            };

            console.info = (...args) => {
                this.addConsoleEntry('info', args);
                originalConsole.info.apply(console, args);
            };

            console.debug = (...args) => {
                this.addConsoleEntry('debug', args);
                originalConsole.debug.apply(console, args);
            };

            // مراقبة أخطاء JavaScript العامة
            window.addEventListener('error', (event) => {
                this.addConsoleEntry('error', [{
                    type: 'JavaScript Error',
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    stack: event.error?.stack
                }]);
                this.stats.totalErrors++;
            });

            // مراقبة Promise rejections
            window.addEventListener('unhandledrejection', (event) => {
                this.addConsoleEntry('error', [{
                    type: 'Unhandled Promise Rejection',
                    reason: event.reason,
                    stack: event.reason?.stack
                }]);
                this.stats.totalErrors++;
            });
        }

        // إضافة إدخال console
        addConsoleEntry(level, args) {
            const entry = {
                timestamp: new Date().toISOString(),
                level,
                message: args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
                ).join(' '),
                raw: args
            };

            this.logs.console.push(entry);
            
            // الحفاظ على حد أقصى للإدخالات
            if (this.logs.console.length > FORTRESS_CONFIG.MAX_LOG_ENTRIES) {
                this.logs.console = this.logs.console.slice(-FORTRESS_CONFIG.MAX_LOG_ENTRIES);
            }
        }

        // ============================================================================
        // 🌐 مراقبة Network
        // ============================================================================

        setupNetworkMonitoring() {
            // مراقبة fetch requests
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                const startTime = performance.now();
                const url = args[0];
                
                try {
                    const response = await originalFetch(...args);
                    const endTime = performance.now();
                    
                    this.addNetworkEntry({
                        url,
                        method: args[1]?.method || 'GET',
                        status: response.status,
                        statusText: response.statusText,
                        duration: endTime - startTime,
                        success: response.ok,
                        timestamp: new Date().toISOString()
                    });
                    
                    this.stats.totalRequests++;
                    if (!response.ok) {
                        this.stats.failedRequests++;
                    }
                    
                    return response;
                } catch (error) {
                    const endTime = performance.now();
                    
                    this.addNetworkEntry({
                        url,
                        method: args[1]?.method || 'GET',
                        error: error.message,
                        duration: endTime - startTime,
                        success: false,
                        timestamp: new Date().toISOString()
                    });
                    
                    this.stats.totalRequests++;
                    this.stats.failedRequests++;
                    
                    throw error;
                }
            };

            // مراقبة XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            const originalXHRSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                this._method = method;
                this._url = url;
                this._startTime = performance.now();
                return originalXHROpen.apply(this, [method, url, ...args]);
            };

            XMLHttpRequest.prototype.send = function(...args) {
                const xhr = this;
                
                xhr.addEventListener('loadend', () => {
                    const endTime = performance.now();
                    
                    DevToolsInspectorFortressIIFE.inspector.addNetworkEntry({
                        url: xhr._url,
                        method: xhr._method,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        duration: endTime - xhr._startTime,
                        success: xhr.status >= 200 && xhr.status < 400,
                        timestamp: new Date().toISOString()
                    });
                    
                    DevToolsInspectorFortressIIFE.inspector.stats.totalRequests++;
                    if (xhr.status < 200 || xhr.status >= 400) {
                        DevToolsInspectorFortressIIFE.inspector.stats.failedRequests++;
                    }
                });
                
                return originalXHRSend.apply(this, args);
            };
        }

        // إضافة إدخال network
        addNetworkEntry(entry) {
            this.logs.network.push(entry);
            
            if (this.logs.network.length > FORTRESS_CONFIG.MAX_LOG_ENTRIES) {
                this.logs.network = this.logs.network.slice(-FORTRESS_CONFIG.MAX_LOG_ENTRIES);
            }
        }

        // ============================================================================
        // 💾 مراقبة Storage
        // ============================================================================

        setupStorageMonitoring() {
            // مراقبة localStorage
            const originalSetItem = localStorage.setItem;
            const originalRemoveItem = localStorage.removeItem;
            const originalClear = localStorage.clear;

            localStorage.setItem = (key, value) => {
                this.addStorageEntry('localStorage', 'setItem', key, value?.length);
                return originalSetItem.call(localStorage, key, value);
            };

            localStorage.removeItem = (key) => {
                this.addStorageEntry('localStorage', 'removeItem', key);
                return originalRemoveItem.call(localStorage, key);
            };

            localStorage.clear = () => {
                this.addStorageEntry('localStorage', 'clear');
                return originalClear.call(localStorage);
            };

            // مراقبة sessionStorage
            const originalSessionSetItem = sessionStorage.setItem;
            const originalSessionRemoveItem = sessionStorage.removeItem;
            const originalSessionClear = sessionStorage.clear;

            sessionStorage.setItem = (key, value) => {
                this.addStorageEntry('sessionStorage', 'setItem', key, value?.length);
                return originalSessionSetItem.call(sessionStorage, key, value);
            };

            sessionStorage.removeItem = (key) => {
                this.addStorageEntry('sessionStorage', 'removeItem', key);
                return originalSessionRemoveItem.call(sessionStorage, key);
            };

            sessionStorage.clear = () => {
                this.addStorageEntry('sessionStorage', 'clear');
                return originalSessionClear.call(sessionStorage);
            };

            // تحديث إحصائيات التخزين دورياً
            this.updateStorageStats();
        }

        // إضافة إدخال storage
        addStorageEntry(storageType, action, key = null, valueSize = null) {
            const entry = {
                timestamp: new Date().toISOString(),
                storageType,
                action,
                key,
                valueSize
            };

            this.logs.storage.push(entry);
            
            if (this.logs.storage.length > FORTRESS_CONFIG.MAX_LOG_ENTRIES) {
                this.logs.storage = this.logs.storage.slice(-FORTRESS_CONFIG.MAX_LOG_ENTRIES);
            }

            // تحديث إحصائيات التخزين
            this.updateStorageStats();
        }

        // تحديث إحصائيات التخزين
        updateStorageStats() {
            try {
                let totalSize = 0;
                
                // حساب حجم localStorage
                for (let key in localStorage) {
                    if (localStorage.hasOwnProperty(key)) {
                        totalSize += localStorage[key].length + key.length;
                    }
                }
                
                // حساب حجم sessionStorage
                for (let key in sessionStorage) {
                    if (sessionStorage.hasOwnProperty(key)) {
                        totalSize += sessionStorage[key].length + key.length;
                    }
                }
                
                this.stats.storageUsage = totalSize;
            } catch (error) {
                this.log(`❌ خطأ في تحديث إحصائيات التخزين: ${error.message}`, 'error');
            }
        }

        // ============================================================================
        // ⚡ مراقبة الأداء
        // ============================================================================

        setupPerformanceMonitoring() {
            // مراقبة Performance Observer إذا كان متاحاً
            if ('PerformanceObserver' in window) {
                try {
                    // مراقبة Navigation
                    const navigationObserver = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            this.addPerformanceEntry('navigation', {
                                name: entry.name,
                                duration: entry.duration,
                                loadEventEnd: entry.loadEventEnd,
                                domContentLoadedEventEnd: entry.domContentLoadedEventEnd,
                                timestamp: entry.startTime
                            });
                        }
                    });
                    navigationObserver.observe({ entryTypes: ['navigation'] });

                    // مراقبة Resource loading
                    const resourceObserver = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            this.addPerformanceEntry('resource', {
                                name: entry.name,
                                duration: entry.duration,
                                size: entry.transferSize,
                                type: entry.initiatorType,
                                timestamp: entry.startTime
                            });
                        }
                    });
                    resourceObserver.observe({ entryTypes: ['resource'] });

                    // مراقبة Measure
                    const measureObserver = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            this.addPerformanceEntry('measure', {
                                name: entry.name,
                                duration: entry.duration,
                                timestamp: entry.startTime
                            });
                        }
                    });
                    measureObserver.observe({ entryTypes: ['measure'] });

                } catch (error) {
                    this.log(`⚠️ تحذير في إعداد Performance Observer: ${error.message}`, 'warning');
                }
            }

            // مراقبة Memory إذا كان متاحاً
            if (performance.memory) {
                setInterval(() => {
                    this.updateMemoryStats();
                }, 10000); // كل 10 ثوانِ
            }
        }

        // إضافة إدخال performance
        addPerformanceEntry(type, entry) {
            const performanceEntry = {
                timestamp: new Date().toISOString(),
                type,
                ...entry
            };

            this.logs.performance.push(performanceEntry);
            
            if (this.logs.performance.length > FORTRESS_CONFIG.MAX_LOG_ENTRIES) {
                this.logs.performance = this.logs.performance.slice(-FORTRESS_CONFIG.MAX_LOG_ENTRIES);
            }
        }

        // تحديث إحصائيات الذاكرة
        updateMemoryStats() {
            if (performance.memory) {
                this.stats.memoryUsage = {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit,
                    timestamp: new Date().toISOString()
                };

                this.addPerformanceEntry('memory', this.stats.memoryUsage);
            }
        }

        // ============================================================================
        // 📊 تحليل وتقارير
        // ============================================================================

        // بدء المراقبة المستمرة
        startMonitoring() {
            if (this.isMonitoring) {
                this.log('⚠️ المراقبة نشطة بالفعل', 'warning');
                return;
            }

            this.isMonitoring = true;
            
            this.monitoringInterval = setInterval(() => {
                this.collectMetrics();
            }, FORTRESS_CONFIG.MONITORING_INTERVAL);

            this.log('🔍 بدء المراقبة المستمرة', 'success');
        }

        // إيقاف المراقبة
        stopMonitoring() {
            if (!this.isMonitoring) {
                this.log('⚠️ المراقبة غير نشطة', 'warning');
                return;
            }

            this.isMonitoring = false;
            
            if (this.monitoringInterval) {
                clearInterval(this.monitoringInterval);
                this.monitoringInterval = null;
            }

            this.log('⏹️ تم إيقاف المراقبة', 'info');
        }

        // جمع المقاييس
        collectMetrics() {
            // تحديث إحصائيات التخزين
            this.updateStorageStats();
            
            // تحديث إحصائيات الذاكرة
            this.updateMemoryStats();
            
            // فحص الأخطاء الحديثة
            this.checkRecentErrors();
        }

        // فحص الأخطاء الحديثة
        checkRecentErrors() {
            const recentThreshold = Date.now() - (60 * 1000); // آخر دقيقة
            const recentErrors = this.logs.console.filter(entry => 
                entry.level === 'error' && 
                new Date(entry.timestamp).getTime() > recentThreshold
            );

            if (recentErrors.length > 0) {
                this.log(`⚠️ تم اكتشاف ${recentErrors.length} خطأ في الدقيقة الأخيرة`, 'warning');
            }
        }

        // إنشاء تقرير شامل
        generateReport() {
            const report = {
                timestamp: new Date().toISOString(),
                fortress: FORTRESS_CONFIG.NAME,
                version: FORTRESS_CONFIG.VERSION,
                
                summary: {
                    monitoringActive: this.isMonitoring,
                    totalConsoleEntries: this.logs.console.length,
                    totalNetworkRequests: this.logs.network.length,
                    totalStorageOperations: this.logs.storage.length,
                    totalPerformanceEntries: this.logs.performance.length
                },
                
                stats: this.stats,
                
                recentActivity: {
                    console: this.logs.console.slice(-10),
                    network: this.logs.network.slice(-10),
                    storage: this.logs.storage.slice(-5),
                    performance: this.logs.performance.slice(-5)
                },
                
                analysis: this.analyzeData()
            };

            return report;
        }

        // تحليل البيانات
        analyzeData() {
            const analysis = {
                healthScore: 100,
                issues: [],
                recommendations: []
            };

            // تحليل الأخطاء
            if (this.stats.totalErrors > 0) {
                analysis.healthScore -= Math.min(this.stats.totalErrors * 5, 50);
                analysis.issues.push(`تم اكتشاف ${this.stats.totalErrors} خطأ`);
                analysis.recommendations.push('راجع console logs لحل الأخطاء');
            }

            // تحليل الشبكة
            if (this.stats.failedRequests > 0) {
                const failureRate = (this.stats.failedRequests / this.stats.totalRequests) * 100;
                if (failureRate > 10) {
                    analysis.healthScore -= 20;
                    analysis.issues.push(`معدل فشل عالي في الطلبات: ${failureRate.toFixed(2)}%`);
                    analysis.recommendations.push('فحص اتصال الشبكة وحالة الخادم');
                }
            }

            // تحليل الذاكرة
            if (this.stats.memoryUsage?.used) {
                const memoryMB = this.stats.memoryUsage.used / (1024 * 1024);
                if (memoryMB > 50) {
                    analysis.healthScore -= 15;
                    analysis.issues.push(`استهلاك ذاكرة عالي: ${memoryMB.toFixed(2)}MB`);
                    analysis.recommendations.push('مراجعة كفاءة الكود وتنظيف الذاكرة');
                }
            }

            // تحليل التخزين
            if (this.stats.storageUsage > 5 * 1024 * 1024) { // 5MB
                analysis.healthScore -= 10;
                analysis.issues.push('استهلاك تخزين محلي عالي');
                analysis.recommendations.push('تنظيف البيانات القديمة من localStorage');
            }

            return analysis;
        }

        // الحصول على أخطاء Console فقط
        getConsoleErrors() {
            return this.logs.console.filter(entry => entry.level === 'error');
        }

        // الحصول على الطلبات الفاشلة
        getFailedRequests() {
            return this.logs.network.filter(entry => !entry.success);
        }

        // مسح السجلات
        clearLogs(type = 'all') {
            if (type === 'all') {
                this.logs = {
                    console: [],
                    network: [],
                    storage: [],
                    performance: [],
                    errors: []
                };
                this.log('🧹 تم مسح جميع السجلات', 'info');
            } else if (this.logs[type]) {
                this.logs[type] = [];
                this.log(`🧹 تم مسح سجلات ${type}`, 'info');
            }
        }

        // تسجيل الرسائل مع الألوان
        log(message, type = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const prefix = `[${timestamp}] [DevToolsInspector]`;
            
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
                    console.log(`%c${prefix} ${message}`, 'color: #6366f1; font-weight: bold;');
            }
        }
    }

    // ============================================================================
    // 🌐 API العام للقلعة
    // ============================================================================
    
    // إنشاء مثيل المفتش
    const inspector = new DevToolsInspector();
    
    // جعل المفتش متاحاً للكلاسات الأخرى
    DevToolsInspectorFortressIIFE.inspector = inspector;
    
    // تصدير API محدود للاستخدام الخارجي
    const DevToolsInspectorAPI = Object.freeze({
        // إدارة المراقبة
        startMonitoring: () => inspector.startMonitoring(),
        stopMonitoring: () => inspector.stopMonitoring(),
        isMonitoring: () => inspector.isMonitoring,
        
        // الحصول على البيانات
        getLogs: (type) => type ? inspector.logs[type] : inspector.logs,
        getStats: () => inspector.stats,
        getConsoleErrors: () => inspector.getConsoleErrors(),
        getFailedRequests: () => inspector.getFailedRequests(),
        
        // التقارير والتحليل
        generateReport: () => inspector.generateReport(),
        
        // إدارة البيانات
        clearLogs: (type) => inspector.clearLogs(type),
        
        // معلومات القلعة
        getVersion: () => FORTRESS_CONFIG.VERSION,
        getName: () => FORTRESS_CONFIG.NAME
    });

    // إتاحة API في النطاق العام (محمي)
    if (typeof window !== 'undefined') {
        if (!window.DevToolsInspectorAPI) {
            Object.defineProperty(window, 'DevToolsInspectorAPI', {
                value: DevToolsInspectorAPI,
                writable: false,
                configurable: false
            });
            
            console.log('%c🔍 DevToolsInspectorFortress loaded successfully!', 'color: #6366f1; font-size: 14px; font-weight: bold;');
            
            // بدء المراقبة تلقائياً
            if (FORTRESS_CONFIG.DEBUG) {
                setTimeout(() => {
                    inspector.startMonitoring();
                }, 1000);
            }
        }
    }

})(); // نهاية IIFE

// تصدير للاستخدام في Node.js (إذا احتجت)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DevToolsInspectorAPI: window.DevToolsInspectorAPI };
}
