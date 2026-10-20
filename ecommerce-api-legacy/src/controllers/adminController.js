const { AppError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../utils/constants');

function createAdminController({ reportModel }) {
    async function financialReport() {
        let rows;
        try {
            rows = await reportModel.findCourseFinancials();
        } catch (err) {
            throw new AppError('Erro DB', 500);
        }
        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const courseData = byCourse.get(row.course_id);
            const student = row.user_name ?? 'Unknown';
            const paid = row.payment_amount ?? 0;
            courseData.students.push({ student, paid });
            if (row.payment_status === PAYMENT_STATUS.PAID) {
                courseData.revenue += row.payment_amount;
            }
        }

        return [...byCourse.values()];
    }

    return { financialReport };
}

module.exports = { createAdminController };
