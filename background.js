function checkForPhishing() {
    if (typeof chrome.tabs !== 'undefined' && chrome.tabs.query) {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            let activeTab = tabs[0];
            
            // Ensure the active tab has a valid URL
            if (activeTab && activeTab.url && 
                !activeTab.url.startsWith('chrome://') && 
                !activeTab.url.startsWith('about:') && 
                !activeTab.url.startsWith('chrome-extension://')) {
                
                chrome.tabs.sendMessage(activeTab.id, {"message": "check_url"});
            } else {
                console.log("Invalid URL, skipping phishing check:", activeTab ? activeTab.url : "No active tab");
            }
        });
    } else {
        console.log("checkForPhishing function is being executed in an incorrect context.");
    }
}

// Add a health-check mechanism to keep the extension alive
function keepAlive() {
    chrome.runtime.sendMessage({check: "active"}, function(response) {
        if (!response || response.status !== "active") {
            console.log("Extension appears inactive, reactivating...");
            
        }
    });
}

// Set the interval in seconds
const shortInterval = 25; // seconds

// Set up periodic checks using alarms API (for Manifest v3)
chrome.alarms.create('keepAlive', { periodInMinutes: 1 });

// Listen for the alarm to recheck the extension state
chrome.alarms.onAlarm.addListener(alarm => {
    if (alarm.name === 'keepAlive') {
        console.log("Running keepAlive check...");
        keepAlive(); // Run the health check
    }
});

// Use setInterval to run keepAlive every 45 seconds
setInterval(() => {
    console.log("Running keepAlive check...");
    keepAlive(); // Run the keep-alive check
}, shortInterval * 1000); // Convert to milliseconds

// Attach listeners to the correct events
chrome.runtime.onStartup.addListener(() => {
    console.log("Extension started up");
});

chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed");
});

chrome.tabs.onActivated.addListener(activeInfo => {
    chrome.tabs.get(activeInfo.tabId, function(tab) {
        if (tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('about:')) {
            checkForPhishing();  // Execute the function directly
        }
    });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('about:')) {
        checkForPhishing();  // Execute the function directly
    }
});
