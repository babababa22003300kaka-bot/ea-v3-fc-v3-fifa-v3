// Fort Knox Digital Identity - Service Worker Phase 2
// ===================================================
// 🏰 خدمة العمل في الخلفية للنظام المتقدم
// ===================================================

const CACHE_NAME = 'fort-knox-v2.1.0';
const FORTRESS_CACHE = 'fortress-static-v2';
const DYNAMIC_CACHE = 'fort-knox-dynamic-v2';

// الملفات الأساسية للتخزين المؤقت
const CORE_ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/CryptoEngineFortress.js',
    '/static/js/SilentIdentityFortress.js',
    '/static/js/FC26_Integration_Bridge.js',
    '/static/js/script.js',
    '/static/manifest.json'
];

// الملفات الاختيارية
const OPTIONAL_ASSETS = [
    '/dashboard',
    '/api/identity/session'
];

// 🚀 تثبيت Service Worker
self.addEventListener('install', event => {
    console.log('🏰 Fort Knox Service Worker - Installing...');
    
    event.waitUntil(
        caches.open(FORTRESS_CACHE)
            .then(cache => {
                console.log('📦 Caching core fortress assets...');
                return cache.addAll(CORE_ASSETS);
            })
            .then(() => {
                console.log('✅ Fort Knox Service Worker installed successfully!');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('❌ Service Worker installation failed:', error);
            })
    );
});

// 🔄 تفعيل Service Worker
self.addEventListener('activate', event => {
    console.log('🔥 Fort Knox Service Worker - Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cache => {
                        // حذف الكاش القديم
                        if (cache !== FORTRESS_CACHE && cache !== DYNAMIC_CACHE) {
                            console.log('🗑️ Deleting old cache:', cache);
                            return caches.delete(cache);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Fort Knox Service Worker activated!');
                return self.clients.claim();
            })
    );
});

// 🌐 اعتراض الطلبات
self.addEventListener('fetch', event => {
    const request = event.request;
    const url = new URL(request.url);
    
    // تجاهل الطلبات الخارجية وطلبات Chrome Extensions
    if (!url.origin.includes(self.location.origin) || 
        url.protocol === 'chrome-extension:' ||
        url.protocol === 'moz-extension:') {
        return;
    }
    
    // استراتيجية Cache First للملفات الثابتة
    if (request.destination === 'script' || 
        request.destination === 'style' ||
        request.url.includes('/static/')) {
        
        event.respondWith(
            caches.match(request)
                .then(response => {
                    if (response) {
                        console.log('📦 Serving from cache:', request.url);
                        return response;
                    }
                    
                    return fetch(request)
                        .then(fetchResponse => {
                            // حفظ في الكاش للمرة القادمة
                            if (fetchResponse.status === 200) {
                                const responseClone = fetchResponse.clone();
                                caches.open(FORTRESS_CACHE)
                                    .then(cache => {
                                        cache.put(request, responseClone);
                                    });
                            }
                            return fetchResponse;
                        });
                })
                .catch(() => {
                    console.log('📱 Offline mode - serving cached version');
                    return caches.match('/');
                })
        );
    }
    
    // استراتيجية Network First للطلبات الديناميكية
    else if (request.url.includes('/api/') || request.method === 'POST') {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // حفظ الاستجابات الناجحة في الكاش الديناميكي
                    if (response.status === 200 && request.method === 'GET') {
                        const responseClone = response.clone();
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(request, responseClone);
                            });
                    }
                    return response;
                })
                .catch(() => {
                    console.log('🔌 Network failed, trying cache...');
                    return caches.match(request)
                        .then(cachedResponse => {
                            if (cachedResponse) {
                                return cachedResponse;
                            }
                            
                            // إرجاع استجابة افتراضية للـ API
                            if (request.url.includes('/api/')) {
                                return new Response(
                                    JSON.stringify({
                                        offline: true,
                                        message: 'النظام يعمل في وضع عدم الاتصال',
                                        timestamp: new Date().toISOString()
                                    }),
                                    {
                                        status: 200,
                                        headers: { 'Content-Type': 'application/json' }
                                    }
                                );
                            }
                            
                            throw new Error('No cached response available');
                        });
                })
        );
    }
    
    // الطلبات العادية - محاولة الشبكة أولاً ثم الكاش
    else {
        event.respondWith(
            fetch(request)
                .catch(() => {
                    return caches.match(request)
                        .then(response => {
                            return response || caches.match('/');
                        });
                })
        );
    }
});

