import 'package:flutter/material.dart';
import '../habit.dart';
import '../http_habit_repository.dart';

class HabitPage extends StatefulWidget {
  const HabitPage({super.key});

  @override
  State<HabitPage> createState() => _HabitPageState();
}

class _HabitPageState extends State<HabitPage> {
  late HttpHabitRepository repo;
  List<Habit> habits = [];

  final TextEditingController _nameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    repo = HttpHabitRepository(1);
    loadHabits();
  }

  Future<void> loadHabits() async {
    try {
      final data = await repo.read();

      setState(() {
        habits = data;
        // print(habits);
      });
    } catch (e) {
      print(e);
    }
  }

  Future<void> addHabit() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;

    final habit = Habit(
      id: 0,
      name: name,
      isDevice: false,
    );

    final success = await repo.create(habit);

    if (success) {
      _nameController.clear();
      await loadHabits();
    }
  }

  Future<void> deleteHabit(int id) async {
    await repo.delete(0);
    await loadHabits();
  }

  void showAddHabitDialog() {
  final TextEditingController controller = TextEditingController();
  bool isDevice = false;

  showDialog(
    context: context,
    builder: (context) {
      return StatefulBuilder(
        builder: (context, setStateDialog) {
          return AlertDialog(
            title: const Text("Add Habit"),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: controller,
                  decoration: const InputDecoration(
                    hintText: "Habit name",
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("Device Habit"),
                    Switch(
                      value: isDevice,
                      onChanged: (value) {
                        setStateDialog(() {
                          isDevice = value;
                        });
                      },
                    ),
                  ],
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Cancel"),
              ),
              ElevatedButton(
                onPressed: () async {
                  final name = controller.text.trim();
                  if (name.isEmpty) return;

                  final habit = Habit(
                    id: 0,
                    name: name,
                    isDevice: isDevice,
                  );

                  final success = await repo.create(habit);

                  if (success) {
                    Navigator.pop(context);
                    loadHabits();
                  }
                },
                child: const Text("Add"),
              ),
            ],
          );
        },
      );
    },
  );
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Habits"),
      ),
      body: RefreshIndicator(
        onRefresh: loadHabits,
        child: ListView.builder(
          itemCount: habits.length,
          itemBuilder: (context, index) {
            final habit = habits[index];

            return ListTile(
              title: Text(habit.name),
              subtitle: Text(
                habit.isDevice ? "Device habit" : "Manual habit",
              ),
              leading: Icon(
                habit.isDevice ? Icons.memory : Icons.person,
              ),
              trailing: IconButton(
                icon: const Icon(Icons.delete),
                onPressed: () => deleteHabit(habit.id),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: showAddHabitDialog,
        child: const Icon(Icons.add),
      ),
    );
  }
}
