function createEnrollmentModel(db) {
    return {
        create: (userId, courseId) => db.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        ),
    };
}

module.exports = { createEnrollmentModel };
