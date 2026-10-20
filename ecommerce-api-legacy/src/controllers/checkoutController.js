const crypto = require('node:crypto');
const { AppError } = require('../utils/errors');
const { APPROVED_CARD_PREFIX, PAYMENT_STATUS } = require('../utils/constants');
const { hashPassword } = require('../utils/password');

function createCheckoutController({ courseModel, userModel, enrollmentModel, paymentModel, auditLogModel, cache, logger }) {
    async function checkout({ usr, eml, pwd, courseId, card }) {
        let course;
        try {
            course = await courseModel.findActiveById(courseId);
        } catch (err) {
            throw new AppError('Curso não encontrado', 404);
        }
        if (!course) {
            throw new AppError('Curso não encontrado', 404);
        }

        let existingUser;
        try {
            existingUser = await userModel.findByEmail(eml);
        } catch (err) {
            throw new AppError('Erro DB', 500);
        }

        let userId;
        if (!existingUser) {
            const rawPassword = pwd ?? crypto.randomBytes(16).toString('hex');
            const passwordHash = hashPassword(rawPassword);
            let createdUser;
            try {
                createdUser = await userModel.create(usr, eml, passwordHash);
            } catch (err) {
                throw new AppError('Erro ao criar usuário', 500);
            }
            userId = createdUser.lastID;
        } else {
            userId = existingUser.id;
        }

        logger.info('Processing payment', { courseId });
        const status = card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;

        if (status === PAYMENT_STATUS.DENIED) {
            throw new AppError('Pagamento recusado', 400);
        }

        let enrollment;
        try {
            enrollment = await enrollmentModel.create(userId, courseId);
        } catch (err) {
            throw new AppError('Erro Matrícula', 500);
        }

        try {
            await paymentModel.create(enrollment.lastID, course.price, status);
        } catch (err) {
            throw new AppError('Erro Pagamento', 500);
        }

        try {
            await auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);
        } catch (err) {
            logger.error('Failed to record audit log', { error: err.message });
        }

        cache.set(`last_checkout_${userId}`, course.title);

        return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
    }

    return { checkout };
}

module.exports = { createCheckoutController };
