import 'dart:convert';
import 'http_repository.dart';
import './rule.dart';

class HttpRuleRepository extends HttpRepository<Rule> {
  HttpRuleRepository(super.userId);

  @override
  String get resource => 'rules';

  @override
  Future<bool> create(Rule rule) async {
    final res = await client.post(uri('/add', rule.toQuery()));
    return res.statusCode == 200;
  }

  @override
  Future<List<Rule>> read() async {
    final res = await client.get(uri(''));

    if (res.statusCode != 200) {
      throw Exception('Failed to load rules');
    }

    final Map<String, dynamic> data = jsonDecode(res.body);
    print(data);
    return <Rule>[];
    // return data.map((e) => Rule.fromJson(e)).toList();
  }

  // Won't work

  @override
  Future<bool> update(Rule rule) async {
    final res = await client.post(
      uri('/update/${rule.id}', rule.toQuery()),
    );
    return res.statusCode == 200;
  }

  @override
  Future<bool> delete(int id) async {
    final res = await client.delete(uri('/$id'));
    return res.statusCode == 200;
  }
}
