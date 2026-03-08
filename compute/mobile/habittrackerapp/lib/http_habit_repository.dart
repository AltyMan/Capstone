import 'dart:convert';
import './http_repository.dart';
import 'habit.dart';

class HttpHabitRepository extends HttpRepository<Habit> {
  HttpHabitRepository(super.userId);

  @override
  String get resource => 'habits';

  @override
  Future<bool> create(Habit habit) async {
    final res = await client.post(uri('/add', habit.toQuery()));
    return res.statusCode == 200;
  }

  @override
  Future<List<Habit>> read() async {
    print(uri(''));
    final res = await client.get(uri(''));

    if (res.statusCode != 200) {
      throw Exception('Failed to load habits');
    }

    final Map<String, dynamic> data = jsonDecode(res.body);
    print(data);
    return <Habit>[];
    // return data.map((e) => Habit.fromJson(e)).toList();
  }

  // Won't work

  @override
  Future<bool> update(Habit habit) async {
    final res = await client.post(
      uri('/update/${habit.id}', habit.toQuery()),
    );
    return res.statusCode == 200;
  }

  @override
  Future<bool> delete(int id) async {
    final res = await client.delete(uri('/$id'));
    return res.statusCode == 200;
  }
}
