class Habit {
  final int id;
  final String name;
  final bool isDevice;

  Habit({
    required this.id,
    required this.name,
    required this.isDevice,
  });

  factory Habit.fromJson(Map<String, dynamic> json) {
    return Habit(
      id: json['id'] ?? 0,
      name: json['habit_name'] ?? "None",
      isDevice: json['is_device'] ?? false,
    );
  }

  Map<String, String> toQuery() {
    return {
      'name': name,
      'device': isDevice.toString(),
    };
  }
}
