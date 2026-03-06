import '../../http_habit_repository.dart';
import '../../http_rule_repository.dart';
import 'habit.dart';
import '../../rule.dart';


Future<void> main() async {
  final habitRepo = HttpHabitRepository(1);
  final ruleRepo = HttpRuleRepository(1);

  try {
    await habitRepo.create(Habit(id: 1, name: "Tester", isDevice: true));
    print('Habit created successfully');
  } catch (e) {
    print('Error: $e');
  }
}
