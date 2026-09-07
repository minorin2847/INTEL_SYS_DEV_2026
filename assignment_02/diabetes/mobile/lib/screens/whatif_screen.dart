import 'package:flutter/material.dart';

import '../main.dart';
import '../models.dart';

/// Screen 3 — interactive what-if. Shows the modifiable-factor deltas returned with
/// the first prediction, plus a BMI slider that re-scores live against the API.
class WhatIfScreen extends StatefulWidget {
  final PredictResult result;
  final Map<String, dynamic> payload;
  const WhatIfScreen({super.key, required this.result, required this.payload});

  @override
  State<WhatIfScreen> createState() => _WhatIfScreenState();
}

class _WhatIfScreenState extends State<WhatIfScreen> {
  late double _bmi;
  double? _liveRisk;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _bmi = widget.result.currentBmi ??
        (widget.payload['BMI'] as num?)?.toDouble() ??
        28.0;
    _liveRisk = widget.result.probability;
  }

  Future<void> _rescore(double bmi) async {
    setState(() => _loading = true);
    try {
      final p = Map<String, dynamic>.from(widget.payload)..['BMI'] = bmi;
      final res = await api.predict(p, include: '');
      if (mounted) setState(() => _liveRisk = res.probability);
    } catch (_) {
      // keep the last value on error
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final r = widget.result;
    return Scaffold(
      appBar: AppBar(title: const Text('What could change')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('One change at a time',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          if (r.whatIfFactors.isEmpty)
            const Text(
              'You are already at the healthier value for every modifiable factor '
              'in this questionnaire.',
              style: TextStyle(color: Colors.black54),
            )
          else
            ...r.whatIfFactors.map((f) {
              final drop = f.delta < 0;
              return ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                leading: Icon(drop ? Icons.trending_down : Icons.trending_up,
                    color: drop ? Colors.green : Colors.red),
                title: Text(f.label),
                trailing: Text(
                  '${(f.newRisk * 100).round()}%  '
                  '(${f.delta >= 0 ? '+' : ''}${(f.delta * 100).toStringAsFixed(1)} pt)',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              );
            }),
          const Divider(height: 32),

          Text('Body-mass index', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Row(
            children: [
              Text(_bmi.toStringAsFixed(0),
                  style: const TextStyle(
                      fontSize: 28, fontWeight: FontWeight.bold)),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_loading
                        ? 'scoring…'
                        : 'estimated risk ${((_liveRisk ?? r.probability) * 100).round()}%'),
                    LinearProgressIndicator(
                      value: (_liveRisk ?? r.probability).clamp(0.0, 1.0),
                      minHeight: 8,
                    ),
                  ],
                ),
              ),
            ],
          ),
          Slider(
            value: _bmi,
            min: 16,
            max: 55,
            divisions: 39,
            label: _bmi.toStringAsFixed(0),
            onChanged: (v) => setState(() => _bmi = v),
            onChangeEnd: _rescore,
          ),
          const SizedBox(height: 8),
          if (r.caveat != null)
            Text('⚠️ ${r.caveat}',
                style: const TextStyle(fontSize: 12, color: Colors.black54)),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}
