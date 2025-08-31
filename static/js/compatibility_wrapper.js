/**
 * 🔧 Compatibility Wrapper - جسر التوافق
 * يربط بين الأسماء القديمة والجديدة للمكونات
 */

(function(window) {
    'use strict';
    
    console.log('🔧 Initializing compatibility wrapper...');
    
    // Wait for components to load
    window.addEventListener('DOMContentLoaded', function() {
        
        // CryptoEngine compatibility
        if (window.cryptoEngine && !window.CryptoFortressAPI) {
            window.CryptoFortressAPI = {
                encrypt: window.cryptoEngine.encrypt.bind(window.cryptoEngine),
                decrypt: window.cryptoEngine.decrypt.bind(window.cryptoEngine),
                hash: async (data) => {
                    // Simulate hash function using encrypt
                    const result = await window.cryptoEngine.encrypt(data, 'hash-key');
                    return result ? result.substring(0, 64) : null;
                },
                generateKey: window.cryptoEngine.generateSalt.bind(window.cryptoEngine),
                initialized: window.cryptoEngine.initialized
            };
            console.log('✅ CryptoFortressAPI compatibility layer created');
        }
        
        // SilentIdentity compatibility
        if (window.silentIdentity && !window.SilentIdentityAPI) {
            window.SilentIdentityAPI = {
                getCurrentIdentity: window.silentIdentity.getCurrentIdentity.bind(window.silentIdentity),
                generateIdentity: window.silentIdentity.generateIdentity.bind(window.silentIdentity),
                validateIdentity: window.silentIdentity.validateIdentity.bind(window.silentIdentity),
                getDeviceFingerprint: window.silentIdentity.getDeviceFingerprint.bind(window.silentIdentity),
                getTrustScore: window.silentIdentity.getTrustScore.bind(window.silentIdentity)
            };
            console.log('✅ SilentIdentityAPI compatibility layer created');
        }
        
        // Dashboard compatibility
        if (window.securityDashboard && !window.DashboardFortressAPI) {
            window.DashboardFortressAPI = {
                init: window.securityDashboard.init ? window.securityDashboard.init.bind(window.securityDashboard) : () => {},
                updateMetrics: window.securityDashboard.updateMetrics ? window.securityDashboard.updateMetrics.bind(window.securityDashboard) : () => {},
                showAlert: window.securityDashboard.showAlert ? window.securityDashboard.showAlert.bind(window.securityDashboard) : () => {},
                logActivity: window.securityDashboard.logActivity ? window.securityDashboard.logActivity.bind(window.securityDashboard) : () => {}
            };
            console.log('✅ DashboardFortressAPI compatibility layer created');
        }
        
        // IntegrationBridge compatibility fix
        if (window.FC26IntegrationBridge) {
            // Add initialize method if it doesn't exist
            if (!window.FC26IntegrationBridge.initialize) {
                window.FC26IntegrationBridge.initialize = function() {
                    console.log('✅ IntegrationBridge initialize called (compatibility mode)');
                    // Bridge is already initialized automatically
                    return true;
                };
            }
        }
        
        console.log('✅ Compatibility wrapper initialized successfully');
    });
    
})(window);