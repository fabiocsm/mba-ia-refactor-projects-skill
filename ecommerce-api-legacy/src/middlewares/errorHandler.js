const { AppError } = require('../utils/errors');

function createErrorHandler(logger) {
    return (err, req, res, next) => {
        if (err instanceof AppError) {
            return res.status(err.status).send(err.message);
        }
        logger.error('Unhandled error', { error: err.message });
        return res.status(500).send('Erro interno');
    };
}

module.exports = { createErrorHandler };
