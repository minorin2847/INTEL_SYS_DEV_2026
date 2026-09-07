import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../core/utils/currency_formatter.dart';
import '../models/prediction_result.dart';
import '../models/property_input.dart';
import '../widgets/primitives.dart';
import '../widgets/result_parts.dart';

class ResultCard extends StatelessWidget {
  final PredictionResult result;
  final PropertyInput? input;
  final VoidCallback onClear;

  const ResultCard({
    super.key,
    required this.result,
    this.input,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: EdgeInsets.fromLTRB(16, 16, 16, 32),
      children: [
        VerdictBlock(
          good: true,
          badge: 'VALUATION COMPLETE',
          title: result.formattedPriceBillion,
          subtitle: 'Estimated Total Value: ${result.predictedPrice} million VNĐ',
        ),
        SizedBox(height: 16),
        
        AppCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Property Specs', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
              SizedBox(height: 12),
              KvGrid([
                ('Unit Price', CurrencyFormatter.formatPerM2(result.pricePerM2)),
                ('Usable Area', '${input?.area ?? "N/A"} m²'),
                ('Layout', '${input?.bedrooms ?? 3} Beds · ${input?.bathrooms ?? 2} Baths'),
                ('Location', input?.district ?? 'N/A'),
                ('Property Type', input?.propertyType ?? 'N/A'),
                ('Dimensions', '${input?.width ?? "N/A"}m × ${input?.length ?? "N/A"}m'),
              ]),
            ],
          ),
        ),
        SizedBox(height: 16),

        if (result.featureContributions.isNotEmpty) ...[
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Key Price Drivers (SHAP)',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                const SizedBox(height: 4),
                Text('Features that most strongly influenced the final price.',
                    style: TextStyle(fontSize: 12, color: context.c.textSoft)),
                const SizedBox(height: 12),
                _ShapBars(result.featureContributions),
              ],
            ),
          ),
          SizedBox(height: 20),
        ],

        Center(
          child: AppButton(
            label: 'Estimate Another Property',
            icon: Icons.refresh,
            onPressed: onClear,
          ),
        ),
      ],
    );
  }
}

/// SHAP-style contribution bars matching the web `.shap-bar--pos` (green→teal)
/// and `.shap-bar--neg` (red→rose) gradients.
class _ShapBars extends StatelessWidget {
  final List<FeatureContribution> factors;
  const _ShapBars(this.factors);

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final top = [...factors]
      ..sort((a, b) => b.impactMillion.abs().compareTo(a.impactMillion.abs()));
    final shown = top.take(5).toList();
    final maxAbs = shown
        .map((f) => f.impactMillion.abs())
        .fold<double>(0.01, (a, b) => a > b ? a : b);

    return Column(
      children: shown.map((f) {
        final positive = f.impactMillion >= 0;
        final frac = (f.impactMillion.abs() / maxAbs).clamp(0.03, 1.0);
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 5),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(f.label,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 12, color: c.text)),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${positive ? '+' : ''}${f.impactMillion.toStringAsFixed(1)}',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w800,
                      color: positive ? c.good : c.bad,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: FractionallySizedBox(
                    widthFactor: frac,
                    child: Container(
                      height: 10,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: positive
                              ? const [Color(0xFF10B981), Color(0xFF14B8A6)]
                              : const [Color(0xFFEF4444), Color(0xFFF43F5E)],
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
      }).toList(),
    );
  }
}
