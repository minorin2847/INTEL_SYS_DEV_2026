import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConfig {
  static const int defaultPort = 8002;

  /// Default API base URL based on running platform.
  static String getDefaultBaseUrl() {
    if (kIsWeb) {
      return 'http://localhost:$defaultPort';
    }
    if (Platform.isAndroid) {
      // 10.0.2.2 is the special alias to your host loopback interface in Android emulator
      return 'http://10.0.2.2:$defaultPort';
    }
    // iOS simulator / macOS desktop
    return 'http://localhost:$defaultPort';
  }

  static const List<Map<String, String>> presetUrls = [
    {'name': 'Android Emulator (10.0.2.2)', 'url': 'http://10.0.2.2:8002'},
    {'name': 'Localhost / iOS Simulator', 'url': 'http://localhost:8002'},
    {'name': 'Local LAN IP (Wi-Fi)', 'url': 'http://192.168.1.100:8002'},
  ];
}
