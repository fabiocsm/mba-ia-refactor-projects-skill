const { AppError } = require('../utils/errors');

const GENERIC_ERROR_MESSAGE = 'Internal Server Error';

function createErrorHandler(logger) {
    return (err, req, res, next) => {
        if (err instanceof AppError) {
            return res.status(err.status).send(err.message);
        }
        logger.error('Erro não tratado', { error: err.message });
        return res.status(500).send(GENERIC_ERROR_MESSAGE);
    };
}

module.exports = { createErrorHandler };
