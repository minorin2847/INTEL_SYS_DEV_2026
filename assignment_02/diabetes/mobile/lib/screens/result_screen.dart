import 'package:flutter/material.dart';

import '../models.dart';
import 'whatif_screen.dart';

// Palette mirrored from diabetes/web/src/styles.css
const _accent = Color(0xFF4F46E5);
const _danger = Color(0xFFEF4444);
const _dangerBg = Color(0xFFFEF2F2);
const _dangerText = Color(0xFFB91C1C);
const _success = Color(0xFF10B981);
const _successBg = Color(0xFFF0FDF4);
const _successText = Color(0xFF047857);

/// Screen 2 — the result: hero card, probability meter, SHAP factor bars,
/// similar cases, and the counterfactual sentence. Styling follows the web
/// app's `.hero-card` / `.meter` / `.shap-bar` treatment.
class ResultScreen extends StatelessWidget {
  final PredictResult result;
  final Map<String, dynamic> payload;
  const ResultScreen({super.key, required this.result, required this.payload});

  @override
  Widget build(BuildContext context) {
    final r = result;
    final pct = (r.probability * 100).round();
    final bad = r.probability >= 0.5;
    final elevated = !bad && r.probability >= 0.2;

    final String badgeText;
    final String heroTitle;
    if (bad) {
      badgeText = 'HIGH RISK';
      heroTitle = 'You have a high risk of diabetes';
    } else if (elevated) {
      badgeText = 'ELEVATED RISK';
      heroTitle = 'Your risk is elevated compared to the average';
    } else {
      badgeText = 'LOW RISK';
      heroTitle = 'Your risk of diabetes is relatively low';
    }

    final maxAbs = r.factors.isEmpty
        ? 0.01
        : r.factors
            .map((x) => x.value.abs())
            .fold<double>(0.01, (a, b) => a > b ? a : b);

    return Scaffold(
      appBar: AppBar(title: const Text('Result')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _HeroCard(
            badgeText: badgeText,
            title: heroTitle,
            pct: pct,
            bad: bad,
            elevated: elevated,
          ),
          const SizedBox(height: 12),

          // --- probability meter ---
          _SectionCard(
            title: 'Risk probability',
            child: _Meter(pct: pct, bad: bad),
          ),

          for (final w in r.warnings)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Row(children: [
                const Icon(Icons.warning_amber, size: 18),
                const SizedBox(width: 6),
                Expanded(child: Text(w, style: const TextStyle(fontSize: 12))),
              ]),
            ),
          const SizedBox(height: 8),
          Text(
            'Completeness ${(r.completeness * 100).round()}% · BMI source: ${r.bmiSource}\n'
            'This is a screening aid, not a diagnosis.',
            style: const TextStyle(fontSize: 12, color: Colors.black54),
          ),
          const SizedBox(height: 12),

          // --- SHAP ---
          _SectionCard(
            title: 'Why this score',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (r.factors.isEmpty)
                  const Text('Explanation not available.',
                      style: TextStyle(color: Colors.black54))
                else
                  ...r.factors.take(8).map((f) => _FactorBar(
                        label: f.label,
                        value: f.value,
                        maxAbs: maxAbs,
                      )),
                const SizedBox(height: 4),
                const Text('Red raises the estimate, green lowers it.',
                    style: TextStyle(fontSize: 12, color: Colors.black54)),
              ],
            ),
          ),

          // --- similar cases ---
          _SectionCard(
            title: 'People similar to you',
            child: r.similarAvailable
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${r.similarWithDiabetes} of your ${r.similarK} closest '
                        'matches in the survey data had diabetes or pre-diabetes.',
                      ),
                      const SizedBox(height: 8),
                      ...r.neighbors.map((n) => ListTile(
                            dense: true,
                            contentPadding: EdgeInsets.zero,
                            leading: Icon(
                              n.outcome.startsWith('diabetes')
                                  ? Icons.circle
                                  : Icons.circle_outlined,
                              size: 14,
                              color: n.outcome.startsWith('diabetes')
                                  ? _danger
                                  : _success,
                            ),
                            title: Text(n.profile,
                                style: const TextStyle(fontSize: 13)),
                            subtitle: Text(
                                '${n.outcome} · proximity ${n.proximity.toStringAsFixed(2)}',
                                style: const TextStyle(fontSize: 11)),
                          )),
                    ],
                  )
                : const Text('Similar-case index not available on the API.',
                    style: TextStyle(color: Colors.black54)),
          ),

          // --- counterfactual + what-if link ---
          _SectionCard(
            title: 'What could change the estimate',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (r.counterfactual != null &&
                    (r.counterfactual!['changes'] as List).isNotEmpty)
                  _CounterfactualText(r.counterfactual!),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  icon: const Icon(Icons.tune),
                  label: const Text('Explore modifiable factors'),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => WhatIfScreen(result: r, payload: payload),
                    ),
                  ),
                ),
                if (r.caveat != null) ...[
                  const SizedBox(height: 12),
                  Text('⚠️ ${r.caveat}',
                      style:
                          const TextStyle(fontSize: 12, color: Colors.black54)),
                ],
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

