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
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Add Habit"),
        content: TextField(
          controller: _nameController,
          decoration: const InputDecoration(
            hintText: "Habit name",
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () async {
              await addHabit();
              Navigator.pop(context);
            },
            child: const Text("Add"),
          ),
        ],
      ),
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
              trailing: IconButton(
                icon: const Icon(Icons.delete),
                onPressed: () => deleteHabit(habit.id),
              )
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
