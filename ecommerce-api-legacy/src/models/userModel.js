function createUserModel(db) {
    return {
        findByEmail: (email) => db.get('SELECT id FROM users WHERE email = ?', [email]),
        create: (name, email, passwordHash) => db.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash],
        ),
        deleteById: (id) => db.run('DELETE FROM users WHERE id = ?', [id]),
    };
}

module.exports = { createUserModel };
