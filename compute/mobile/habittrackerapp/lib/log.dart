class Log {
    final int id;
    final int user_id;
    final String habit_name;
    final String timestamp;
    final String state;
    final bool self_reported;

    Log({
        required this.id,
        required this.user_id,
        required this.habit_name,
        required this.timestamp,
        required this.state,
        required this.self_reported,
    });

    factory Log.fromJson(Map<String, dynamic> json) {
        return Log(
            id: json['id'],
            user_id: json['user_id'],
            habit_name: json['habit_name'] ?? '',
            timestamp: json['timestamp'] ?? '',
            state: json['state'] ?? 'completed',
            self_reported: json['self_reported'] == 1,
        );
    }

    Map<String, String> toQuery() {
        return {
        'name': habit_name,
        'state': state,
        'reported': self_reported.toString(),
        };
    }
}


