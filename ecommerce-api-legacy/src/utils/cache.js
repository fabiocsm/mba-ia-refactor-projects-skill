function createCache(logger) {
    const store = new Map();

    return {
        set(key, value) {
            logger.info('Cache updated', { key });
            store.set(key, value);
        },
    };
}

module.exports = { createCache };
