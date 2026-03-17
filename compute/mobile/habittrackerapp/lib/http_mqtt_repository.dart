import 'dart:convert';
import 'package:http/http.dart' as http;

class HttpMqttRepository {
  final String baseUrl;
    // 172.20.10.13
  HttpMqttRepository({this.baseUrl = 'http://192.168.2.211:5000'});

  Uri _uri(String path) => Uri.parse('$baseUrl$path');

Future<List<Map<String, dynamic>>> getDevices() async {
  final res = await http.get(_uri('/devices'));
  if (res.statusCode != 200) throw Exception('Failed to load devices');

  final data = jsonDecode(res.body) as Map<String, dynamic>;

  return data.entries.map((entry) {
    final device = Map<String, dynamic>.from(entry.value);

    return {
      'id': entry.key,
      'type': device['type'],
      'vendor': device['vendor'],
      'state': (device['last_state'] ?? 'OFF').toString().toLowerCase(),
    };
  }).toList();
}

  Future<bool> setDevice(String deviceId, String state) async {
  final uri = Uri.parse('$baseUrl/devices/$deviceId/set?state=$state');

  final res = await http.post(uri);

  return res.statusCode == 200;
}
}
