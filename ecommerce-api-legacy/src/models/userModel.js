function createUserModel(db) {
    return {
        findByEmail: (email) => db.get('SELECT * FROM users WHERE email = ?', [email]),
        create: async (name, email, passwordHash) => {
            const { lastID } = await db.run(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
                [name, email, passwordHash],
            );
            return lastID;
        },
        deleteById: (id) => db.run('DELETE FROM users WHERE id = ?', [id]),
    };
}

module.exports = { createUserModel };
