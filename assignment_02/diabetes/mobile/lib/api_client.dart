// REST client for the diabetes screening API. The mobile app performs no inference
// itself — every screen is a view over these endpoints.
//
// Base URL: pass --dart-define=API_URL=http://<host>:8000 at build/run time.
// Default 10.0.2.2 is the Android emulator's alias for the host machine's localhost.

import 'dart:convert';
import 'package:http/http.dart' as http;

import 'models.dart';

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => message;
}

class ApiClient {
  static const String baseUrl =
      String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000');

  final http.Client _http = http.Client();

  Uri _u(String path, [Map<String, dynamic>? q]) =>
      Uri.parse('$baseUrl$path').replace(
        queryParameters: q?.map((k, v) => MapEntry(k, '$v')),
      );

  Future<bool> health() async {
    try {
      final r = await _http
          .get(_u('/healthz'))
          .timeout(const Duration(seconds: 5));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<Question>> questions() async {
    final r = await _http.get(_u('/questions'));
    _check(r);
    final body = jsonDecode(r.body) as Map<String, dynamic>;
    return (body['questions'] as List)
        .map((q) => Question.fromJson((q as Map).cast<String, dynamic>()))
        .toList();
  }

  Future<Map<String, dynamic>> modelInfo() async {
    final r = await _http.get(_u('/model-info'));
    _check(r);
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<PredictResult> predict(
    Map<String, dynamic> payload, {
    String include = 'explain,similar,whatif,counterfactual',
  }) async {
    final r = await _http.post(
      _u('/predict', {'include': include}),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );
    if (r.statusCode == 422) {
      throw ApiException('The server rejected the input: ${r.body}');
    }
    _check(r);
    return PredictResult.fromJson(
        jsonDecode(r.body) as Map<String, dynamic>);
  }

  Future<List<HistoryItem>> history(String session) async {
    final r = await _http.get(_u('/history', {'session': session}));
    _check(r);
    final body = jsonDecode(r.body) as Map<String, dynamic>;
    return (body['screenings'] as List)
        .map((h) => HistoryItem.fromJson((h as Map).cast<String, dynamic>()))
        .toList();
  }

  void _check(http.Response r) {
    if (r.statusCode >= 400) {
      throw ApiException('API error ${r.statusCode}: ${r.body}');
    }
  }
}
