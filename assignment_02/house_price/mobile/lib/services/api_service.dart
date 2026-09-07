import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/health_status.dart';
import '../models/prediction_result.dart';
import '../models/property_input.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiService {
  final http.Client _client = http.Client();
  final Duration _timeout = const Duration(seconds: 10);

  Future<HealthStatus> checkHealth(String baseUrl) async {
    final uri = Uri.parse('$baseUrl/healthz');
    try {
      final response = await _client.get(uri).timeout(_timeout);
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return HealthStatus.fromJson(data);
      }
      return HealthStatus.disconnected();
    } catch (_) {
      return HealthStatus.disconnected();
    }
  }

  Future<PredictionResult> predictPrice(String baseUrl, PropertyInput input) async {
    final uri = Uri.parse('$baseUrl/predict');
    final body = json.encode(input.toJson());

    try {
      final response = await _client.post(
        uri,
        headers: {
          'Content-Type': 'application/json; charset=UTF-8',
          'ngrok-skip-browser-warning': 'true',
        },
        body: body,
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return PredictionResult.fromJson(data);
      }

      if (response.statusCode == 422) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final detail = data['detail'];
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          final msg = first['msg'] ?? 'Dữ liệu không hợp lệ';
          final loc = (first['loc'] as List?)?.join('.') ?? '';
          throw ApiException('Lỗi dữ liệu ($loc): $msg', 422);
        }
        throw ApiException('Dữ liệu không hợp lệ (422)', 422);
      }

      if (response.statusCode == 503) {
        throw ApiException(
          'Mô hình chưa được nạp trên máy chủ (503). Hãy kiểm tra file model_pipeline.joblib.',
          503,
        );
      }

      throw ApiException('Máy chủ phản hồi mã lỗi ${response.statusCode}', response.statusCode);
    } on SocketException catch (e) {
      throw ApiException(
        'Không thể kết nối đến máy chủ tại $baseUrl. Vui lòng kiểm tra địa chỉ IP và xem FastAPI đã chạy chưa ($e).',
      );
    } on TimeoutException {
      throw ApiException('Yêu cầu tới $baseUrl bị hết thời gian (Timeout 10s).');
    } on FormatException {
      throw ApiException('Phản hồi từ máy chủ không đúng định dạng JSON.');
    }
  }

  void dispose() {
    _client.close();
  }
}
