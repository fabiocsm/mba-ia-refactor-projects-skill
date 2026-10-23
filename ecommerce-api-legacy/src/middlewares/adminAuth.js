const crypto = require('node:crypto');
const { AppError } = require('../utils/errors');
const { ADMIN_TOKEN_HEADER } = require('../utils/constants');

const ADMIN_DISABLED_MESSAGE = 'Admin endpoint disabled';
const UNAUTHORIZED_MESSAGE = 'Unauthorized';

function createAdminAuth(adminToken) {
    return (req, res, next) => {
        if (!adminToken) {
            return next(new AppError(ADMIN_DISABLED_MESSAGE, 403));
        }
        const provided = Buffer.from(req.get(ADMIN_TOKEN_HEADER) ?? '');
        const expected = Buffer.from(adminToken);
        if (provided.length !== expected.length || !crypto.timingSafeEqual(provided, expected)) {
            return next(new AppError(UNAUTHORIZED_MESSAGE, 401));
        }
        return next();
    };
}

module.exports = { createAdminAuth };
