const { AppError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../utils/constants');

const UNKNOWN_STUDENT_NAME = 'Unknown';
const DB_ERROR_MESSAGE = 'Erro DB';

function createAdminController({ reportModel }) {
    return {
        async financialReport() {
            let rows;
            try {
                rows = await reportModel.financialReport();
            } catch (error) {
                throw new AppError(DB_ERROR_MESSAGE, 500);
            }
            const courses = new Map();

            for (const row of rows) {
                if (!courses.has(row.course_id)) {
                    courses.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
                }
                if (row.enrollment_id === null) continue;

                const courseData = courses.get(row.course_id);
                const paid = row.payment_status === PAYMENT_STATUS.PAID ? row.payment_amount : 0;
                if (row.payment_status === PAYMENT_STATUS.PAID) {
                    courseData.revenue += row.payment_amount;
                }
                courseData.students.push({
                    student: row.student_name ?? UNKNOWN_STUDENT_NAME,
                    paid,
                });
            }

            return [...courses.values()];
        },
    };
}

module.exports = { createAdminController };
