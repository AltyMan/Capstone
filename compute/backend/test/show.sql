INSERT INTO habits (user_id, mqtt_topic, habit_name, is_device, assoc_dev_id) VALUES (1, "idk/idk", "plug2", True, "hs105");

DELETE FROM habit_logs WHERE habit_name = 'plug1';
DELETE FROM habit_logs WHERE habit_name = 'plug2';
DELETE FROM habit_logs WHERE habit_name = 'plug3';

SELECT * FROM habit_rules WHERE user_id = 1;
SELECT * FROM habits WHERE user_id = 1;
SELECT * from habit_logs WHERE user_id = 1;
