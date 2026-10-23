const express = require('express');
const { config } = require('./config');
const { createDatabase, initSchema, seed } = require('./database/connection');
const { createLogger } = require('./utils/logger');
const { hashPassword } = require('./utils/password');
const { createPaymentGateway } = require('./services/paymentGateway');

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
    const db = createDatabase(':memory:');
    await initSchema(db);
    await seed(db, { hashPassword });

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const reportModel = createReportModel(db);

    const paymentGateway = createPaymentGateway({ apiKey: config.paymentGatewayKey, logger });

    const checkoutController = createCheckoutController({
        userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, logger,
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

    app.listen(config.port, () => {
        logger.info(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    logger.error('Startup failed', { error: err.message });
    process.exitCode = 1;
});
