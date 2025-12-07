// Format Icons and Utilities
export const formatIcons = {
    // Images
    jpg: '🖼️',
    jpeg: '🖼️',
    png: '🖼️',
    webp: '🖼️',
    gif: '🎞️',
    bmp: '🖼️',
    tiff: '🖼️',
    svg: '🎨',
    heic: '📸',

    // Documents
    pdf: '📄',
    docx: '📝',
    doc: '📝',
    xlsx: '📊',
    xls: '📊',
    csv: '📋',
    json: '📋',
    parquet: '📊',
    pptx: '📽️',
    ppt: '📽️',

    // Audio
    mp3: '🎵',
    wav: '🎵',
    aac: '🎵',
    ogg: '🎵',
    m4a: '🎵',
    flac: '🎵',

    // Archives
    zip: '📦',
    '7z': '📦',
    tar: '📦',

    // Default
    default: '📁'
};

export const getFormatIcon = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    return formatIcons[ext] || formatIcons.default;
};

export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export const getFormatColor = (format) => {
    const colors = {
        // Images - Purple/Pink
        jpg: '#f093fb', jpeg: '#f093fb', png: '#f093fb', webp: '#f093fb',
        gif: '#f5576c', svg: '#4facfe', heic: '#43e97b',

        // Documents - Blue
        pdf: '#667eea', docx: '#764ba2', xlsx: '#38f9d7',
        csv: '#43e97b', json: '#fa709a',

        // Audio - Orange/Yellow
        mp3: '#f6d365', wav: '#fda085', aac: '#f093fb',

        // Archives - Gray
        zip: '#a8edea', '7z': '#fed6e3', tar: '#c2e9fb'
    };
    return colors[format] || '#667eea';
};
