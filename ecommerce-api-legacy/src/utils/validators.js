const { AppError } = require('./errors');

const BAD_REQUEST_MESSAGE = 'Bad Request';

function validateCheckoutPayload(body) {
    const payload = (body && typeof body === 'object') ? body : {};
    const { usr: username, eml: email, pwd: password, c_id: courseId, card } = payload;

    if (!username || !email || !courseId || !card || typeof card !== 'string') {
        throw new AppError(BAD_REQUEST_MESSAGE, 400);
    }

    return { username, email, password, courseId, card };
}

module.exports = { validateCheckoutPayload };
