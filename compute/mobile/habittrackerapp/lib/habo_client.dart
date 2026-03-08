import './http_habit_repository.dart';
import './http_rule_repository.dart';
import './habit.dart';
import './rule.dart';


// Still need to test Update/Delete (Have no actual delete routes)

Future<void> main() async {
  final habitRepo = HttpHabitRepository(1);
  final ruleRepo = HttpRuleRepository(1);

  // Habit Block
  try {
    Habit tester = Habit(id: 1, name: "Tester", isDevice: true);
    await habitRepo.create(tester);
    print("Habit created successfully!");
    await habitRepo.read();
    print("Habits read successfully!");
    // await habitRepo.update(tester);

  } catch (e) {
    print('Habit Error: $e');
  }

  // Rule Block
  try {
    Rule tester = Rule(id: 1, habit: "Tester", day: 0, hour: 8, minute: 45, active: true);
    await ruleRepo.create(tester);
    print("Rule created sucessfully!");
    await ruleRepo.read();
    print("Rules read sucessfully!");
  } catch(e) {
    print('Rule Error: $e');
  }

  // Log Block
  // User Block
}
