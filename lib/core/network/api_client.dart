import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import '../storage/local_storage.dart';

class ApiClient {
  static Future<Map<String, String>> _headers({bool withAuth = false}) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };

    if (withAuth) {
      final token = await LocalStorage.getToken();
      if (token != null && token.isNotEmpty) {
        headers['Authorization'] = 'Token $token';
      }
    }

    return headers;
  }

  static Future<http.Response> post(
    String endpoint, {
    Map<String, dynamic>? body,
    bool withAuth = false,
  }) async {
    final uri = Uri.parse('${ApiConstants.baseUrl}$endpoint');
    return http.post(
      uri,
      headers: await _headers(withAuth: withAuth),
      body: jsonEncode(body ?? {}),
    );
  }

  static Future<http.Response> get(
    String endpoint, {
    bool withAuth = false,
  }) async {
    final uri = Uri.parse('${ApiConstants.baseUrl}$endpoint');
    return http.get(
      uri,
      headers: await _headers(withAuth: withAuth),
    );
  }
}