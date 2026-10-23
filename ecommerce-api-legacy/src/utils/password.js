const crypto = require('node:crypto');

const SALT_BYTES = 16;
const KEY_LENGTH = 32;

function hashPassword(password) {
    const salt = crypto.randomBytes(SALT_BYTES).toString('hex');
    const key = crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex');
    return `${salt}:${key}`;
}

module.exports = { hashPassword };
