/**
 * 📊 Dashboard - لوحة التحكم الأمنية
 * نظام مراقبة وإدارة الأمان في الوقت الفعلي
 */

(function(window, undefined) {
    'use strict';

    class Dashboard {
        constructor() {
            this.version = '2.0.0';
            this.metrics = {
                requests: [],
                threats: [],
                sessions: [],
                performance: {}
            };
            this.updateInterval = null;
            this.isActive = false;
            
            this.init();
            console.log('📊 Dashboard initialized');
        }

        /**
         * تهيئة لوحة التحكم
         */
        init() {
            // Initialize metrics collection
            this.startMetricsCollection();
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize UI if exists
            this.initializeUI();
            
            this.isActive = true;
        }

        /**
         * بدء جمع المقاييس
         */
        startMetricsCollection() {
            // Collect performance metrics every 5 seconds
            this.updateInterval = setInterval(() => {
                this.collectPerformanceMetrics();
                this.updateDashboard();
            }, 5000);
            
            // Initial collection
            this.collectPerformanceMetrics();
        }

        /**
         * جمع مقاييس الأداء
         */
        collectPerformanceMetrics() {
            // Memory usage
            if (performance.memory) {
                this.metrics.performance.memory = {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit,
                    percentage: (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100
                };
            }
            
            // Navigation timing
            if (performance.timing) {
                const timing = performance.timing;
                this.metrics.performance.pageLoad = {
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    domInteractive: timing.domInteractive - timing.navigationStart,
                    dns: timing.domainLookupEnd - timing.domainLookupStart,
                    tcp: timing.connectEnd - timing.connectStart,
                    request: timing.responseStart - timing.requestStart,
                    response: timing.responseEnd - timing.responseStart
                };
            }
            
            // Resource timing
            const resources = performance.getEntriesByType('resource');
            this.metrics.performance.resources = {
                count: resources.length,
                totalSize: resources.reduce((total, r) => total + (r.transferSize || 0), 0),
                avgDuration: resources.reduce((total, r) => total + r.duration, 0) / resources.length || 0
            };
        }

        /**
         * إضافة تهديد للسجل
         */
        logThreat(threat) {
            this.metrics.threats.push({
                ...threat,
                timestamp: Date.now(),
                id: this.generateId()
            });
            
            // Keep only last 100 threats
            if (this.metrics.threats.length > 100) {
                this.metrics.threats = this.metrics.threats.slice(-100);
            }
            
            // Update UI
            this.updateThreatDisplay();
        }

        /**
         * تسجيل طلب
         */
        logRequest(request) {
            this.metrics.requests.push({
                ...request,
                timestamp: Date.now(),
                id: this.generateId()
            });
            
            // Keep only last 100 requests
            if (this.metrics.requests.length > 100) {
                this.metrics.requests = this.metrics.requests.slice(-100);
            }
        }

        /**
         * تسجيل جلسة
         */
        logSession(session) {
            this.metrics.sessions.push({
                ...session,
                timestamp: Date.now(),
                id: this.generateId()
            });
            
            // Keep only last 50 sessions
            if (this.metrics.sessions.length > 50) {
                this.metrics.sessions = this.metrics.sessions.slice(-50);
            }
        }

        /**
         * الحصول على إحصائيات الأمان
         */
        getSecurityStats() {
            const now = Date.now();
            const oneHourAgo = now - (60 * 60 * 1000);
            const oneDayAgo = now - (24 * 60 * 60 * 1000);
            
            return {
                threats: {
                    total: this.metrics.threats.length,
                    lastHour: this.metrics.threats.filter(t => t.timestamp > oneHourAgo).length,
                    lastDay: this.metrics.threats.filter(t => t.timestamp > oneDayAgo).length,
                    byType: this.groupBy(this.metrics.threats, 'type')
                },
                requests: {
                    total: this.metrics.requests.length,
                    lastHour: this.metrics.requests.filter(r => r.timestamp > oneHourAgo).length,
                    lastDay: this.metrics.requests.filter(r => r.timestamp > oneDayAgo).length,
                    byStatus: this.groupBy(this.metrics.requests, 'status')
                },
                sessions: {
                    active: this.metrics.sessions.filter(s => s.active).length,
                    total: this.metrics.sessions.length,
                    avgDuration: this.calculateAvgSessionDuration()
                },
                performance: this.metrics.performance
            };
        }

        /**
         * حساب متوسط مدة الجلسات
         */
        calculateAvgSessionDuration() {
            const completedSessions = this.metrics.sessions.filter(s => s.endTime);
            if (completedSessions.length === 0) return 0;
            
            const totalDuration = completedSessions.reduce((total, s) => {
                return total + (s.endTime - s.startTime);
            }, 0);
            
            return totalDuration / completedSessions.length;
        }

        /**
         * تجميع البيانات حسب خاصية
         */
        groupBy(array, key) {
            return array.reduce((result, item) => {
                const group = item[key] || 'unknown';
                result[group] = (result[group] || 0) + 1;
                return result;
            }, {});
        }

        /**
         * تحديث لوحة التحكم
         */
        updateDashboard() {
            const stats = this.getSecurityStats();
            
            // Update UI elements if they exist
            this.updateElement('dashboard-threats-total', stats.threats.total);
            this.updateElement('dashboard-threats-hour', stats.threats.lastHour);
            this.updateElement('dashboard-requests-total', stats.requests.total);
            this.updateElement('dashboard-requests-hour', stats.requests.lastHour);
            this.updateElement('dashboard-sessions-active', stats.sessions.active);
            
            // Update performance metrics
            if (stats.performance.memory) {
                this.updateElement('dashboard-memory-usage', 
                    `${Math.round(stats.performance.memory.percentage)}%`
                );
            }
            
            // Dispatch custom event
            window.dispatchEvent(new CustomEvent('dashboardUpdated', {
                detail: stats
            }));
        }

        /**
         * تحديث عنصر في الواجهة
         */
        updateElement(id, value) {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        }

        /**
         * تحديث عرض التهديدات
         */
        updateThreatDisplay() {
            const container = document.getElementById('dashboard-threats-list');
            if (!container) return;
            
            // Clear existing
            container.innerHTML = '';
            
            // Add recent threats
            const recentThreats = this.metrics.threats.slice(-5).reverse();
            recentThreats.forEach(threat => {
                const item = document.createElement('div');
                item.className = `threat-item threat-${threat.severity}`;
                item.innerHTML = `
                    <span class="threat-type">${threat.type}</span>
                    <span class="threat-message">${threat.message}</span>
                    <span class="threat-time">${new Date(threat.timestamp).toLocaleTimeString()}</span>
                `;
                container.appendChild(item);
            });
        }

        /**
         * إعداد مستمعي الأحداث
         */
        setupEventListeners() {
            // Listen for security events
            window.addEventListener('securityThreat', (event) => {
                this.logThreat(event.detail);
            });
            
            window.addEventListener('secureRequest', (event) => {
                this.logRequest(event.detail);
            });
            
            window.addEventListener('sessionCreated', (event) => {
                this.logSession(event.detail);
            });
        }

        /**
         * تهيئة واجهة المستخدم
         */
        initializeUI() {
            // Check if dashboard container exists
            const container = document.getElementById('security-dashboard');
            if (!container) return;
            
            // Add basic structure if not exists
            if (!container.innerHTML) {
                container.innerHTML = this.getDashboardHTML();
            }
            
            console.log('✅ Dashboard UI initialized');
        }

        /**
         * الحصول على HTML للوحة التحكم
         */
        getDashboardHTML() {
            return `
                <div class="dashboard-header">
                    <h2>🛡️ لوحة التحكم الأمنية</h2>
                    <span class="dashboard-status">نشط</span>
                </div>
                <div class="dashboard-metrics">
                    <div class="metric-card">
                        <h3>التهديدات</h3>
                        <div class="metric-value" id="dashboard-threats-total">0</div>
                        <div class="metric-label">إجمالي</div>
                    </div>
                    <div class="metric-card">
                        <h3>الطلبات</h3>
                        <div class="metric-value" id="dashboard-requests-total">0</div>
                        <div class="metric-label">إجمالي</div>
                    </div>
                    <div class="metric-card">
                        <h3>الجلسات</h3>
                        <div class="metric-value" id="dashboard-sessions-active">0</div>
                        <div class="metric-label">نشط</div>
                    </div>
                    <div class="metric-card">
                        <h3>الذاكرة</h3>
                        <div class="metric-value" id="dashboard-memory-usage">0%</div>
                        <div class="metric-label">استخدام</div>
                    </div>
                </div>
                <div class="dashboard-threats">
                    <h3>آخر التهديدات</h3>
                    <div id="dashboard-threats-list"></div>
                </div>
            `;
        }

        /**
         * توليد معرف فريد
         */
        generateId() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        }

        /**
         * تدمير لوحة التحكم
         */
        destroy() {
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
            }
            this.isActive = false;
            console.log('🗑️ Dashboard destroyed');
        }

        /**
         * تصدير البيانات
         */
        exportData() {
            return {
                version: this.version,
                timestamp: Date.now(),
                metrics: this.metrics,
                stats: this.getSecurityStats()
            };
        }
    }

    // Export to global scope
    window.Dashboard = Dashboard;
    
    // Auto-initialize
    window.dashboard = new Dashboard();
    console.log('📊 Dashboard fortress loaded and ready');

})(window);