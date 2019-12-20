CREATE TABLE IF NOT EXISTS `tabPatch` (
    `id`        INTEGER   PRIMARY KEY AUTOINCREMENT,
    `name`      TEXT,
    `duration`  REAL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `tabSingle` (
    `id`        INTEGER   PRIMARY KEY AUTOINCREMENT,
    `key`       TEXT,
    `value`     TEXT
);