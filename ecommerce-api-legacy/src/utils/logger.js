const LEVELS = Object.freeze({ info: 20, error: 40 });

function createLogger(level = 'info', stream = process.stdout) {
    const threshold = LEVELS[level] ?? LEVELS.info;

    const write = (name, message, meta = {}) => {
        if (LEVELS[name] < threshold) return;
        stream.write(`${JSON.stringify({ time: new Date().toISOString(), level: name, message, ...meta })}\n`);
    };

    return Object.freeze({
        info: (message, meta) => write('info', message, meta),
        error: (message, meta) => write('error', message, meta),
    });
}

module.exports = { createLogger };
