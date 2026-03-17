import 'package:flutter/material.dart';
import '../http_logs_repository.dart';
import '../log.dart';

class ChecklistPage extends StatefulWidget {
  final void Function(int completed, int total)? onCountChanged;
  const ChecklistPage({super.key, this.onCountChanged});

  @override
  State<ChecklistPage> createState() => _ChecklistPageState();
}

class _ChecklistPageState extends State<ChecklistPage> {
  final logRepo = HttpLogRepository(1);
  late Future<List<Log>> logs = logRepo.read();
  List<Log> _tasks = [];

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Log>>(
      future: logs,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}'));
        }

        if (_tasks.isEmpty) {
          _tasks = snapshot.data!;
        }

        final completedCount = _tasks.where((log) => log.state == 'completed').length;
        final totalCount = _tasks.length;

        WidgetsBinding.instance.addPostFrameCallback((_) {
          widget.onCountChanged?.call(completedCount, totalCount);
        });

        return Column(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              color: Theme.of(context).colorScheme.primaryContainer,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Daily Logs',
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
                  final log = _tasks[index];
                  final isCompleted = log.state == 'completed';
                  return Card(
                    margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    child: CheckboxListTile(
                      title: Text(
                        log.habit_name,
                        style: TextStyle(
                          decoration: isCompleted ? TextDecoration.lineThrough : null,
                          color: isCompleted ? Colors.grey : null,
                        ),
                      ),
                      subtitle: Text(log.timestamp),
                      value: isCompleted,
                      onChanged: (bool? value) async {
                        final newState = (value ?? false) ? 'completed' : 'missed';
                        final success = await logRepo.updateField(log.id, 'state', newState);
                        if (success) {
                          setState(() {
                            _tasks[index] = Log(
                              id: log.id,
                              user_id: log.user_id,
                              habit_name: log.habit_name,
                              timestamp: log.timestamp,
                              state: newState,
                              self_reported: log.self_reported,
                            );
                          });
                          final completed = _tasks.where((l) => l.state == 'completed').length;
                          widget.onCountChanged?.call(completed, _tasks.length);
                        }
                      },
                      secondary: Icon(
                        isCompleted ? Icons.check_circle : Icons.radio_button_unchecked,
                        color: isCompleted ? Colors.green : Colors.grey,
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }
}
