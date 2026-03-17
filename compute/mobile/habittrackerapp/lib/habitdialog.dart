import 'package:flutter/material.dart';
import './habit.dart';
import './http_habit_repository.dart';

class AddHabitDialog extends StatefulWidget {
  @override
  State<AddHabitDialog> createState() => _AddHabitDialogState();
}

class _AddHabitDialogState extends State<AddHabitDialog> {
  final _idController = TextEditingController();
  final _nameController = TextEditingController();
  bool _isDevice = false;
  final _hrepo = HttpHabitRepository(1);

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text("Add Habit"),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [

          TextField(
            controller: _idController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: "ID",
            ),
          ),

          TextField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: "Habit Name",
            ),
          ),

          Row(
            children: [
              Text("Is Device"),
              Spacer(),
              Switch(
                value: _isDevice,
                onChanged: (value) {
                  setState(() {
                    _isDevice = value;
                  });
                },
              ),
            ],
          )
        ],
      ),

      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text("Cancel"),
        ),

        ElevatedButton(
          onPressed: () {
            final habit = Habit(
              id: int.parse(_idController.text),
              name: _nameController.text,
              isDevice: _isDevice,
            );

            print(habit.name); // replace with your logic
            _hrepo.create(habit);
            Navigator.pop(context);
          },
          child: Text("Save"),
        ),
      ],
    );
  }
}
