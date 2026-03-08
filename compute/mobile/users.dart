import 'dart:convert';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://192.168.2.19:5000';

/// Fetches user information including habits, logs, and rules from the backend.
///
/// This function makes a GET request to the /users/<user_id> endpoint as defined
/// in the Python Flask backend (users.py). It returns a map containing:
/// - 'habits': List of habit objects
/// - 'logs': List of log records (as maps)
/// - 'rules': List of rule objects
///
/// @param userId The ID of the user to fetch information for
/// @return A Future that resolves to a Map<String, dynamic> with the user data
/// @throws Exception if the request fails or returns a non-200 status code
Future<Map<String, dynamic>> getUserInfo(int userId) async {
  final url = '$baseUrl/users/$userId';
  final uri = Uri.parse(url);

  final response = await http.get(uri);

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data;
  } else {
    throw Exception('Failed to load user info: ${response.statusCode} ${response.reasonPhrase}');
  }
}
