const sqlite3 = require('sqlite3').verbose();

function createDatabase(path) {
    const raw = new sqlite3.Database(path);

    return {
        run: (sql, params = []) => new Promise((resolve, reject) => {
            raw.run(sql, params, function onRun(err) {
                if (err) reject(err);
                else resolve({ lastID: this.lastID, changes: this.changes });
            });
        }),
        get: (sql, params = []) => new Promise((resolve, reject) => {
            raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        }),
        all: (sql, params = []) => new Promise((resolve, reject) => {
            raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
        }),
    };
}

module.exports = { createDatabase };
