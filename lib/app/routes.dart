import 'package:flutter/material.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/otp_verify_screen.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/requests/screens/my_requests_screen.dart';

class AppRoutes {
  static const String login = '/login';
  static const String otpVerify = '/otp-verify';
  static const String dashboard = '/dashboard';
  static const String myRequests = '/my-requests';

  static Map<String, WidgetBuilder> get routes => {
        login: (_) => const LoginScreen(),
        otpVerify: (_) => const OtpVerifyScreen(),
        dashboard: (_) => const DashboardScreen(),
        myRequests: (_) => const MyRequestsScreen(),
      };
}