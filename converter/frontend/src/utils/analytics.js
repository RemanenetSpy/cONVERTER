// Google Analytics helper functions
export const initGA = (measurementId) => {
    // Load GA script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);

    // Initialize GA
    window.dataLayer = window.dataLayer || [];
    function gtag() {
        window.dataLayer.push(arguments);
    }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', measurementId);
};

// Track page views
export const trackPageView = (path) => {
    if (window.gtag) {
        window.gtag('config', process.env.REACT_APP_GA_MEASUREMENT_ID, {
            page_path: path,
        });
    }
};

// Track conversion events
export const trackConversion = (inputFormat, outputFormat, fileSize) => {
    if (window.gtag) {
        window.gtag('event', 'conversion', {
            event_category: 'File Conversion',
            event_label: `${inputFormat} to ${outputFormat}`,
            value: Math.round(fileSize / 1024), // KB
        });
    }
};

// Track download
export const trackDownload = (filename) => {
    if (window.gtag) {
        window.gtag('event', 'download', {
            event_category: 'File Download',
            event_label: filename,
        });
    }
};

// Track feedback submission
export const trackFeedback = (type) => {
    if (window.gtag) {
        window.gtag('event', 'feedback_submit', {
            event_category: 'User Feedback',
            event_label: type,
        });
    }
};
