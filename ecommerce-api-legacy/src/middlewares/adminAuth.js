const crypto = require('node:crypto');
const { AppError } = require('../utils/errors');

const ADMIN_TOKEN_HEADER = 'x-admin-token';

function createAdminAuth(adminToken) {
    return (req, res, next) => {
        if (!adminToken) {
            return next(new AppError('Recurso administrativo desabilitado', 403));
        }
        const provided = Buffer.from(req.get(ADMIN_TOKEN_HEADER) ?? '');
        const expected = Buffer.from(adminToken);
        if (provided.length !== expected.length || !crypto.timingSafeEqual(provided, expected)) {
            return next(new AppError('Não autorizado', 401));
        }
        return next();
    };
}

module.exports = { createAdminAuth };
