import 'package:flutter/material.dart';

class MyRequestsScreen extends StatelessWidget {
  const MyRequestsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final items = [
      {
        'requestNo': 'REQ001',
        'status': 'PENDING',
        'date': '07-04-2026',
      },
      {
        'requestNo': 'REQ002',
        'status': 'SHIPPED',
        'date': '05-04-2026',
      },
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Requests'),
      ),
      body: ListView.builder(
        itemCount: items.length,
        itemBuilder: (context, index) {
          final item = items[index];
          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: ListTile(
              title: Text(item['requestNo']!),
              subtitle: Text('Date: ${item['date']}'),
              trailing: Text(item['status']!),
            ),
          );
        },
      ),
    );
  }
}