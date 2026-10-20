const { AppError } = require('../utils/errors');

function createUserController({ userModel, logger }) {
    async function deleteUser(id) {
        try {
            await userModel.deleteById(id);
        } catch (err) {
            logger.error('Failed to delete user', { error: err.message });
            throw new AppError('Erro ao deletar usuário', 500);
        }
        return 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';
    }

    return { deleteUser };
}

module.exports = { createUserController };
