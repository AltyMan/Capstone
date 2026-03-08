import 'dart:convert';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://192.168.2.19:5000';

/// Adds a new rule for the user.
///
/// Makes a POST request to /<user_id>/rules/add with query parameters.
/// @param userId The user ID
/// @param habit The habit name
/// @param day The day
/// @param hour The hour
/// @param minute The minute
/// @param active Whether active
/// @return True if successful
Future<bool> addRule(int userId, String habit, int day, int hour, int minute, bool active) async {
  final url = '$baseUrl/$userId/rules/add';
  final uri = Uri.parse(url).replace(queryParameters: {
    'habit': habit,
    'day': day.toString(),
    'hour': hour.toString(),
    'minute': minute.toString(),
    'active': active.toString(),
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Retrieves all rules for the user.
///
/// Makes a GET request to /<user_id>/rules.
/// @param userId The user ID
/// @return List of rule maps
Future<List<Map<String, dynamic>>> getRules(int userId) async {
  final url = '$baseUrl/$userId/rules';
  final uri = Uri.parse(url);

  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final result = data['result'] as List<dynamic>;
    return result.cast<Map<String, dynamic>>();
  } else {
    throw Exception('Failed to load rules: ${response.statusCode}');
  }
}

/// Updates rules for a habit (placeholder, as per Python code).
///
/// Makes a POST request to /<user_id>/rules/update.
/// @param userId The user ID
/// @param habit The habit name
/// @return True if successful
Future<bool> updateRule(int userId, String habit) async {
  final url = '$baseUrl/$userId/rules/update';
  final uri = Uri.parse(url).replace(queryParameters: {
    'habit': habit,
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Deletes rules for a habit.
///
/// Makes a POST request to /<user_id>/rules/delete.
/// @param userId The user ID
/// @param habit The habit name
/// @return True if successful
Future<bool> deleteRule(int userId, String habit) async {
  final url = '$baseUrl/$userId/rules/delete';
  final uri = Uri.parse(url).replace(queryParameters: {
    'habit': habit,
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}
