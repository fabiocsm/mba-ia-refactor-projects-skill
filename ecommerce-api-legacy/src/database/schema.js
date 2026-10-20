const { PAYMENT_STATUS } = require('../utils/constants');

async function initSchema(db) {
    await db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await db.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await db.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await db.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await db.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seed(db, { hashPassword }) {
    const seedPasswordHash = hashPassword('123');

    const user = await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash],
    );
    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
        ['Clean Architecture', 997.0, 'Docker', 497.0],
    );
    const enrollment = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [user.lastID, 1],
    );
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollment.lastID, 997.0, PAYMENT_STATUS.PAID],
    );
}

module.exports = { initSchema, seed };
