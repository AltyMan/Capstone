import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  final int completedCount;
  final int totalCount;

  const HomePage({
    super.key,
    this.completedCount = 0,
    this.totalCount = 0,
  });

  @override
  Widget build(BuildContext context) {
    final rate = totalCount == 0 ? 0 : ((completedCount / totalCount) * 100).round();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Welcome to Habit Tracker',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          _buildStatCard('Current Streak', '7 days', Icons.local_fire_department, Colors.orange),
          const SizedBox(height: 12),
          _buildStatCard('Tasks Completed Today', '$completedCount / $totalCount', Icons.check_circle, Colors.green),
          const SizedBox(height: 12),
          _buildStatCard('Completion Rate', '$rate%', Icons.trending_up, Colors.blue),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(icon, color: color, size: 40),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, color: Colors.grey)),
                const SizedBox(height: 4),
                Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}