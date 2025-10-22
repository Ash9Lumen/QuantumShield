chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.message === "check_url") {
        let url = window.location.href;

        // Check if the alert for this URL has already been shown in this session
        if (!sessionStorage.getItem(url)) {
            fetch('http://127.0.0.1:5000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_phishing) {
                    window.stop(); // Immediately stop navigation
                    sessionStorage.setItem(url, true); // Store the URL in sessionStorage to prevent repeated alerts
                    disableScroll(); // Disable scroll when alert is triggered
                    injectExternalCSS(); // Inject external CSS file before showing modal
                    showPhishingAlert(url); // Show custom alert
                } else {
                    console.log("This URL is safe.");
                }
            })
            .catch(error => {
                console.error(`Error checking URL ${url}:`, error);
            });
            console.log("Phishing check triggered.");
            sendResponse({ status: "received" });
        } else {
            console.log("Alert for this URL has already been shown.");
        }
    } else {
        sendResponse({ status: "unknown request" });
    }
});

// Function to inject external CSS for the modal
function injectExternalCSS() {
    let link = document.createElement('link');
    link.href = chrome.runtime.getURL('styles/style.css');
    link.type = 'text/css';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
}

// Function to show the phishing alert modal
function showPhishingAlert(url) {
    let modal = document.createElement('div');
    modal.id = 'phishing-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <p><strong>WARNING:</strong> This URL has the potential to be PHISHING! Are you sure you want to visit ${url}?</p>
            <button id="phishing-yes">Yes</button>
            <button id="phishing-no">No</button>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('phishing-yes').onclick = function () {
        sessionStorage.removeItem(url); // Clear sessionStorage for the URL so it can trigger again when switching tabs
        document.body.removeChild(modal); // Remove modal if Yes is clicked
        enableScroll(); // Re-enable scroll
        console.log("User chose to proceed to the phishing URL.");
    };

    document.getElementById('phishing-no').onclick = function () {
        window.location.href = chrome.runtime.getURL('Blocked.html'); // Redirect if No is clicked
        document.body.removeChild(modal); // Remove modal
        enableScroll(); // Re-enable scroll
    };
}

// Function to disable page scrolling
function disableScroll() {
    document.body.style.overflow = 'hidden';
}

// Function to re-enable page scrolling
function enableScroll() {
    document.body.style.overflow = '';
}

// Clear the sessionStorage when navigating away from the page (helps in refreshing the alert when revisiting)
window.addEventListener('beforeunload', function () {
    let url = window.location.href;
    sessionStorage.removeItem(url); // Clear the entry for the current URL in sessionStorage when navigating away
});
