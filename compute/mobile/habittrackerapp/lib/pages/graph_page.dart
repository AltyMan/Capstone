import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../http_habit_repository.dart';
import '../http_logs_repository.dart';
import '../habit.dart';
import '../log.dart';

bool isSuccess(String state) {
  final s = state.toLowerCase();
  return s == "completed" || s == "on";
}

class GraphPage extends StatefulWidget {
  const GraphPage({super.key});

  @override
  State<GraphPage> createState() => _GraphPageState();
}

class _GraphPageState extends State<GraphPage> {
  final habitRepo = HttpHabitRepository(1);
  final logRepo = HttpLogRepository(1);

  List<Habit> habits = [];
  List<Log> logs = [];

  String? selectedHabit;

  /// store sorted days so we can label X axis
  List<DateTime> sortedDays = [];

  @override
  void initState() {
    super.initState();
    loadData();
  }

  Future<void> loadData() async {
    try {
      final h = await habitRepo.read();
      final l = await logRepo.read();

      setState(() {
        habits = h;
        logs = l;

        if (habits.isNotEmpty) {
          selectedHabit = habits.first.name;
        }
      });
    } catch (e) {
      print(e);
    }
  }

  List<FlSpot> buildSpots() {
    if (selectedHabit == null) return [];

    final filtered = logs.where((l) =>
        l.habit_name == selectedHabit &&
        isSuccess(l.state));

    Map<DateTime, int> counts = {};

    for (var log in filtered) {
      try {
        final dt = DateTime.parse(
          log.timestamp.replaceFirst(' ', 'T'),
        );

        final day = DateTime(dt.year, dt.month, dt.day);

        counts[day] = (counts[day] ?? 0) + 1;
      } catch (e) {
        continue;
      }
    }

    sortedDays = counts.keys.toList()..sort();

    List<FlSpot> spots = [];

    for (int i = 0; i < sortedDays.length; i++) {
      final day = sortedDays[i];
      spots.add(
        FlSpot(i.toDouble(), counts[day]!.toDouble()),
      );
    }

    return spots;
  }

  String formatDate(DateTime dt) {
    return "${dt.month}/${dt.day}";
  }

  @override
  Widget build(BuildContext context) {
    final spots = buildSpots();

    final double maxY = spots.isEmpty
    ? 1.0
    : spots.fold(0.0, (max, e) => e.y > max ? e.y : max) + 1.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Habit Analytics"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButton<String>(
              value: selectedHabit,
              hint: const Text("Select habit"),
              isExpanded: true,
              items: habits.map((h) {
                return DropdownMenuItem(
                  value: h.name,
                  child: Text(h.name),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  selectedHabit = value;
                });
              },
            ),

            const SizedBox(height: 24),

            SizedBox(
              height: 250,
              child: spots.isEmpty
                  ? const Center(child: Text("No data"))
                  : LineChart(
                      LineChartData(
                        minX: 0,
                        maxX: spots.length > 1
                            ? spots.length.toDouble() - 1
                            : 1,

                        /// ✅ proper Y scaling
                        minY: 0,
                        maxY: maxY,

                        gridData: const FlGridData(show: true),
                        borderData: FlBorderData(show: true),

                        /// ✅ real axes
                        titlesData: FlTitlesData(
                          leftTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              interval: 1,
                              reservedSize: 32,
                              getTitlesWidget: (value, meta) {
                                return Text(
                                  value.toInt().toString(),
                                  style: const TextStyle(fontSize: 10),
                                );
                              },
                            ),
                          ),
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              interval: 1,
                              getTitlesWidget: (value, meta) {
                                final index = value.toInt();

                                if (index < 0 ||
                                    index >= sortedDays.length) {
                                  return const SizedBox();
                                }

                                return Text(
                                  formatDate(sortedDays[index]),
                                  style: const TextStyle(fontSize: 10),
                                );
                              },
                            ),
                          ),
                          topTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                          rightTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                        ),

                        lineBarsData: [
                          LineChartBarData(
                            spots: spots,
                            isCurved: true,
                            barWidth: 3,
                            dotData: const FlDotData(show: true),
                          ),
                        ],
                      ),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}