const express = require('express');
const { asyncHandler } = require('../middlewares/asyncHandler');

function createUserRoutes(userController) {
    const router = express.Router();

    router.delete('/api/users/:id', asyncHandler(async (req, res) => {
        const message = await userController.deleteUser(req.params.id);
        res.status(200).send(message);
    }));

    return router;
}

module.exports = { createUserRoutes };
