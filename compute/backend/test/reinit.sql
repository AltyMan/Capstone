
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        );

INSERT INTO users DEFAULT VALUES;


DROP TABLE IF EXISTS habits;
CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mqtt_topic TEXT,
            assoc_dev_id TEXT,
            habit_name TEXT NOT NULL,
            is_device BOOLEAN DEFAULT 0,
            habit_full_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
INSERT INTO habits (user_id, mqtt_topic, habit_name, is_device, assoc_dev_id)
VALUES (1, "bing/bong", "Bonger", True, "hs105");

DROP TABLE IF EXISTS habit_rules;
CREATE TABLE IF NOT EXISTS habit_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id TEXT NOT NULL DEFAULT "No Job",
            habit_name TEXT NOT NULL,
            day INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            count INTEGER DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT False,
            FOREIGN KEY(user_id) REFERENCES users(id)
            FOREIGN KEY(user_id) REFERENCES habits(user_id)
        );
INSERT INTO habit_rules (user_id, habit_name, day, hour, minute, count)
VALUES (1, "Bonger", 0, 12, 32, 67);

DROP TABLE IF EXISTS habit_logs;
CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            habit_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            state TEXT,
            self_reported BOOLEAN,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
INSERT INTO habit_logs (user_id, habit_name, timestamp, state, self_reported)
VALUES (1, "Bonger", "2026-02-05 16:20:53", "ON", True);

SELECT * FROM habit_rules WHERE user_id = 1;
SELECT * FROM habits WHERE user_id = 1;
SELECT * from habit_logs WHERE user_id = 1;
/*
{
  "title": "Push-ups",
  "position": 1,
  "twoDayRule": false,
  "cue": "After breakfast",
  "routine": "Do 20 push-ups",
  "reward": "Feel strong",
  "showReward": true,
  "advanced": false,
  "notification": true,
  "notTime": "08:00",
  "sanction": "",
  "showSanction": false,
  "accountant": "",
  "habitType": 1,
  "targetValue": 20.0,
  "partialValue": 10.0,
  "unit": "reps",
  "archived": false
}
*/