// 🔔 استقبال الرسائل من التطبيق الرئيسي
self.addEventListener('message', event => {
    console.log('📨 Service Worker received message:', event.data);
    
    if (event.data && event.data.type) {
        switch (event.data.type) {
            case 'SKIP_WAITING':
                self.skipWaiting();
                break;
                
            case 'CACHE_UPDATE':
                // تحديث الكاش يدوياً
                caches.open(FORTRESS_CACHE)
                    .then(cache => {
                        return cache.addAll(CORE_ASSETS);
                    })
                    .then(() => {
                        event.ports[0].postMessage({ success: true });
                    })
                    .catch(error => {
                        event.ports[0].postMessage({ success: false, error: error.message });
                    });
                break;
                
            case 'CLEAR_CACHE':
                // مسح الكاش
                caches.keys()
                    .then(cacheNames => {
                        return Promise.all(
                            cacheNames.map(cache => caches.delete(cache))
                        );
                    })
                    .then(() => {
                        event.ports[0].postMessage({ cleared: true });
                    });
                break;
                
            case 'FORTRESS_STATUS':
                // إرسال حالة النظام
                event.ports[0].postMessage({
                    status: 'active',
                    version: '2.1.0',
                    caches: [FORTRESS_CACHE, DYNAMIC_CACHE],
                    timestamp: new Date().toISOString()
                });
                break;
        }
    }
});

// 🚨 معالجة الأخطاء
self.addEventListener('error', event => {
    console.error('🚨 Service Worker Error:', event.error);
});

// 🔄 مزامنة الخلفية
self.addEventListener('sync', event => {
    console.log('🔄 Background sync triggered:', event.tag);
    
    if (event.tag === 'fortress-identity-sync') {
        event.waitUntil(
            // مزامنة بيانات الهوية الصامتة
            syncIdentityData()
        );
    }
});

// 🔔 معالجة الإشعارات Push
self.addEventListener('push', event => {
    console.log('🔔 Push notification received');
    
    const options = {
        body: 'تحديث أمني من Fort Knox',
        icon: '/static/icon-192.png',
        badge: '/static/badge-72.png',
        tag: 'fort-knox-security',
        requireInteraction: true,
        actions: [
            {
                action: 'view',
                title: 'عرض التفاصيل'
            },
            {
                action: 'dismiss',
                title: 'إغلاق'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Fort Knox Security Alert', options)
    );
});

// 🎯 نقر على الإشعار
self.addEventListener('notificationclick', event => {
    console.log('🎯 Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// 📊 دالة مزامنة بيانات الهوية
async function syncIdentityData() {
    try {
        console.log('🔄 Syncing fortress identity data...');
        
        // محاكاة مزامنة البيانات
        const response = await fetch('/api/identity/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                timestamp: new Date().toISOString(),
                source: 'service-worker'
            })
        });
        
        if (response.ok) {
            console.log('✅ Identity sync completed successfully');
        } else {
            console.log('⚠️ Identity sync failed, will retry later');
        }
        
    } catch (error) {
        console.error('❌ Identity sync error:', error);
    }
}

// 🎉 تحديد نجاح التثبيت
console.log('🏰 Fort Knox Service Worker Phase 2 - Loaded and Ready!');
console.log('🔐 Military-grade offline support activated');
console.log('📱 Progressive Web App features enabled');