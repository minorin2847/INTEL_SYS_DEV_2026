class FeatureContribution {
  final String name;
  final String label;
  final double impactMillion;
  final String direction;
  final double importancePct;

  FeatureContribution({
    required this.name,
    required this.label,
    required this.impactMillion,
    required this.direction,
    required this.importancePct,
  });

  factory FeatureContribution.fromJson(Map<String, dynamic> json) {
    return FeatureContribution(
      name: json['name'] as String? ?? '',
      label: json['label'] as String? ?? (json['name'] as String? ?? ''),
      impactMillion: (json['impact_million'] as num?)?.toDouble() ?? 0,
      direction: json['direction'] as String? ?? 'positive',
      importancePct: (json['importance_pct'] as num?)?.toDouble() ?? 0,
    );
  }
}

class PredictionResult {
  final double predictedPrice;
  final double? pricePerM2;
  final String formattedPriceBillion;
  final String currency;
  final String modelName;
  final String interpretation;
  final List<FeatureContribution> featureContributions;

  PredictionResult({
    required this.predictedPrice,
    this.pricePerM2,
    required this.formattedPriceBillion,
    required this.currency,
    required this.modelName,
    required this.interpretation,
    this.featureContributions = const [],
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      predictedPrice: (json['predicted_price'] as num).toDouble(),
      pricePerM2: json['price_per_m2'] != null ? (json['price_per_m2'] as num).toDouble() : null,
      formattedPriceBillion: json['formatted_price_billion'] as String? ?? '',
      currency: json['currency'] as String? ?? 'million VND',
      modelName: json['model_name'] as String? ?? 'RandomForest',
      interpretation: json['interpretation'] as String? ?? '',
      featureContributions: ((json['feature_contributions'] as List?) ?? [])
          .map((e) => FeatureContribution.fromJson((e as Map).cast<String, dynamic>()))
          .toList(),
    );
  }
}
