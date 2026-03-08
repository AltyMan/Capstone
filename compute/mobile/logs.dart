import 'dart:convert';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://192.168.2.19:5000';

/// Adds a new log entry for the user.
///
/// Makes a POST request to /<user_id>/logs/add with query parameters.
/// @param userId The user ID
/// @param name The habit name
/// @param state The log state
/// @param reported Whether self-reported
/// @return True if successful
Future<bool> addLog(int userId, String name, String state, bool reported) async {
  final url = '$baseUrl/$userId/logs/add';
  final uri = Uri.parse(url).replace(queryParameters: {
    'name': name,
    'state': state,
    'reported': reported.toString(),
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Retrieves log entries for the user, optionally filtered by habit name.
///
/// Makes a GET request to /<user_id>/logs.
/// @param userId The user ID
/// @param name Optional habit name to filter
/// @return List of log maps
Future<List<Map<String, dynamic>>> getLogs(int userId, {String? name}) async {
  final url = '$baseUrl/$userId/logs';
  final params = name != null ? {'name': name} : {};
  final uri = Uri.parse(url).replace(queryParameters: params);

  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final result = data['result'] as List<dynamic>;
    return result.cast<Map<String, dynamic>>();
  } else {
    throw Exception('Failed to load logs: ${response.statusCode}');
  }
}

/// Updates a log entry for the user.
///
/// Makes a POST request to /<user_id>/logs/update.
/// @param userId The user ID
/// @param id The log ID
/// @param field The field to update
/// @param value The new value
/// @return True if successful
Future<bool> updateLog(int userId, int id, String field, String value) async {
  final url = '$baseUrl/$userId/logs/update';
  final uri = Uri.parse(url).replace(queryParameters: {
    'id': id.toString(),
    'field': field,
    'value': value,
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}

/// Deletes a log entry for the user.
///
/// Makes a POST request to /<user_id>/logs/delete.
/// @param userId The user ID
/// @param id The log ID
/// @return True if successful
Future<bool> deleteLog(int userId, int id) async {
  final url = '$baseUrl/$userId/logs/delete';
  final uri = Uri.parse(url).replace(queryParameters: {
    'id': id.toString(),
  });

  final response = await http.post(uri);

  return response.statusCode == 200;
}
