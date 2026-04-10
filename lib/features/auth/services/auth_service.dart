import 'dart:convert';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/api_client.dart';

class AuthService {
  Future<Map<String, dynamic>> sendOtp(String mobileNo) async {
    final response = await ApiClient.post(
      ApiConstants.sendOtp,
      body: {'mobile_no': mobileNo},
    );

    return {
      'statusCode': response.statusCode,
      'data': jsonDecode(response.body),
    };
  }

  Future<Map<String, dynamic>> verifyOtp({
    required String mobileNo,
    required String otp,
  }) async {
    final response = await ApiClient.post(
      ApiConstants.verifyOtp,
      body: {
        'mobile_no': mobileNo,
        'otp': otp,
      },
    );

    return {
      'statusCode': response.statusCode,
      'data': jsonDecode(response.body),
    };
  }
}