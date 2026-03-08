import 'dart:convert';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://192.168.2.19:5000';

/// Adds a new habit for the user.
///
/// Makes a POST request to /<user_id>/habits/add with query parameters.
/// @param userId The user ID
/// @param name The habit name
/// @param isDevice Whether the habit is device-associated
/// @return True if successful (status 200)
Future<bool> addHabit(int userId, String name, bool isDevice) async {
  final url = '$baseUrl/$userId/habits/add';
  final uri = Uri.parse(url).replace(queryParameters: {
    'name': name,
    'device': isDevice.toString(),
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Retrieves all habits for the user.
///
/// Makes a GET request to /<user_id>/habits.
/// @param userId The user ID
/// @return List of habit maps
Future<List<Map<String, dynamic>>> getHabits(int userId) async {
  final url = '$baseUrl/$userId/habits';
  final uri = Uri.parse(url);

  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final result = data['result'] as Map<String, dynamic>;
    final habits = result['habits'] as List<dynamic>;
    return habits.cast<Map<String, dynamic>>();
  } else {
    throw Exception('Failed to load habits: ${response.statusCode}');
  }
}

/// Updates a habit field for the user.
///
/// Makes a POST request to /<user_id>/habits/update.
/// @param userId The user ID
/// @param name The habit name
/// @param field The field to update
/// @param value The new value
/// @return True if successful
Future<bool> updateHabit(int userId, String name, String field, String value) async {
  final url = '$baseUrl/$userId/habits/update';
  final uri = Uri.parse(url).replace(queryParameters: {
    'name': name,
    'field': field,
    'value': value,
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Deletes a habit for the user.
///
/// Makes a POST request to /<user_id>/habits/delete.
/// @param userId The user ID
/// @param name The habit name
/// @return True if successful
Future<bool> deleteHabit(int userId, String name) async {
  final url = '$baseUrl/$userId/habits/delete';
  final uri = Uri.parse(url).replace(queryParameters: {
    'name': name,
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}
