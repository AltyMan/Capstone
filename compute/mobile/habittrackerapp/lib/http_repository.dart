import 'package:http/http.dart' as http;

abstract class HttpRepository<T> {
  final int userId;
  final http.Client client;

  static const String baseUrl = 'http://172.20.10.13:5000';

  HttpRepository(this.userId, {http.Client? client})
      : client = client ?? http.Client();

  String get resource;

  Uri uri(String path, [Map<String, String>? params]) {
    return Uri.parse('$baseUrl/$userId/$resource$path')
        .replace(queryParameters: params);
  }

  Future<bool> create(T item);
  Future<List<T>> read();
  Future<bool> update(T item);
  Future<bool> delete(int id);
}
