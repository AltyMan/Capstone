import 'dart:convert';
import 'package:flutter/material.dart';
import '../http_habit_repository.dart';
import '../habit.dart';

class HabitPage extends StatefulWidget {
  
  const HabitPage({super.key});

  @override
  State<HabitPage> createState() => _HabitPageState();
}

class _HabitPageState extends State<HabitPage> {
  late HttpHabitRepository repo;

  List<Map<String, dynamic>> habits = [];

  @override
  void initState() {
    super.initState();
    repo = HttpHabitRepository(1);
    loadHabits();
  }

  Future<void> loadHabits() async {
    final res = await repo.client.get(repo.uri(''));

    if (res.statusCode != 200) {
      throw Exception("Failed to load habits");
    }

    final Map<String, dynamic> json = jsonDecode(res.body);
    final List data = json["result"]["habits"];

    setState(() {
      habits = List<Map<String, dynamic>>.from(data);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Habits")),
      body: ListView.builder(
        itemCount: habits.length,
        itemBuilder: (context, index) {
          final habit = habits[index];

          final name = habit["habit_name"];
          final isDevice = habit["is_device"];

          return ListTile(
            title: Text(name),
            subtitle: Text(isDevice ? "Device habit" : "Manual habit"),
          );
        },
      ),
    );
  }
}
