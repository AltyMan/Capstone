class Rule {
  final int id;
  final String habit;
  final int day;
  final int hour;
  final int minute;
  final bool active;

  Rule({
    required this.id,
    required this.habit,
    required this.day,
    required this.hour,
    required this.minute,
    required this.active,
  });

  factory Rule.fromJson(Map<String, dynamic> json) {
    return Rule(
      id: json['id'],
      habit: json['habit'],
      day: json['day'],
      hour: json['hour'],
      minute: json['minute'],
      active: json['active'],
    );
  }

  Map<String, String> toQuery() {
    return {
      'habit': habit,
      'day': day.toString(),
      'hour': hour.toString(),
      'minute': minute.toString(),
      'active': active.toString(),
    };
  }
}
