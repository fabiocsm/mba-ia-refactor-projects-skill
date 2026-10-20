const LEVELS = Object.freeze({ debug: 10, info: 20, warn: 30, error: 40 });

function createLogger(level = 'info', stream = process.stdout) {
    const threshold = LEVELS[level] ?? LEVELS.info;
    const write = (name, message, meta = {}) => {
        if (LEVELS[name] < threshold) return;
        stream.write(`${JSON.stringify({ time: new Date().toISOString(), level: name, message, ...meta })}\n`);
    };
    return Object.freeze({
        debug: (message, meta) => write('debug', message, meta),
        info: (message, meta) => write('info', message, meta),
        warn: (message, meta) => write('warn', message, meta),
        error: (message, meta) => write('error', message, meta),
    });
}

module.exports = { createLogger };
