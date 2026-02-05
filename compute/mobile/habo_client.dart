// import 'dart:convert';
import 'package:http/http.dart' as http;

class HttpHabitRepository{
  final int userId;
  static const String _baseUrl = 'http://192.168.2.19:5000';

  HttpHabitRepository(this.userId);

  Uri _uri(String path, [Map<String, String>? params]) {
    return Uri.parse('$_baseUrl/$userId/habits$path')
        .replace(queryParameters: params);
  }

  // -------------------------
  // POST /<user_id>/habits/add?name=&device=
  // -------------------------
  Future<int> createHabit(String title, bool is_device) async {

    final response = await http.post(
      _uri('/add', {
        'name': title,
        'device': is_device.toString(),
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to create habit');
    }

    return 1; // backend does not return ID
  }

  Future<int> getUserInfo() async {
    final response = await http.post(
      _uri('/')
    );

    if (response.statusCode != 200) {
      throw Exception("Failed to get user information");
    }

    return 1;
  }
}

Future<void> main() async {
  final repo = HttpHabitRepository(1);

  try {
    await repo.createHabit('Test Habit from Dart', false);
    print('Habit created successfully');
  } catch (e) {
    print('Error: $e');
  }
}
