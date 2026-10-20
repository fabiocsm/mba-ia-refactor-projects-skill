const { AppError } = require('./errors');

function validateCheckoutPayload(body) {
    const data = body && typeof body === 'object' ? body : {};
    const { usr, eml, pwd, c_id, card } = data;

    if (!usr || !eml || !c_id || !card) {
        throw new AppError('Bad Request', 400);
    }
    if (typeof usr !== 'string' || typeof eml !== 'string' || typeof card !== 'string') {
        throw new AppError('Bad Request', 400);
    }
    if (pwd !== undefined && pwd !== null && typeof pwd !== 'string') {
        throw new AppError('Bad Request', 400);
    }
    if (typeof c_id !== 'number' && typeof c_id !== 'string') {
        throw new AppError('Bad Request', 400);
    }

    return {
        usr,
        eml,
        pwd: typeof pwd === 'string' && pwd.length > 0 ? pwd : null,
        courseId: c_id,
        card,
    };
}

module.exports = { validateCheckoutPayload };
