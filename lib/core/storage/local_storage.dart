import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class LocalStorage {
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  static const String tokenKey = 'auth_token';
  static const String mobileKey = 'mobile_no';

  static Future<void> saveToken(String token) async {
    await _storage.write(key: tokenKey, value: token);
  }

  static Future<String?> getToken() async {
    return _storage.read(key: tokenKey);
  }

  static Future<void> saveMobile(String mobile) async {
    await _storage.write(key: mobileKey, value: mobile);
  }

  static Future<String?> getMobile() async {
    return _storage.read(key: mobileKey);
  }

  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}