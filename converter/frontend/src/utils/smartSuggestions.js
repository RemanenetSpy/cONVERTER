// Smart Format Suggestions (AI-powered)
export const formatSuggestions = {
    // Image suggestions based on use case
    jpg: {
        web: { format: 'webp', reason: '50% smaller, better for web' },
        print: { format: 'png', reason: 'Lossless quality for printing' },
        email: { format: 'jpg', reason: 'Compressed, universally supported', compress: true },
        social: { format: 'jpg', reason: 'Optimized for social media', maxDimension: 1920 }
    },
    jpeg: {
        web: { format: 'webp', reason: '50% smaller, better for web' },
        print: { format: 'png', reason: 'Lossless quality for printing' },
        email: { format: 'jpg', reason: 'Compressed, universally supported', compress: true }
    },
    png: {
        web: { format: 'webp', reason: '30% smaller with transparency' },
        print: { format: 'png', reason: 'Already optimal for print' },
        email: { format: 'jpg', reason: 'Smaller file size', compress: true }
    },
    svg: {
        web: { format: 'svg', reason: 'Scalable, perfect for web' },
        print: { format: 'png', reason: 'High resolution raster', maxDimension: 3000 },
        email: { format: 'png', reason: 'Better compatibility', maxDimension: 1200 }
    },

    // Document suggestions
    pdf: {
        edit: { format: 'docx', reason: 'Editable in Word' },
        data: { format: 'xlsx', reason: 'Extract tables to Excel' },
        archive: { format: 'pdf', reason: 'Already optimal', compress: true }
    },
    docx: {
        share: { format: 'pdf', reason: 'Universal compatibility' },
        web: { format: 'pdf', reason: 'Better for viewing online' },
        archive: { format: 'pdf', reason: 'Long-term storage' }
    },
    xlsx: {
        share: { format: 'pdf', reason: 'Preserve formatting' },
        data: { format: 'csv', reason: 'Universal data format' },
        api: { format: 'json', reason: 'Better for APIs' }
    },
    csv: {
        analysis: { format: 'xlsx', reason: 'Better for Excel analysis' },
        api: { format: 'json', reason: 'Modern data format' },
        archive: { format: 'parquet', reason: 'Compressed columnar storage' }
    },

    // Audio suggestions
    mp3: {
        quality: { format: 'wav', reason: 'Lossless audio quality' },
        podcast: { format: 'mp3', reason: 'Already optimal', bitrate: '128k' },
        archive: { format: 'flac', reason: 'Lossless compression' }
    },
    wav: {
        podcast: { format: 'mp3', reason: 'Smaller, good quality', bitrate: '192k' },
        music: { format: 'mp3', reason: 'Smaller, high quality', bitrate: '320k' },
        web: { format: 'mp3', reason: 'Better compatibility' }
    }
};

export const getSmartSuggestion = (filename, useCase = 'web') => {
    const ext = filename.split('.').pop().toLowerCase();
    const suggestions = formatSuggestions[ext];

    if (!suggestions) return null;

    return suggestions[useCase] || suggestions.web || suggestions.share || null;
};

// Conversion Templates
export const conversionTemplates = {
    socialMediaPack: {
        name: '📱 Social Media Pack',
        description: 'Convert 1 image to 5 optimized sizes for social platforms',
        input: ['jpg', 'jpeg', 'png'],
        outputs: [
            { format: 'jpg', width: 1200, height: 630, name: 'Facebook Post' },
            { format: 'jpg', width: 1080, height: 1080, name: 'Instagram Square' },
            { format: 'jpg', width: 1080, height: 1920, name: 'Instagram Story' },
            { format: 'jpg', width: 1500, height: 500, name: 'Twitter Header' },
            { format: 'jpg', width: 1200, height: 1200, name: 'LinkedIn Post' }
        ]
    },

    documentArchive: {
        name: '📁 Document Archive',
        description: 'Convert PDF to multiple editable formats',
        input: ['pdf'],
        outputs: [
            { format: 'docx', name: 'Word Document' },
            { format: 'xlsx', name: 'Excel Spreadsheet' },
            { format: 'txt', name: 'Plain Text' }
        ]
    },

    audioPodcast: {
        name: '🎙️ Podcast Package',
        description: 'Convert audio to podcast-ready formats',
        input: ['wav', 'mp3', 'm4a'],
        outputs: [
            { format: 'mp3', bitrate: '128k', name: 'Standard Quality' },
            { format: 'mp3', bitrate: '192k', name: 'High Quality' },
            { format: 'mp3', bitrate: '64k', name: 'Low Bandwidth' }
        ]
    },

    webOptimized: {
        name: '🌐 Web Optimized',
        description: 'Convert images for web with compression',
        input: ['jpg', 'jpeg', 'png', 'gif'],
        outputs: [
            { format: 'webp', quality: 80, name: 'WebP Modern' },
            { format: 'jpg', quality: 85, name: 'JPEG Fallback' },
            { format: 'jpg', quality: 60, maxDimension: 800, name: 'Thumbnail' }
        ]
    },

    printReady: {
        name: '🖨️ Print Ready',
        description: 'High-resolution formats for printing',
        input: ['jpg', 'jpeg', 'png'],
        outputs: [
            { format: 'png', name: 'Lossless PNG' },
            { format: 'tiff', name: 'TIFF High-Res' },
            { format: 'pdf', name: 'PDF Document' }
        ]
    }
};

export const getApplicableTemplates = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    return Object.entries(conversionTemplates)
        .filter(([_, template]) => template.input.includes(ext))
        .map(([key, template]) => ({ key, ...template }));
};

// Use case detector (simple AI)
export const detectUseCase = (filename, fileSize) => {
    const ext = filename.split('.').pop().toLowerCase();
    const sizeMB = fileSize / (1024 * 1024);

    // Image use case detection
    if (['jpg', 'jpeg', 'png', 'webp'].includes(ext)) {
        if (sizeMB > 5) return 'email'; // Large image, suggest compression
        if (filename.toLowerCase().includes('logo')) return 'web';
        if (filename.toLowerCase().includes('print')) return 'print';
        return 'web'; // Default
    }

    // Document use case detection
    if (ext === 'pdf') {
        if (sizeMB > 10) return 'archive'; // Large PDF, suggest compression
        if (filename.toLowerCase().includes('form')) return 'edit';
        if (filename.toLowerCase().includes('data')) return 'data';
        return 'share';
    }

    if (ext === 'docx') return 'share';
    if (ext === 'xlsx') return 'data';

    // Audio use case detection
    if (['wav', 'mp3'].includes(ext)) {
        if (filename.toLowerCase().includes('podcast')) return 'podcast';
        if (sizeMB > 20) return 'podcast'; // Large audio, compress
        return 'quality';
    }

    return 'web'; // Default
};
