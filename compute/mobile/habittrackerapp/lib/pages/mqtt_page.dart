import 'package:flutter/material.dart';

class MqttPage extends StatefulWidget {
  const MqttPage({super.key});

  @override
  State<MqttPage> createState() => _MqttPageState();
}

class _MqttPageState extends State<MqttPage> {
  // Static demo data - will be replaced with real MQTT data later
  final List<Map<String, dynamic>> _devices = [
    {'name': 'Bedroom Light', 'type': 'light', 'status': true},
    {'name': 'Smart Thermostat', 'type': 'thermostat', 'status': false},
    {'name': 'Kitchen Outlet', 'type': 'outlet', 'status': true},
    {'name': 'Desk Lamp', 'type': 'light', 'status': false},
  ];

  final List<Map<String, dynamic>> _automations = [
    {'name': 'Morning Routine', 'enabled': true, 'trigger': 'Wake up detected'},
    {'name': 'Bed Made Alert', 'enabled': true, 'trigger': 'CV detection'},
    {'name': 'Evening Wind Down', 'enabled': false, 'trigger': '9:00 PM'},
  ];

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Connected Devices',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Add new device dialog
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Add Device feature coming soon')),
                  );
                },
                icon: const Icon(Icons.add),
                label: const Text('Add'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...List.generate(_devices.length, (index) {
            final device = _devices[index];
            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: Icon(
                  _getDeviceIcon(device['type']),
                  color: device['status'] ? Colors.green : Colors.grey,
                  size: 32,
                ),
                title: Text(device['name']),
                subtitle: Text(device['status'] ? 'On' : 'Off'),
                trailing: Switch(
                  value: device['status'],
                  onChanged: (value) {
                    setState(() {
                      device['status'] = value;
                    });
                  },
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
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              IconButton(
                onPressed: () {
                  // TODO: Create automation dialog
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Create Automation feature coming soon')),
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
                  automation['enabled'] ? Icons.play_circle_outline : Icons.pause_circle_outline,
                  color: automation['enabled'] ? Colors.blue : Colors.grey,
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
                        const Text('Actions:', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                        const Text('• Turn on bedroom light'),
                        const Text('• Set thermostat to 72°F'),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            TextButton(
                              onPressed: () {
                                // TODO: Edit automation
                              },
                              child: const Text('EDIT'),
                            ),
                            TextButton(
                              onPressed: () {
                                // TODO: Delete automation
                              },
                              child: const Text('DELETE', style: TextStyle(color: Colors.red)),
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
      case 'outlet':
        return Icons.power;
      default:
        return Icons.device_unknown;
    }
  }
}
