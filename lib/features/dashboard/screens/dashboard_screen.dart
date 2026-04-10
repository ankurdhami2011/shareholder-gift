import 'package:flutter/material.dart';
import '../../../app/routes.dart';
import '../../../core/storage/local_storage.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  Future<void> _logout(BuildContext context) async {
    await LocalStorage.clearAll();
    if (!context.mounted) return;
    Navigator.pushNamedAndRemoveUntil(
      context,
      AppRoutes.login,
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final cardStyle = BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      boxShadow: const [
        BoxShadow(
          blurRadius: 6,
          color: Colors.black12,
          offset: Offset(0, 2),
        ),
      ],
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            onPressed: () => _logout(context),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: cardStyle,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome Shareholder',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text('Gift Cycle: 2026-27'),
                  Text('Status: Eligible'),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Container(
              decoration: cardStyle,
              child: ListTile(
                leading: const Icon(Icons.card_giftcard),
                title: const Text('Apply for Gift'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {},
              ),
            ),
            const SizedBox(height: 12),
            Container(
              decoration: cardStyle,
              child: ListTile(
                leading: const Icon(Icons.list_alt),
                title: const Text('My Requests'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  Navigator.pushNamed(context, AppRoutes.myRequests);
                },
              ),
            ),
            const SizedBox(height: 12),
            Container(
              decoration: cardStyle,
              child: const ListTile(
                leading: Icon(Icons.local_shipping),
                title: Text('Track Delivery'),
                trailing: Icon(Icons.arrow_forward_ios),
              ),
            ),
          ],
        ),
      ),
    );
  }
}