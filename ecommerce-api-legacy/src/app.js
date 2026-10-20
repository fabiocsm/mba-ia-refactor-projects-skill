const express = require('express');
const { config } = require('./config');
const { createLogger } = require('./utils/logger');
const { createCache } = require('./utils/cache');
const { hashPassword } = require('./utils/password');
const { createDatabase } = require('./database/connection');
const { initSchema, seed } = require('./database/schema');

const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createReportModel } = require('./models/reportModel');

const { createCheckoutController } = require('./controllers/checkoutController');
const { createAdminController } = require('./controllers/adminController');
const { createUserController } = require('./controllers/userController');

const { createCheckoutRoutes } = require('./routes/checkoutRoutes');
const { createAdminRoutes } = require('./routes/adminRoutes');
const { createUserRoutes } = require('./routes/userRoutes');

const { createAdminAuth } = require('./middlewares/adminAuth');
const { createErrorHandler } = require('./middlewares/errorHandler');

const logger = createLogger(config.logLevel);

async function start() {
    const db = createDatabase(config.dbPath);

    await initSchema(db);
    await seed(db, { hashPassword });

    const cache = createCache(logger);

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const reportModel = createReportModel(db);

    const checkoutController = createCheckoutController({
        courseModel,
        userModel,
        enrollmentModel,
        paymentModel,
        auditLogModel,
        cache,
        logger,
    });
    const adminController = createAdminController({ reportModel });
    const userController = createUserController({ userModel, logger });

    const adminAuth = createAdminAuth(config.adminToken);

    const app = express();
    app.use(express.json());
    app.use(createCheckoutRoutes(checkoutController));
    app.use(createAdminRoutes(adminController, adminAuth));
    app.use(createUserRoutes(userController));
    app.use(createErrorHandler(logger));

    app.listen(config.port, config.host, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    logger.error('Startup failed', { error: err.message });
    process.exitCode = 1;
});

module.exports = { start };
