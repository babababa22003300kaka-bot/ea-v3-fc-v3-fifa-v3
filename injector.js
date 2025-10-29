// injector.js - Intercepts fetch requests to updateSenderPage

(() => {
    console.log("🚀 [INJECTOR] Script injected!");

    // Save original fetch
    const originalFetch = window.fetch;

    // Override fetch
    window.fetch = async (...args) => {
        const url = args[0];

        // Check if this is updateSenderPage request
        if (typeof url === 'string' && url.includes('updateSenderPage')) {
            console.log(`[INJECTOR] ✅ Intercepted: ${url}`);

            // Let request pass through
            const response = await originalFetch(...args);

            // Clone response to read it
            const clonedResponse = response.clone();

            // Read data and send to Python
            clonedResponse.json().then(data => {
                console.log(`[INJECTOR] 📊 Data captured (${data?.data?.length || 0} accounts)`);

                // Call Python function (exposed via Playwright)
                if (window.onDataUpdate) {
                    window.onDataUpdate(data);
                } else {
                    console.warn("[INJECTOR] ⚠️ onDataUpdate not found!");
                }
            }).catch(err => {
                console.error("[INJECTOR] ❌ Error reading response:", err);
            });

            // Return original response (website continues normally)
            return response;
        }

        // Other requests: pass through
        return await originalFetch(...args);
    };

    console.log("✅ [INJECTOR] Fetch patched! Listening for updates...");
})();
