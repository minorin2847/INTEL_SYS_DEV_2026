class HealthStatus {
  final String status;
  final bool modelLoaded;
  final String? modelName;
  final int? featuresCount;

  HealthStatus({
    required this.status,
    required this.modelLoaded,
    this.modelName,
    this.featuresCount,
  });

  factory HealthStatus.fromJson(Map<String, dynamic> json) {
    return HealthStatus(
      status: json['status'] as String? ?? 'unknown',
      modelLoaded: json['model_loaded'] as bool? ?? false,
      modelName: json['model_name'] as String?,
      featuresCount: json['features_count'] as int?,
    );
  }

  factory HealthStatus.disconnected() {
    return HealthStatus(
      status: 'disconnected',
      modelLoaded: false,
      modelName: null,
    );
  }
}
