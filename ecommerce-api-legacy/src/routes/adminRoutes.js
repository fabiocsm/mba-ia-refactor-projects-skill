const express = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');

function createAdminRoutes(adminController, adminAuth) {
    const router = express.Router();

    router.get('/api/admin/financial-report', adminAuth, asyncHandler(async (req, res) => {
        const report = await adminController.financialReport();
        res.status(200).json(report);
    }));

    return router;
}

module.exports = { createAdminRoutes };
