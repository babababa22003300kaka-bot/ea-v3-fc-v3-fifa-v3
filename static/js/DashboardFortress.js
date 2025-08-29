// DashboardFortress.js - قلعة لوحة التحكم المعزولة تماماً
/**
 * 🏰 قلعة لوحة التحكم - FC 26 Dashboard System
 * ============================================
 * نظام IIFE معزول تماماً لإدارة لوحة التحكم
 * - معزول تماماً عن النظام الرئيسي
 * - إدارة البيانات والإحصائيات
 * - واجهة تفاعلية للأدمن والمستخدمين
 * - تحديث تلقائي للبيانات
 */

(function DashboardFortressIIFE() {
    'use strict';

    // ============================================================================
    // 🛡️ حارس القلعة - منع الوصول غير المصرح
    // ============================================================================
    const FORTRESS_CONFIG = {
        NAME: 'DashboardFortress',
        VERSION: '1.0.0',
        SECURITY_LEVEL: 'MAXIMUM',
        AUTO_REFRESH: true,
        REFRESH_INTERVAL: 30000, // 30 ثانية
        MAX_RETRIES: 3,
        DEBUG: false
    };

    // ============================================================================
    // 📊 مدير البيانات المعزول
    // ============================================================================
    class DashboardDataManager {
        constructor() {
            this.data = {
                users_analytics: null,
                telegram_analytics: null,
                system_health: null,
                recent_activity: null,
                last_updated: null
            };
            this.loading = false;
            this.error = null;
            this.retryCount = 0;
        }

        async fetchDashboardData() {
            if (this.loading) {
                console.log('🏰 البيانات قيد التحميل...');
                return false;
            }

            this.loading = true;
            this.error = null;

            try {
                const response = await fetch('/api/dashboard-data', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP Error: ${response.status}`);
                }

                const result = await response.json();

                if (result.success) {
                    this.data = result.dashboard_data;
                    this.data.last_updated = new Date().toISOString();
                    this.retryCount = 0;

                    this.log('تم تحديث البيانات بنجاح');
                    return true;
                } else {
                    throw new Error(result.error || 'فشل في جلب البيانات');
                }

            } catch (error) {
                this.error = error.message;
                this.retryCount++;

                this.log(`خطأ في جلب البيانات: ${error.message}`, 'error');

                // إعادة المحاولة إذا لم نصل للحد الأقصى
                if (this.retryCount < FORTRESS_CONFIG.MAX_RETRIES) {
                    setTimeout(() => this.fetchDashboardData(), 5000);
                }

                return false;
            } finally {
                this.loading = false;
            }
        }

        getData() {
            return this.data;
        }

        getError() {
            return this.error;
        }

        isLoading() {
            return this.loading;
        }

        log(message, level = 'info') {
            if (FORTRESS_CONFIG.DEBUG) {
                console.log(`🏰 [${FORTRESS_CONFIG.NAME}] ${message}`);
            }
        }
    }

    // ============================================================================
    // 🎨 مدير الواجهة المعزول
    // ============================================================================
    class DashboardUIManager {
        constructor(dataManager) {
            this.dataManager = dataManager;
            this.elements = {};
            this.charts = {};
            this.initialized = false;
        }

        init() {
            if (this.initialized) return;

            this.cacheElements();
            this.setupEventListeners();
            this.setupAutoRefresh();
            this.initialized = true;

            console.log('🏰 تم تهيئة واجهة لوحة التحكم');
        }

        cacheElements() {
            this.elements = {
                // الحاويات الرئيسية
                dashboardContainer: document.getElementById('dashboardContainer'),
                loadingIndicator: document.getElementById('dashboardLoading'),
                errorContainer: document.getElementById('dashboardError'),

                // بطاقات الإحصائيات
                totalUsersCard: document.getElementById('totalUsersCard'),
                platformsChart: document.getElementById('platformsChart'),
                paymentMethodsChart: document.getElementById('paymentMethodsChart'),
                telegramStatsCard: document.getElementById('telegramStatsCard'),

                // النشاطات الأخيرة
                activityList: document.getElementById('activityList'),
                systemHealthCard: document.getElementById('systemHealthCard'),

                // أزرار التحكم
                refreshBtn: document.getElementById('refreshDashboardBtn'),
                exportBtn: document.getElementById('exportDataBtn')
            };
        }

        setupEventListeners() {
            if (this.elements.refreshBtn) {
                this.elements.refreshBtn.addEventListener('click', () => {
                    this.refreshData();
                });
            }

            if (this.elements.exportBtn) {
                this.elements.exportBtn.addEventListener('click', () => {
                    this.exportData();
                });
            }
        }

        setupAutoRefresh() {
            if (FORTRESS_CONFIG.AUTO_REFRESH) {
                setInterval(() => {
                    if (!this.dataManager.isLoading()) {
                        this.dataManager.fetchDashboardData().then(success => {
                            if (success) {
                                this.updateUI();
                            }
                        });
                    }
                }, FORTRESS_CONFIG.REFRESH_INTERVAL);
            }
        }

        async refreshData() {
            this.showLoading();
            const success = await this.dataManager.fetchDashboardData();

            if (success) {
                this.updateUI();
                this.showSuccessMessage('تم تحديث البيانات');
            } else {
                this.showError(this.dataManager.getError());
            }
        }

        updateUI() {
            const data = this.dataManager.getData();

            if (!data) return;

            try {
                this.updateUsersAnalytics(data.users_analytics);
                this.updateTelegramAnalytics(data.telegram_analytics);
                this.updateSystemHealth(data.system_health);
                this.updateRecentActivity(data.recent_activity);
                this.updateLastUpdated(data.last_updated);

                this.hideLoading();
                this.hideError();

            } catch (error) {
                console.error('خطأ في تحديث الواجهة:', error);
                this.showError('خطأ في عرض البيانات');
            }
        }

        updateUsersAnalytics(analytics) {
            if (!analytics || !analytics.success) return;

            const data = analytics.analytics;

            // إجمالي المستخدمين
            if (this.elements.totalUsersCard) {
                this.elements.totalUsersCard.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-icon">👥</div>
                        <div class="stat-info">
                            <div class="stat-number">${data.total_users}</div>
                            <div class="stat-label">إجمالي المستخدمين</div>
                        </div>
                    </div>
                `;
            }

            // رسم بياني للمنصات
            this.createPlatformsChart(data.platforms_breakdown);

            // رسم بياني لطرق الدفع
            this.createPaymentMethodsChart(data.payment_methods_breakdown);
        }

        createPlatformsChart(platformsData) {
            if (!this.elements.platformsChart) return;

            const chartHTML = Object.entries(platformsData).map(([platform, count]) => {
                const percentage = (count / Object.values(platformsData).reduce((a, b) => a + b, 0) * 100).toFixed(1);
                return `
                    <div class="chart-item">
                        <div class="chart-label">${this.getPlatformName(platform)}</div>
                        <div class="chart-bar">
                            <div class="chart-fill" style="width: ${percentage}%"></div>
                        </div>
                        <div class="chart-value">${count} (${percentage}%)</div>
                    </div>
                `;
            }).join('');

            this.elements.platformsChart.innerHTML = `
                <h3>توزيع المنصات</h3>
                <div class="chart-container">${chartHTML}</div>
            `;
        }

        createPaymentMethodsChart(paymentData) {
            if (!this.elements.paymentMethodsChart) return;

            const chartHTML = Object.entries(paymentData).map(([method, count]) => {
                const percentage = (count / Object.values(paymentData).reduce((a, b) => a + b, 0) * 100).toFixed(1);
                return `
                    <div class="chart-item">
                        <div class="chart-label">${this.getPaymentMethodName(method)}</div>
                        <div class="chart-bar">
                            <div class="chart-fill payment-${method}" style="width: ${percentage}%"></div>
                        </div>
                        <div class="chart-value">${count} (${percentage}%)</div>
                    </div>
                `;
            }).join('');

            this.elements.paymentMethodsChart.innerHTML = `
                <h3>طرق الدفع</h3>
                <div class="chart-container">${chartHTML}</div>
            `;
        }

        updateTelegramAnalytics(telegramData) {
            if (!telegramData || !telegramData.success) return;

            const data = telegramData.telegram_analytics;

            if (this.elements.telegramStatsCard) {
                this.elements.telegramStatsCard.innerHTML = `
                    <div class="telegram-stats">
                        <h3>📱 إحصائيات التليجرام</h3>
                        <div class="stat-grid">
                            <div class="stat-item">
                                <div class="stat-value">${data.total_codes}</div>
                                <div class="stat-label">أكواد التفعيل</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">@${data.bot_username}</div>
                                <div class="stat-label">اسم البوت</div>
                            </div>
                        </div>
                    </div>
                `;
            }
        }

        updateSystemHealth(healthData) {
            if (!healthData || !healthData.success) return;

            const health = healthData.health;

            if (this.elements.systemHealthCard) {
                this.elements.systemHealthCard.innerHTML = `
                    <div class="system-health">
                        <h3>⚡ صحة النظام</h3>
                        <div class="health-indicators">
                            <div class="health-item ${health.ministry_status}">
                                <span class="health-icon">🏰</span>
                                <span class="health-label">وزارة لوحة التحكم</span>
                                <span class="health-status">${health.ministry_status}</span>
                            </div>
                            <div class="health-item ${health.components.profile_handler}">
                                <span class="health-icon">👤</span>
                                <span class="health-label">إدارة الملفات</span>
                                <span class="health-status">${health.components.profile_handler}</span>
                            </div>
                            <div class="health-item ${health.components.telegram_manager}">
                                <span class="health-icon">📱</span>
                                <span class="health-label">إدارة التليجرام</span>
                                <span class="health-status">${health.components.telegram_manager}</span>
                            </div>
                        </div>
                        <div class="uptime">
                            <span>مدة التشغيل: ${health.uptime}</span>
                        </div>
                    </div>
                `;
            }
        }

        updateRecentActivity(activityData) {
            if (!activityData || !activityData.success) return;

            const activities = activityData.activities;

            if (this.elements.activityList) {
                const activitiesHTML = activities.slice(0, 10).map(activity => `
                    <div class="activity-item ${activity.level.toLowerCase()}">
                        <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                        <div class="activity-source">${activity.source}</div>
                        <div class="activity-text">${activity.activity}</div>
                    </div>
                `).join('');

                this.elements.activityList.innerHTML = `
                    <h3>📋 النشاطات الأخيرة</h3>
                    <div class="activities-container">${activitiesHTML}</div>
                `;
            }
        }

        updateLastUpdated(timestamp) {
            if (!timestamp) return;

            const updateElements = document.querySelectorAll('.last-updated');
            updateElements.forEach(element => {
                element.textContent = `آخر تحديث: ${this.formatTime(timestamp)}`;
            });
        }

        showLoading() {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'block';
            }
        }

        hideLoading() {
            if (this.elements.loadingIndicator) {
                this.elements.loadingIndicator.style.display = 'none';
            }
        }

        showError(message) {
            if (this.elements.errorContainer) {
                this.elements.errorContainer.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>${message}</span>
                    </div>
                `;
                this.elements.errorContainer.style.display = 'block';
            }
        }

        hideError() {
            if (this.elements.errorContainer) {
                this.elements.errorContainer.style.display = 'none';
            }
        }

        showSuccessMessage(message) {
            // إنشاء رسالة نجاح مؤقتة
            const successDiv = document.createElement('div');
            successDiv.className = 'success-notification';
            successDiv.innerHTML = `
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            `;

            document.body.appendChild(successDiv);

            setTimeout(() => {
                successDiv.remove();
            }, 3000);
        }

        async exportData() {
            try {
                const response = await fetch('/api/dashboard-export', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `fc26_dashboard_${new Date().getTime()}.json`;
                    a.click();

                    this.showSuccessMessage('تم تصدير البيانات بنجاح');
                } else {
                    throw new Error('فشل في تصدير البيانات');
                }

            } catch (error) {
                this.showError('خطأ في تصدير البيانات: ' + error.message);
            }
        }

        // دوال مساعدة
        getPlatformName(platform) {
            const names = {
                'playstation': 'PlayStation',
                'xbox': 'Xbox',
                'pc': 'PC',
                'غير محدد': 'غير محدد'
            };
            return names[platform] || platform;
        }

        getPaymentMethodName(method) {
            const names = {
                'vodafone_cash': 'فودافون كاش',
                'etisalat_cash': 'اتصالات كاش',
                'orange_cash': 'أورانج كاش',
                'we_cash': 'وي كاش',
                'bank_wallet': 'محفظة بنكية',
                'tilda': 'تيلدا',
                'instapay': 'إنستا باي'
            };
            return names[method] || method;
        }

        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString('ar-EG', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    // ============================================================================
    // 🚀 تهيئة وإطلاق القلعة
    // ============================================================================

    // إنشاء مدير البيانات
    const dataManager = new DashboardDataManager();

    // إنشاء مدير الواجهة
    const uiManager = new DashboardUIManager(dataManager);

    // تهيئة القلعة عند تحميل DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFortress);
    } else {
        initializeFortress();
    }

    async function initializeFortress() {
        console.log(`🏰 بدء تهيئة ${FORTRESS_CONFIG.NAME} v${FORTRESS_CONFIG.VERSION}`);

        // تهيئة مدير الواجهة
        uiManager.init();

        // تحميل البيانات الأولية
        uiManager.showLoading();
        const success = await dataManager.fetchDashboardData();

        if (success) {
            uiManager.updateUI();
            console.log('🏰 تم تهيئة لوحة التحكم بنجاح');
        } else {
            uiManager.showError('فشل في تحميل البيانات الأولية');
            console.error('🏰 فشل في تهيئة لوحة التحكم');
        }
    }

    // تصدير واجهة محدودة للنافذة العامة (إذا احتاج الأمر)
    window.DashboardFortress = {
        version: FORTRESS_CONFIG.VERSION,
        refresh: () => uiManager.refreshData(),
        export: () => uiManager.exportData(),
        getData: () => dataManager.getData()
    };

    console.log(`🏰 ${FORTRESS_CONFIG.NAME} v${FORTRESS_CONFIG.VERSION} محمل ومحمي`);

})(); // نهاية IIFE المعزول
