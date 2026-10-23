const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');
const { validateCheckoutPayload } = require('../utils/validators');

function createCheckoutRoutes(checkoutController) {
    const router = express.Router();

    router.post('/api/checkout', asyncHandler(async (req, res) => {
        const payload = validateCheckoutPayload(req.body);
        const result = await checkoutController.checkout(payload);
        res.status(200).json(result);
    }));

    return router;
}

module.exports = { createCheckoutRoutes };
