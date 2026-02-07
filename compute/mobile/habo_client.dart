import 'http_habit_repository.dart';
import 'http_rule_repository.dart';
import 'habit.dart';
import 'rule.dart';


Future<void> main() async {
  final habit_repo = HttpHabitRepository(1);
  final rule_repo = HttpRuleRepository(1);

  try {
    await habit_repo.create(Habit(id: 1, name: "Tester", isDevice: true));
    print('Habit created successfully');
  } catch (e) {
    print('Error: $e');
  }
}
