
SELECT * FROM habit_rules WHERE user_id = 1;
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

need to update db to reflect this

INSERT INTO habit_rules (user_id, job_id, habit_id, day, hour, minute, count, active)
VALUES (1, "239402382", "Sleep", 0, 12, 32, 67, True);
*/