import 'dart:convert';
import 'http_repository.dart';
import './user.dart';

class HttpUserRepository extends HttpRepository<User> {
    HttpuserRepository(super.userId);

    @override
    String get resource => '';

    @override
    Future<bool> create(User user) async {
        final res = await client.post(uri('/add', user.toQuery())); 
        return res.statusCode == 200;
    }

    @override
    Future<List<User>> read() async {
        final res = await client.get(uri(''));

        if (res.statusCode != 200) {
            throw Exception('Failed to load users');
        }

        final Map<String, dynamic> data = jsonDecode(res.body);
        print(data);
        return <User>[];
    }

    @override
    Future<bool> update(User user) async {
        final res = await client.post(
        uri('/update/${user.user_id}', user.toQuery()),
        );
        return res.statusCode == 200;
    }

    @override
    Future<bool> delete(int user_id) async {
        final res = await client.delete(uri('/$user_id'));
        return res.statusCode == 200;
    }

}
