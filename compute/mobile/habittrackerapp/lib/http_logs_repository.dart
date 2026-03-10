import 'dart:convert';
import './http_repository.dart';
import 'log.dart';

class HttpLogRepository extends HttpRepository<Log> {
    HttpLogRepository(super.userId);

    @override
    String get resource => 'logs';

    @override
    Future<bool> create(Log log) async {
        final res = await client.post(uri('/add', log.toQuery()));
        return res.statusCode == 200;
    }

    @override
    Future<List<Log>> read() async {
        final res = await client.get(uri(''));

        if (res.statusCode != 200) {
            throw Exception('Failed to load logs');
        }

        final Map<String, dynamic> data = jsonDecode(res.body);
        List<dynamic> ilogs = data['result'];
        print(ilogs);
        List<Log> logs = ilogs.map((e) => Log.fromJson(e)).toList();
        return logs;
    }

    @override
    Future<bool> update(Log log) async {
        final res = await client.post(
            uri('/update/${log.id}', log.toQuery()),
        );
        return res.statusCode == 200;
    }
    
    Future<bool> updateField(int id, String field, String value) async {
    final res = await client.post(
        uri('/update', {'id': id.toString(), 'field': field, 'value': value}),
    );
    return res.statusCode == 200;
}

    @override
    Future<bool> delete(int id) async {
        final res = await client.delete(uri('/$id'));
        return res.statusCode == 200;
    }
}
