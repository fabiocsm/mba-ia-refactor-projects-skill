const config = Object.freeze({
    port: Number(process.env.PORT) || 3000,
    host: process.env.HOST || '0.0.0.0',
    dbPath: process.env.DATABASE_PATH || ':memory:',
    logLevel: process.env.LOG_LEVEL || 'info',
    adminToken: process.env.ADMIN_TOKEN || '',
});

module.exports = { config };
