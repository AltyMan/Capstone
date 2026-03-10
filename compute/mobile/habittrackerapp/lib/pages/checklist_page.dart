import 'package:flutter/material.dart';
import '../http_logs_repository.dart';
import '../log.dart';

class ChecklistPage extends StatefulWidget {
  const ChecklistPage({super.key});

  @override
  State<ChecklistPage> createState() => _ChecklistPageState();
}

class _ChecklistPageState extends State<ChecklistPage> {
    final logRepo = HttpLogRepository(1);
    Future<List<Log>> logs = logRepo.read(); 
  final List<Map<String, dynamic>> _tasks = [
    {'name': 'Morning Meditation', 'completed': true, 'time': '6:00 AM'},
    {'name': 'Exercise', 'completed': true, 'time': '7:00 AM'},
    {'name': 'Drink Water (8 glasses)', 'completed': false, 'time': 'Throughout day'},
    {'name': 'Read for 30 minutes', 'completed': true, 'time': '8:00 PM'},
    {'name': 'Journal', 'completed': false, 'time': '9:00 PM'},
    {'name': 'Make Bed', 'completed': true, 'time': '6:30 AM'},
    {'name': 'Practice Guitar', 'completed': false, 'time': '5:00 PM'},
    {'name': 'Cook Healthy Meal', 'completed': true, 'time': '6:00 PM'},
  ];

  @override
  Widget build(BuildContext context) {
    final completedCount = _tasks.where((task) => task['completed']).length;
    final totalCount = _tasks.length;

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          color: Theme.of(context).colorScheme.primaryContainer,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Daily Routine',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              Text(
                '$completedCount / $totalCount',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: _tasks.length,
            itemBuilder: (context, index) {
              final task = _tasks[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                child: CheckboxListTile(
                  title: Text(
                    task['name'],
                    style: TextStyle(
                      decoration: task['completed'] ? TextDecoration.lineThrough : null,
                      color: task['completed'] ? Colors.grey : null,
                    ),
                  ),
                  subtitle: Text(task['time']),
                  value: task['completed'],
                  onChanged: (bool? value) {
                    setState(() {
                      task['completed'] = value ?? false;
                    });
                  },
                  secondary: Icon(
                    task['completed'] ? Icons.check_circle : Icons.radio_button_unchecked,
                    color: task['completed'] ? Colors.green : Colors.grey,
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
