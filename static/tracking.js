// static/tracking.js

// --- Cookie Utilities ---
function setCookie(name, value, days = 365) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/;SameSite=Lax`;
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// --- Session Management ---
function getSessionId() {
    let sessionId = getCookie('user_session_id');
    if (!sessionId) {
        sessionId = self.crypto.randomUUID();
        setCookie('user_session_id', sessionId);
    }
    return sessionId;
}

// --- IP Address Detection ---
async function getClientIP() {
    try {
        // Try to get IP from a public IP service
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        console.log('Could not fetch external IP, using fallback method');
        // Fallback: try to get IP from the server
        try {
            const response = await fetch('/api/client-ip');
            const data = await response.json();
            return data.ip;
        } catch (fallbackError) {
            console.log('Could not get IP address:', fallbackError);
            return 'Unknown';
        }
    }
}

// --- Device Info ---
function getDeviceInfo() {
    const ua = navigator.userAgent;
    let os = 'Unknown OS';
    let model = 'Unknown Model';

    // OS detection
    if (/Windows/.test(ua)) os = 'Windows';
    else if (/Mac OS X/.test(ua)) os = 'macOS';
    else if (/Android/.test(ua)) os = 'Android';
    else if (/iOS/.test(ua)) os = 'iOS';
    else if (/Linux/.test(ua)) os = 'Linux';

    // Model detection (simplified)
    const androidModel = ua.match(/Android\s([^;]+)/);
    if (androidModel) model = androidModel[1];

    const iOSModel = ua.match(/\((iPhone|iPad|iPod)/);
    if (iOSModel) model = iOSModel[1];

    if (os === 'Windows' || os === 'macOS' || os === 'Linux') {
        model = 'Desktop';
    }

    return { os, model };
}

// --- Tracking ---
let sessionStartTime = Date.now();
let clientIP = 'Unknown';

// Initialize IP address
async function initializeTracking() {
    clientIP = await getClientIP();
}

function trackEvent(eventName, eventData = {}) {
    const payload = {
        sessionId: getSessionId(),
        deviceInfo: getDeviceInfo(),
        ip: clientIP,
        eventName: eventName,
        eventData: {
            ...eventData,
            url: window.location.pathname,
            timestamp: Date.now() // Use milliseconds timestamp for better precision
        }
    };

    fetch('/api/track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies in the request
        body: JSON.stringify(payload),
        keepalive: true // This is important for requests sent during page unload
    }).catch(error => {
        console.error('Tracking Error:', error);
    });
}

function trackPageView() {
    trackEvent('pageView', { 
        page: getCurrentPage(),
        url: window.location.pathname 
    });
}

function getCurrentPage() {
    // Extract page number from URL or use current path
    const path = window.location.pathname;
    if (path.includes('/quiz/page/')) {
        const match = path.match(/\/quiz\/page\/(\d+)/);
        return match ? match[1] : 'home';
    }
    return path === '/' ? 'home' : path.replace('/', '');
}

function trackTimeSpent() {
    const timeSpent = Math.round((Date.now() - sessionStartTime) / 1000);
    trackEvent('timeSpent', { duration: timeSpent });
}

function trackQuizProgress(questionId, isCorrect) {
    trackEvent('quizAnswer', { questionId, isCorrect });
}

function trackQuizPageNavigation(fromPage, toPage) {
    trackEvent('quizPageNavigation', { fromPage, toPage });
}

function trackQuizAnswer(questionId, selectedAnswer, isCorrect, page) {
    trackEvent('quizAnswer', { 
        questionId, 
        selectedAnswer, 
        isCorrect, 
        page: page || getCurrentPage() 
    });
}

function trackQuizSearch(searchTerm, page) {
    trackEvent('quizSearch', { 
        searchTerm, 
        page: page || getCurrentPage() 
    });
}

function trackQuizQuestionView(questionId, page) {
    trackEvent('questionView', { 
        questionId, 
        page: page || getCurrentPage() 
    });
}

// --- Initialization ---
async function initTracking() {
    await initializeTracking();
    const sessionId = getSessionId();
    const deviceInfo = getDeviceInfo();

    // Initial tracking call
    trackPageView();

    // Set up recurring tracking
    setInterval(trackTimeSpent, 15000); // Track time every 15 seconds
    
    // Track page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            trackEvent('pageHidden', { page: getCurrentPage() });
        } else {
            trackEvent('pageVisible', { page: getCurrentPage() });
        }
    });
    
    // Track before page unload
    window.addEventListener('beforeunload', function() {
        trackEvent('pageUnload', { page: getCurrentPage() });
    });
    
    // Track page focus/blur
    window.addEventListener('focus', function() {
        trackEvent('pageFocus', { page: getCurrentPage() });
    });
    
    window.addEventListener('blur', function() {
        trackEvent('pageBlur', { page: getCurrentPage() });
    });
}

// Start tracking when the script is loaded
initTracking();