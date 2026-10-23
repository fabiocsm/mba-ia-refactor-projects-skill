const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function createAdminRoutes(adminController, adminAuth) {
    const router = express.Router();

    router.get('/api/admin/financial-report', adminAuth, asyncHandler(async (req, res) => {
        res.json(await adminController.financialReport());
    }));

    return router;
}

module.exports = { createAdminRoutes };
