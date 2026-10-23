const USER_DELETED_MESSAGE = 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';

function createUserController({ userModel, logger }) {
    return {
        async deleteUser(id) {
            try {
                await userModel.deleteById(id);
            } catch (error) {
                logger.error('Falha ao deletar usuário', { error: error.message });
            }
            return USER_DELETED_MESSAGE;
        },
    };
}

module.exports = { createUserController };
