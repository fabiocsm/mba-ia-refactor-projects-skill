const { AppError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../utils/constants');
const { hashPassword } = require('../utils/password');

const COURSE_NOT_FOUND_MESSAGE = 'Curso não encontrado';
const DB_ERROR_MESSAGE = 'Erro DB';
const ENROLLMENT_ERROR_MESSAGE = 'Erro Matrícula';
const PAYMENT_ERROR_MESSAGE = 'Erro Pagamento';
const USER_CREATION_ERROR_MESSAGE = 'Erro ao criar usuário';
const PAYMENT_DENIED_MESSAGE = 'Pagamento recusado';
const PASSWORD_REQUIRED_MESSAGE = 'Senha obrigatória para novo usuário';
const SUCCESS_MESSAGE = 'Sucesso';

function createCheckoutController({
    userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, logger,
}) {
    return {
        async checkout({ username, email, password, courseId, card }) {
            let course;
            try {
                course = await courseModel.findActiveById(courseId);
            } catch (error) {
                throw new AppError(DB_ERROR_MESSAGE, 500);
            }
            if (!course) {
                throw new AppError(COURSE_NOT_FOUND_MESSAGE, 404);
            }

            let user;
            try {
                user = await userModel.findByEmail(email);
            } catch (error) {
                throw new AppError(DB_ERROR_MESSAGE, 500);
            }

            let userId;
            if (!user) {
                if (typeof password !== 'string' || !password) {
                    throw new AppError(PASSWORD_REQUIRED_MESSAGE, 400);
                }
                try {
                    userId = await userModel.create(username, email, hashPassword(password));
                } catch (error) {
                    throw new AppError(USER_CREATION_ERROR_MESSAGE, 500);
                }
            } else {
                userId = user.id;
            }

            const status = paymentGateway.charge(card);
            if (status === PAYMENT_STATUS.DENIED) {
                throw new AppError(PAYMENT_DENIED_MESSAGE, 400);
            }

            let enrollmentId;
            try {
                enrollmentId = await enrollmentModel.create(userId, courseId);
            } catch (error) {
                throw new AppError(ENROLLMENT_ERROR_MESSAGE, 500);
            }

            try {
                await paymentModel.create(enrollmentId, course.price, status);
            } catch (error) {
                throw new AppError(PAYMENT_ERROR_MESSAGE, 500);
            }

            try {
                await auditLogModel.record(`Checkout curso ${courseId} por ${userId}`);
            } catch (error) {
                logger.error('Falha ao registrar log de auditoria', { error: error.message });
            }

            return { msg: SUCCESS_MESSAGE, enrollment_id: enrollmentId };
        },
    };
}

module.exports = { createCheckoutController };
