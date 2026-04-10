import 'package:flutter/material.dart';
import '../../../app/routes.dart';
import '../../../core/storage/local_storage.dart';
import '../services/auth_service.dart';

class OtpVerifyScreen extends StatefulWidget {
  const OtpVerifyScreen({super.key});

  @override
  State<OtpVerifyScreen> createState() => _OtpVerifyScreenState();
}

class _OtpVerifyScreenState extends State<OtpVerifyScreen> {
  final TextEditingController otpController = TextEditingController();
  final AuthService authService = AuthService();

  bool isLoading = false;
  String mobileNo = '';

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args != null) {
      mobileNo = args.toString();
    }
  }

  Future<void> _verifyOtp() async {
    final otp = otpController.text.trim();

    if (otp.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter OTP')),
      );
      return;
    }

    setState(() => isLoading = true);

    final result = await authService.verifyOtp(
      mobileNo: mobileNo,
      otp: otp,
    );

    setState(() => isLoading = false);

    if (!mounted) return;

    if (result['statusCode'] == 200 || result['statusCode'] == 201) {
      final token = result['data']['access_token']?.toString() ?? '';

      if (token.isNotEmpty) {
        await LocalStorage.saveToken(token);
      }

      Navigator.pushNamedAndRemoveUntil(
        context,
        AppRoutes.dashboard,
        (route) => false,
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result['data']['message']?.toString() ?? 'OTP verification failed')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Verify OTP'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 20),
            Text(
              'OTP sent to $mobileNo',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: otpController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Enter OTP',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.lock),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: isLoading ? null : _verifyOtp,
                child: isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Verify OTP'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}