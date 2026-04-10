import 'package:flutter/material.dart';
import '../../../app/routes.dart';
import '../../../core/storage/local_storage.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController mobileController = TextEditingController();
  final AuthService authService = AuthService();

  bool isLoading = false;

  Future<void> _sendOtp() async {
    final mobile = mobileController.text.trim();

    if (mobile.isEmpty || mobile.length < 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter valid mobile number')),
      );
      return;
    }

    setState(() => isLoading = true);

    final result = await authService.sendOtp(mobile);

    setState(() => isLoading = false);

    if (!mounted) return;

    if (result['statusCode'] == 200 || result['statusCode'] == 201) {
      await LocalStorage.saveMobile(mobile);

      Navigator.pushNamed(
        context,
        AppRoutes.otpVerify,
        arguments: mobile,
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['data']['message']?.toString() ?? 'Failed to send OTP')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 30),
            const Icon(Icons.phone_android, size: 80),
            const SizedBox(height: 20),
            const Text(
              'Login with Mobile Number',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 25),
            TextField(
              controller: mobileController,
              keyboardType: TextInputType.phone,
              maxLength: 10,
              decoration: const InputDecoration(
                labelText: 'Mobile Number',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.phone),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: isLoading ? null : _sendOtp,
                child: isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Send OTP'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}