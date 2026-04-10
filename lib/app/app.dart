import 'package:flutter/material.dart';
import 'routes.dart';
import 'theme.dart';
import '../features/splash/splash_screen.dart';

class ShareholderGiftApp extends StatelessWidget {
  const ShareholderGiftApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Shareholder Gift',
      theme: AppTheme.lightTheme,
      routes: AppRoutes.routes,
      home: const SplashScreen(),
    );
  }
}