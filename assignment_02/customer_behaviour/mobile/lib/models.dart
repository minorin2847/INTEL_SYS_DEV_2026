// Data models mirroring the customer-behaviour API's JSON (Sephora is_recommended).

class FormFieldSpec {
  final String field;
  final String type; // "number" | "choice" | "text" | "textarea"
  final String label;
  final String section;
  final bool required;
  final num? min;
  final num? max;
  final String? note;
  final List<String> options;
  final List<List<String>> examples; // [[title, text], ...] for the review field

  FormFieldSpec({
    required this.field,
    required this.type,
    required this.label,
    required this.section,
    required this.required,
    this.min,
    this.max,
    this.note,
    this.options = const [],
    this.examples = const [],
  });

  factory FormFieldSpec.fromJson(Map<String, dynamic> j) => FormFieldSpec(
        field: j['field'] as String,
        type: j['type'] as String,
        label: j['label'] as String,
        section: (j['section'] ?? '') as String,
        required: j['required'] == true,
        min: j['min'] as num?,
        max: j['max'] as num?,
        note: j['note'] as String?,
        options:
            ((j['options'] as List?) ?? []).map((e) => e.toString()).toList(),
        examples: ((j['examples'] as List?) ?? [])
            .map((e) => (e as List).map((x) => x.toString()).toList())
            .toList(),
      );
}

class TermPull {
  final String term;
  final double effect;
  TermPull(this.term, this.effect);
  factory TermPull.fromJson(Map<String, dynamic> j) =>
      TermPull(j['term'].toString(), (j['effect'] as num).toDouble());
}

class PredictResult {
  final String prediction; // "recommend" | "not recommend"
  final double confidence;
  final double pRecommend;
  final double threshold;
  final List<TermPull> termsAgainst; // toward "not recommend"
  final List<TermPull> termsToward; // toward "recommend"
  final Map<String, dynamic> signals;
  final Map<String, dynamic>? contributions;
  final String model;
  final String representation;

  PredictResult({
    required this.prediction,
    required this.confidence,
    required this.pRecommend,
    required this.threshold,
    required this.termsAgainst,
    required this.termsToward,
    required this.signals,
    required this.contributions,
    required this.model,
    required this.representation,
  });

  bool get good => prediction == 'recommend';

  factory PredictResult.fromJson(Map<String, dynamic> j) {
    final terms = (j['review_terms'] as Map?)?.cast<String, dynamic>() ?? {};
    List<TermPull> pull(String k) => ((terms[k] as List?) ?? [])
        .map((e) => TermPull.fromJson((e as Map).cast<String, dynamic>()))
        .toList();
    return PredictResult(
      prediction: j['prediction'] as String,
      confidence: (j['confidence'] as num).toDouble(),
      pRecommend: (j['p_recommend'] as num).toDouble(),
      threshold: (j['threshold'] as num).toDouble(),
      termsAgainst: pull('against'),
      termsToward: pull('toward'),
      signals: (j['signals'] as Map?)?.cast<String, dynamic>() ?? {},
      contributions: (j['contributions'] as Map?)?.cast<String, dynamic>(),
      model: (j['model'] ?? '') as String,
      representation: (j['representation'] ?? '') as String,
    );
  }
}
