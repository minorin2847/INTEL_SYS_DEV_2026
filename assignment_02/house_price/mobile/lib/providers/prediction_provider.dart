import 'package:flutter/foundation.dart';
import '../core/constants/api_config.dart';
import '../models/health_status.dart';
import '../models/prediction_result.dart';
import '../models/property_input.dart';
import '../services/api_service.dart';

class PredictionProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  String _baseUrl = ApiConfig.getDefaultBaseUrl();
  HealthStatus? _healthStatus;
  bool _isHealthLoading = false;
  bool _isSubmitting = false;
  PredictionResult? _result;
  String? _errorMessage;

  // Preset definitions for fast demo / grading
  final List<Map<String, dynamic>> presets = [
    {
      'title': 'Nhà phố Rạch Giá',
      'desc': '78.7 m², 2 tầng, 3 PN, An Giang',
      'data': PropertyInput(
        area: 78.7,
        width: 4.0,
        length: 19.6,
        bedrooms: 3,
        bathrooms: 2,
        floors: 2,
        alleyWidth: 3.5,
        agentListingCount: 1,
        propertyType: 'Nhà riêng',
        position: 'Đường chính',
        direction: 'Nam',
        roadType: 'Đường nhựa',
        province: 'an-giang',
        agentRole: 'Chính chủ',
        ward: 'Phường An Hòa',
        district: 'Rạch Giá',
      ),
    },
    {
      'title': 'Căn hộ Quận 7',
      'desc': '65.5 m², 2 PN, 2 PT, TP.HCM',
      'data': PropertyInput(
        area: 65.5,
        bedrooms: 2,
        bathrooms: 2,
        floors: 1,
        propertyType: 'Căn hộ chung cư',
        position: 'Đường chính',
        direction: 'Đông Nam',
        province: 'tp-ho-chi-minh',
        agentRole: 'Môi giới',
        district: 'Quận 7',
      ),
    },
    {
      'title': 'Đất Gia Lâm (Hà Nội)',
      'desc': '100 m², mặt tiền 5m',
      'data': PropertyInput(
        area: 100.0,
        width: 5.0,
        length: 20.0,
        propertyType: 'Đất',
        position: 'Đường chính',
        direction: 'Tây Bắc',
        roadType: 'Đường nhựa',
        province: 'ha-noi',
        agentRole: 'Chính chủ',
        district: 'Gia Lâm',
      ),
    },
    {
      'title': 'Tối thiểu (85m²)',
      'desc': 'Chỉ nhập diện tích 85 m²',
      'data': PropertyInput(area: 85.0),
    },
  ];

  String get baseUrl => _baseUrl;
  HealthStatus? get healthStatus => _healthStatus;
  bool get isHealthLoading => _isHealthLoading;
  bool get isSubmitting => _isSubmitting;
  PredictionResult? get result => _result;
  String? get errorMessage => _errorMessage;

  PredictionProvider() {
    checkHealth();
  }

  void setBaseUrl(String newUrl) {
    if (newUrl.trim().isEmpty) return;
    _baseUrl = newUrl.trim().replaceAll(RegExp(r'/+$'), '');
    notifyListeners();
    checkHealth();
  }

  Future<void> checkHealth() async {
    _isHealthLoading = true;
    notifyListeners();

    try {
      _healthStatus = await _apiService.checkHealth(_baseUrl);
    } catch (_) {
      _healthStatus = HealthStatus.disconnected();
    } finally {
      _isHealthLoading = false;
      notifyListeners();
    }
  }

  Future<void> predict(PropertyInput input) async {
    _isSubmitting = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _result = await _apiService.predictPrice(_baseUrl, input);
    } on ApiException catch (e) {
      _errorMessage = e.message;
    } catch (e) {
      _errorMessage = 'Lỗi không xác định: $e';
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }

  void clearResult() {
    _result = null;
    _errorMessage = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _apiService.dispose();
    super.dispose();
  }
}