/// `.hero-card` — 2px coloured border, tinted background, uppercase status pill,
/// large percentage, and a subtitle sentence.
class _HeroCard extends StatelessWidget {
  final String badgeText;
  final String title;
  final int pct;
  final bool bad;
  final bool elevated;
  const _HeroCard({
    required this.badgeText,
    required this.title,
    required this.pct,
    required this.bad,
    required this.elevated,
  });

  @override
  Widget build(BuildContext context) {
    final Color border = bad
        ? _danger
        : elevated
            ? Colors.grey.shade300
            : _success;
    final Color bg = bad
        ? _dangerBg
        : elevated
            ? Colors.white
            : _successBg;
    final Color titleColor = bad
        ? _dangerText
        : elevated
            ? Colors.black87
            : _successText;
    final Color badgeBg = bad
        ? const Color(0xFFFEE2E2)
        : elevated
            ? Colors.grey.shade100
            : const Color(0xFFD1FAE5);
    final Color badgeFg = bad
        ? _danger
        : elevated
            ? Colors.black54
            : _success;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border, width: 2),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: badgeBg,
              border: Border.all(color: badgeFg),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Text(
              badgeText,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
                color: badgeFg,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            title,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3,
              color: titleColor,
            ),
          ),
          const SizedBox(height: 6),
          Text.rich(
            TextSpan(
              text: 'Estimated probability: ',
              style: const TextStyle(fontSize: 15, color: Colors.black87),
              children: [
                TextSpan(
                  text: '$pct%',
                  style: const TextStyle(fontWeight: FontWeight.w800),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// `.meter` — rounded track with a coloured fill and a 0/50/100 scale.
class _Meter extends StatelessWidget {
  final int pct;
  final bool bad;
  const _Meter({required this.pct, required this.bad});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: Stack(
            children: [
              Container(height: 14, color: const Color(0xFFE5E7EB)),
              LayoutBuilder(
                builder: (context, c) => Container(
                  height: 14,
                  width: c.maxWidth * (pct / 100).clamp(0.0, 1.0),
                  decoration: BoxDecoration(
                    color: bad ? _danger : _success,
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('0%', style: TextStyle(fontSize: 12, color: Colors.black54)),
            Text('50%', style: TextStyle(fontSize: 12, color: Colors.black54)),
            Text('100%', style: TextStyle(fontSize: 12, color: Colors.black54)),
          ],
        ),
      ],
    );
  }
}

/// `.card` — white surface, rounded corners, subtle border, section title.
class _SectionCard extends StatelessWidget {
  final String title;
  final Widget child;
  const _SectionCard({required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: Colors.grey.shade200),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  fontSize: 15, fontWeight: FontWeight.w700, color: _accent)),
          const SizedBox(height: 10),
          child,
        ],
      ),
    );
  }
}

class _FactorBar extends StatelessWidget {
  final String label;
  final double value;
  final double maxAbs;
  const _FactorBar(
      {required this.label, required this.value, required this.maxAbs});

  @override
  Widget build(BuildContext context) {
    final frac = (value.abs() / maxAbs).clamp(0.0, 1.0);
    final positive = value > 0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$label  (${value >= 0 ? '+' : ''}${value.toStringAsFixed(3)})',
              style: const TextStyle(fontSize: 12)),
          const SizedBox(height: 3),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: Align(
              alignment: Alignment.centerLeft,
              child: FractionallySizedBox(
                widthFactor: frac == 0 ? 0.01 : frac,
                child: Container(
                  height: 10,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: positive
                          ? const [_danger, Color(0xFFF43F5E)] // red → rose
                          : const [_success, Color(0xFF14B8A6)], // green → teal
                    ),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CounterfactualText extends StatelessWidget {
  final Map<String, dynamic> cf;
  const _CounterfactualText(this.cf);
  @override
  Widget build(BuildContext context) {
    final changes = (cf['changes'] as List)
        .map((c) => '${c['label']} → ${c['to']}')
        .join(', ');
    final feasible = cf['feasible'] == true;
    final fromPct = ((cf['from_risk'] as num) * 100).round();
    final toPct = ((cf['to_risk'] as num) * 100).round();
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFEEF2FB),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        'If $changes, the estimate moves from $fromPct% (${cf['from_band']}) '
        'to $toPct% (${cf['to_band']}) — '
        '${feasible ? 'would reach' : 'would still not reach'} the '
        '${cf['target_band']} band.',
        style: const TextStyle(fontSize: 13),
      ),
    );
  }
}
