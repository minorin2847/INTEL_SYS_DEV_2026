// Data models mirroring the API's JSON responses.

class Question {
  final String section;
  final String field;
  final String type; // "yesno" | "choice" | "number"
  final String label;
  final bool required;
  final bool modifiable;
  final String? note;
  final num? min;
  final num? max;
  final List<List<dynamic>> options; // [[code, label], ...]

  Question({
    required this.section,
    required this.field,
    required this.type,
    required this.label,
    required this.required,
    required this.modifiable,
    this.note,
    this.min,
    this.max,
    this.options = const [],
  });

  factory Question.fromJson(Map<String, dynamic> j) => Question(
        section: j['section'] as String,
        field: j['field'] as String,
        type: j['type'] as String,
        label: j['label'] as String,
        required: j['required'] == true,
        modifiable: j['modifiable'] == true,
        note: j['note'] as String?,
        min: j['min'] as num?,
        max: j['max'] as num?,
        options: ((j['options'] as List?) ?? [])
            .map((o) => (o as List).toList())
            .toList(),
      );
}

class ShapFactor {
  final String label;
  final double value;
  final String direction;
  ShapFactor(this.label, this.value, this.direction);
  factory ShapFactor.fromJson(Map<String, dynamic> j) => ShapFactor(
        j['label'] as String,
        (j['value'] as num).toDouble(),
        j['direction'] as String,
      );
}

class SimilarCase {
  final String profile;
  final String outcome;
  final double proximity;
  SimilarCase(this.profile, this.outcome, this.proximity);
  factory SimilarCase.fromJson(Map<String, dynamic> j) => SimilarCase(
        j['profile'] as String,
        j['outcome'] as String,
        (j['proximity'] as num).toDouble(),
      );
}

class WhatIfFactor {
  final String feature;
  final String label;
  final double newRisk;
  final double delta;
  WhatIfFactor(this.feature, this.label, this.newRisk, this.delta);
  factory WhatIfFactor.fromJson(Map<String, dynamic> j) => WhatIfFactor(
        j['feature'] as String,
        j['label'] as String,
        (j['new_risk'] as num).toDouble(),
        (j['delta'] as num).toDouble(),
      );
}

class PredictResult {
  final double probability;
  final String band;
  final String bandLabel;
  final List<double>? uncertaintyBand;
  final double completeness;
  final List<String> imputedFields;
  final String bmiSource;
  final List<String> warnings;
  final List<ShapFactor> factors;
  final bool similarAvailable;
  final int similarWithDiabetes;
  final int similarK;
  final List<SimilarCase> neighbors;
  final List<WhatIfFactor> whatIfFactors;
  final List<Map<String, dynamic>> bmiSweep;
  final double? currentBmi;
  final Map<String, dynamic>? counterfactual;
  final String? caveat;

  PredictResult({
    required this.probability,
    required this.band,
    required this.bandLabel,
    required this.uncertaintyBand,
    required this.completeness,
    required this.imputedFields,
    required this.bmiSource,
    required this.warnings,
    required this.factors,
    required this.similarAvailable,
    required this.similarWithDiabetes,
    required this.similarK,
    required this.neighbors,
    required this.whatIfFactors,
    required this.bmiSweep,
    required this.currentBmi,
    required this.counterfactual,
    required this.caveat,
  });

  factory PredictResult.fromJson(Map<String, dynamic> j) {
    final explain = (j['explain'] as Map?)?.cast<String, dynamic>();
    final similar = (j['similar'] as Map?)?.cast<String, dynamic>();
    final whatif = (j['whatif'] as Map?)?.cast<String, dynamic>();
    return PredictResult(
      probability: (j['probability'] as num).toDouble(),
      band: j['band'] as String,
      bandLabel: j['band_label'] as String,
      uncertaintyBand: (j['uncertainty_band'] as List?)
          ?.map((e) => (e as num).toDouble())
          .toList(),
      completeness: (j['completeness'] as num).toDouble(),
      imputedFields:
          ((j['imputed_fields'] as List?) ?? []).map((e) => e.toString()).toList(),
      bmiSource: (j['bmi_source'] ?? '') as String,
      warnings: ((j['warnings'] as List?) ?? []).map((e) => e.toString()).toList(),
      factors: (((explain?['factors']) as List?) ?? [])
          .map((f) => ShapFactor.fromJson((f as Map).cast<String, dynamic>()))
          .toList(),
      similarAvailable: similar?['available'] == true,
      similarWithDiabetes: (similar?['n_with_diabetes'] as num?)?.toInt() ?? 0,
      similarK: (similar?['k'] as num?)?.toInt() ?? 5,
      neighbors: (((similar?['neighbors']) as List?) ?? [])
          .map((n) => SimilarCase.fromJson((n as Map).cast<String, dynamic>()))
          .toList(),
      whatIfFactors: (((whatif?['factors']) as List?) ?? [])
          .map((w) => WhatIfFactor.fromJson((w as Map).cast<String, dynamic>()))
          .toList(),
      bmiSweep: (((whatif?['bmi_sweep']) as List?) ?? [])
          .map((e) => (e as Map).cast<String, dynamic>())
          .toList(),
      currentBmi: (whatif?['current_bmi'] as num?)?.toDouble(),
      counterfactual:
          (j['counterfactual'] as Map?)?.cast<String, dynamic>(),
      caveat: whatif?['caveat'] as String?,
    );
  }
}

class HistoryItem {
  final DateTime time;
  final double probability;
  final String band;
  final double completeness;
  HistoryItem(this.time, this.probability, this.band, this.completeness);
  factory HistoryItem.fromJson(Map<String, dynamic> j) => HistoryItem(
        DateTime.fromMillisecondsSinceEpoch(
            ((j['ts'] as num) * 1000).round()),
        (j['probability'] as num).toDouble(),
        j['band'] as String,
        (j['completeness'] as num).toDouble(),
      );
}
