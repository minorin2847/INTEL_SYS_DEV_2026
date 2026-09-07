import 'package:flutter/material.dart';

import '../models.dart';
import '../theme.dart';
import '../widgets/primitives.dart';
import '../widgets/result_parts.dart';

class ResultScreen extends StatelessWidget {
  final PredictResult result;
  final Map<String, dynamic> modelInfo;
  const ResultScreen(
      {super.key, required this.result, this.modelInfo = const {}});

  String _pct(double x) => '${(x * 100).round()}%';
  String? _s(dynamic v) => v?.toString();

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final good = result.good;
    final s = result.signals;
    final pRec = (result.pRecommend * 100).round();

    final kv = <(String, String)>[
      ('Skin type', _s(s['skin_type']) ?? '—'),
      ('Category', _s(s['category']) ?? '—'),
      ('Brand', _s(s['brand']) ?? '—'),
      (
        'Price',
        s['price_usd'] == null
            ? '—'
            : '\$${s['price_usd']}'
                '${s['price_tier'] != null ? ' · ${s['price_tier']}' : ''}'
      ),
      ('Product “loves”', _s(s['product_loves']) ?? '—'),
      ('Review length', '${s['review_tokens'] ?? '—'} words'),
    ];

    final against = result.termsAgainst.map((t) => t.term).toList();
    final toward = result.termsToward.map((t) => t.term).toList();

    return Scaffold(
      appBar: AppBar(title: const Text('Prediction')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(Sp.s4, Sp.s4, Sp.s4, Sp.s8),
        children: [
          VerdictBlock(
            good: good,
            badge: good ? 'RECOMMENDS' : "WON’T RECOMMEND",
            title: good
                ? 'This customer would probably recommend it'
                : 'This customer probably would not recommend it',
            subtitle:
                'Chance of a recommendation: $pRec% — we call it “recommends” above '
                '${_pct(result.threshold)}.',
          ),
          const SizedBox(height: Sp.s4),

          // meter
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionLabel('Chance of a recommendation'),
                const SizedBox(height: Sp.s3),
                Meter(
                  value: result.pRecommend,
                  threshold: result.threshold,
                  good: good,
                  leftLabel: 'won’t',
                  rightLabel: 'recommends',
                ),
                
              ],
            ),
          ),
          const SizedBox(height: Sp.s4),

          // signals
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionLabel('What the model saw'),
                const SizedBox(height: Sp.s3),
                KvGrid(kv),
                
              ],
            ),
          ),

          if (against.isNotEmpty || toward.isNotEmpty) ...[
            const SizedBox(height: Sp.s4),
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SectionLabel('Review words that moved the call'),
                  const SizedBox(height: Sp.s3),
                  if (against.isNotEmpty) ...[
                    Text('▼ toward “won’t recommend”',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: c.bad)),
                    const SizedBox(height: 6),
                    ChipRow(against, good: false),
                    const SizedBox(height: Sp.s3),
                  ],
                  if (toward.isNotEmpty) ...[
                    Text('▲ toward “recommends”',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: c.good)),
                    const SizedBox(height: 6),
                    ChipRow(toward, good: true),
                  ],
                ],
              ),
            ),
          ],

          if (result.contributions != null) ...[
            const SizedBox(height: Sp.s4),
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SectionLabel('Why this prediction — each factor’s pull'),
                  const SizedBox(height: Sp.s3),
                  ContribChart(result.contributions!),
                ],
              ),
            ),
          ],

          

          const SizedBox(height: Sp.s5),
          Center(
            child: AppButton(
              label: 'Score another review',
              icon: Icons.arrow_back,
              onPressed: () => Navigator.of(context).pop(),
            ),
          ),
          const SizedBox(height: Sp.s3),
          Text(
            '${result.model} · ${result.representation}',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 10, color: c.textFaint),
          ),
        ],
      ),
    );
  }
}
