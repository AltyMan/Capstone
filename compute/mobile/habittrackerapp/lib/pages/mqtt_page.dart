import 'dart:async';
import 'package:flutter/material.dart';
import '../http_mqtt_repository.dart';
import '../http_habit_repository.dart';
import '../habit.dart';
import '../habitdialog.dart';

class MqttPage extends StatefulWidget {
  const MqttPage({super.key});

  @override
  State<MqttPage> createState() => _MqttPageState();
}

class _MqttPageState extends State<MqttPage> {
  final _repo = HttpMqttRepository();
  final _hrepo = HttpHabitRepository(1);

  List<Map<String, dynamic>> _devices = [];
  late Timer _refreshTimer;


// Need to change this to update automatically, IHN
  final List<Map<String, dynamic>> _automations = [
    {'name': 'Morning Routine', 'enabled': true, 'trigger': 'Wake up detected'},
    {'name': 'Bed Made Alert', 'enabled': true, 'trigger': 'CV detection'},
    {'name': 'Evening Wind Down', 'enabled': false, 'trigger': '9:00 PM'},
  ];

  @override
  void initState() {
    super.initState();
    _loadDevices();

    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _loadDevices();
    });
  }

  @override
  void dispose() {
    _refreshTimer.cancel();
    super.dispose();
  }

  Future<void> _loadDevices() async {
    try {
      final devices = await _repo.getDevices();
      setState(() {
        _devices = devices;
      });
    } catch (e) {
      debugPrint("Failed to load devices: $e");
    }
  }

  Future<void> _toggleDevice(int index, bool value) async {
    final device = _devices[index];
    final newState = value ? 'on' : 'off';

    final success = await _repo.setDevice(device['id'], newState);

    if (success) {
      setState(() {
        _devices[index] = {...device, 'state': newState};
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to update device')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return _devices.isEmpty
        ? const Center(child: CircularProgressIndicator())
        : SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Connected Devices',
                      style:
                          TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.refresh),
                          onPressed: _loadDevices,
                        ),
                        ElevatedButton.icon(
                        // Do I need to make another page here?
                          onPressed: () {
                          // Habit habit = Habit(id: 1, name: "plug2", isDevice: true);
                            // _hrepo.create(habit);

                            showDialog(
                            context: context,
                            builder: (context) => AddHabitDialog(),
                            );
                            
                            // ScaffoldMessenger.of(context).showSnackBar(
                              // const SnackBar(
                                 // content:
                                   //   Text('Added plug2')),
                           // );
                          },
                          icon: const Icon(Icons.add),
                          label: const Text('Add'),
                        ),
                      ],
                    )
                  ],
                ),
                const SizedBox(height: 16),
                ...List.generate(_devices.length, (index) {
                  final device = _devices[index];
                  final isOn =
                      (device['state'] ?? '').toString().toLowerCase() == 'on';

                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ListTile(
                      leading: Icon(
                        _getDeviceIcon(device['type'] ?? ''),
                        color: isOn ? Colors.green : Colors.grey,
                        size: 32,
                      ),
                      title: Text(device['id'] ?? 'Unknown'),
                      subtitle: Text(isOn ? 'On' : 'Off'),
                      trailing: Switch(
                        value: isOn,
                        onChanged: (value) => _toggleDevice(index, value),
                      ),
                    ),
                  );
                }),
                const SizedBox(height: 32),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Automations',
                      style:
                          TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    IconButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                              content: Text(
                                  'Create Automation feature coming soon')),
                        );
                      },
                      icon: const Icon(Icons.add_circle_outline),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ...List.generate(_automations.length, (index) {
                  final automation = _automations[index];

                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: ExpansionTile(
                      leading: Icon(
                        automation['enabled']
                            ? Icons.play_circle_outline
                            : Icons.pause_circle_outline,
                        color:
                            automation['enabled'] ? Colors.blue : Colors.grey,
                      ),
                      title: Text(automation['name']),
                      subtitle: Text('Trigger: ${automation['trigger']}'),
                      trailing: Switch(
                        value: automation['enabled'],
                        onChanged: (value) {
                          setState(() {
                            automation['enabled'] = value;
                          });
                        },
                      ),
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Actions:',
                                  style:
                                      TextStyle(fontWeight: FontWeight.bold)),
                              const SizedBox(height: 8),
                              const Text('• Turn on bedroom light'),
                              const Text('• Set thermostat to 72°F'),
                              const SizedBox(height: 12),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.end,
                                children: [
                                  TextButton(
                                      onPressed: () {},
                                      child: const Text('EDIT')),
                                  TextButton(
                                    onPressed: () {},
                                    child: const Text(
                                      'DELETE',
                                      style: TextStyle(color: Colors.red),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }),
              ],
            ),
          );
  }

  IconData _getDeviceIcon(String type) {
    switch (type) {
      case 'light':
        return Icons.lightbulb;
      case 'thermostat':
        return Icons.thermostat;
      case 'plug':
        return Icons.power;
      default:
        return Icons.device_unknown;
    }
  }
}
