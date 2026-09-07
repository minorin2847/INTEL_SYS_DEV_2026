import 'package:intl/intl.dart';

class CurrencyFormatter {
  static final NumberFormat _millionFormat = NumberFormat('#,##0.0', 'vi_VN');
  static final NumberFormat _billionFormat = NumberFormat('#,##0.00', 'vi_VN');

  /// Format price given in million VND into natural Vietnamese notation.
  static String formatVND(double priceInMillion) {
    if (priceInMillion >= 1000) {
      final billion = priceInMillion / 1000.0;
      return '${_billionFormat.format(billion)} tỷ VNĐ';
    }
    return '${_millionFormat.format(priceInMillion)} triệu VNĐ';
  }

  /// Format price per square meter.
  static String formatPerM2(double? ppm2) {
    if (ppm2 == null || ppm2 <= 0) return 'N/A';
    return '${_millionFormat.format(ppm2)} tr/m²';
  }
}
