const { APPROVED_CARD_PREFIX, PAYMENT_STATUS } = require('../utils/constants');

function createPaymentGateway({ apiKey, logger }) {
    return {
        charge(cardNumber) {
            logger.info('Processando pagamento', { gatewayConfigured: Boolean(apiKey) });
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentGateway };
