import 'package:flutter/material.dart';

import '../core/theme/app_theme.dart';
import 'primitives.dart';

/// Horizontal numbered stepper (skill §6c). Done = ✓ accent, active = ring,
/// future = dim. Done steps are tappable to jump back.
class StepperBar extends StatelessWidget {
  final List<String> steps;
  final int current;
  final void Function(int) onJump;
  const StepperBar(
      {super.key,
      required this.steps,
      required this.current,
      required this.onJump});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Row(
      children: List.generate(steps.length, (i) {
        final done = i < current, active = i == current;
        final ink = done || active ? c.accentInk : c.textSoft;
        return Expanded(
          child: Column(
            children: [
              Row(
                children: [
                  Expanded(
                    child: i == 0
                        ? const SizedBox()
                        : Container(
                            height: 2, color: i <= current ? c.accent : c.border),
                  ),
                  GestureDetector(
                    onTap: done ? () => onJump(i) : null,
                    child: Container(
                      width: 30,
                      height: 30,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: done ? c.accent : (active ? c.surface : c.surface2),
                        shape: BoxShape.circle,
                        border: Border.all(
                            color: active || done ? c.accent : c.border, width: 2),
                        boxShadow: active
                            ? [
                                BoxShadow(
                                    color: c.accent.withValues(alpha: 0.3),
                                    blurRadius: 0,
                                    spreadRadius: 3)
                              ]
                            : null,
                      ),
                      child: done
                          ? Icon(Icons.check, size: 16, color: c.accentInk)
                          : Text('${i + 1}',
                              style: TextStyle(
                                  fontSize: Ty.xs,
                                  fontWeight: FontWeight.w700,
                                  color: active ? c.accent : ink)),
                    ),
                  ),
                  Expanded(
                    child: i == steps.length - 1
                        ? const SizedBox()
                        : Container(
                            height: 2,
                            color: i < current ? c.accent : c.border),
                  ),
                ],
              ),
              const SizedBox(height: 5),
              Text(
                steps[i],
                textAlign: TextAlign.center,
                maxLines: 2,
                style: TextStyle(
                  fontSize: Ty.xs,
                  fontWeight: FontWeight.w600,
                  color: active ? c.text : c.textSoft,
                ),
              ),
            ],
          ),
        );
      }),
    );
  }
}

/// Big tinted headline verdict (skill §4 "Verdict block").
class VerdictBlock extends StatelessWidget {
  final bool good;
  final String badge, title, subtitle;
  const VerdictBlock(
      {super.key,
      required this.good,
      required this.badge,
      required this.title,
      required this.subtitle});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final tint = good ? c.goodWeak : c.badWeak;
    final ink = good ? c.good : c.bad;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(Sp.s5),
      decoration: BoxDecoration(
        color: tint,
        borderRadius: Rad.rMd,
        border: Border.all(color: ink.withValues(alpha: 0.55), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Pill(badge, tone: good ? 'good' : 'bad'),
          const SizedBox(height: Sp.s3),
          Text(title,
              style: TextStyle(
                  fontSize: Ty.lg, fontWeight: FontWeight.w800, color: ink, height: 1.3)),
          const SizedBox(height: Sp.s2),
          Text(subtitle,
              style: TextStyle(fontSize: Ty.sm, color: c.text, height: 1.5)),
        ],
      ),
    );
  }
}

/// Probability meter with a threshold rule (skill §4 Meter). The number is truth,
/// the bar is decoration.
class Meter extends StatelessWidget {
  final double value; // 0..1
  final double threshold;
  final bool good;
  final String leftLabel, rightLabel;
  const Meter({
    super.key,
    required this.value,
    required this.threshold,
    required this.good,
    this.leftLabel = "0%",
    this.rightLabel = "100%",
  });

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        LayoutBuilder(builder: (context, box) {
          final w = box.maxWidth;
          return Stack(
            clipBehavior: Clip.none,
            children: [
              Container(
                height: 12,
                decoration:
                    BoxDecoration(color: c.surface2, borderRadius: Rad.rPill),
              ),
              Container(
                height: 12,
                width: (w * value).clamp(4.0, w),
                decoration: BoxDecoration(
                    color: good ? c.good : c.bad, borderRadius: Rad.rPill),
              ),
              Positioned(
                left: (w * threshold) - 1,
                top: -2,
                child: Container(width: 2, height: 16, color: c.text),
              ),
            ],
          );
        }),
        const SizedBox(height: 6),
        DefaultTextStyle(
          style: TextStyle(fontSize: Ty.xs, color: c.textFaint),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(leftLabel),
              Text('${(threshold * 100).round()}% cut-off'),
              Text(rightLabel),
            ],
          ),
        ),
      ],
    );
  }
}

/// label → value rows (skill §6). label soft, value 600.
class KvGrid extends StatelessWidget {
  final List<(String, String)> rows;
  const KvGrid(this.rows, {super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Column(
      children: rows
          .map((r) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 120,
                      child: Text(r.$1,
                          style: TextStyle(fontSize: Ty.xs, color: c.textSoft)),
                    ),
                    Expanded(
                      child: Text(r.$2,
                          style: TextStyle(
                              fontSize: Ty.sm, fontWeight: FontWeight.w600, color: c.text)),
                    ),
                  ],
                ),
              ))
          .toList(),
    );
  }
}

/// Wrap of small tinted chips for short tokens (skill §6).
class ChipRow extends StatelessWidget {
  final List<String> items;
  final bool good;
  const ChipRow(this.items, {super.key, required this.good});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      children: items
          .map((t) => Container(
                padding: const EdgeInsets.symmetric(horizontal: Sp.s2, vertical: 4),
                decoration: BoxDecoration(
                  color: good ? c.goodWeak : c.badWeak,
                  borderRadius: Rad.rPill,
                  border: Border.all(
                      color: (good ? c.good : c.bad).withValues(alpha: 0.4)),
                ),
                child: Text(t,
                    style: TextStyle(
                        fontSize: Ty.xs,
                        fontWeight: FontWeight.w600,
                        color: good ? c.good : c.bad)),
              ))
          .toList(),
    );
  }
}

/// Diverging bar chart of the linear model's per-feature pull (skill §6b).
class ContribChart extends StatelessWidget {
  final Map<String, dynamic> contributions;
  const ContribChart(this.contributions, {super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final items = ((contributions['items'] as List?) ?? [])
        .map((e) => (e as Map).cast<String, dynamic>())
        .toList();
    final other = (contributions['other_effect'] as num?)?.toDouble() ?? 0;
    final rows = [...items];
    if (other.abs() >= 0.01) {
      rows.add({'label': 'Other smaller factors combined', 'kind': 'other', 'effect': other});
    }
    if (rows.isEmpty) return const SizedBox();

    final maxAbs = rows
        .map((r) => (r['effect'] as num).abs().toDouble())
        .fold<double>(0.4, (a, b) => a > b ? a : b);

    final basePct = (((contributions['base_p'] as num?)?.toDouble() ?? 0) * 100).round();
    final finalPct = (((contributions['final_p'] as num?)?.toDouble() ?? 0) * 100).round();
    final delta = finalPct - basePct;

    Color tagBg(String k) => k == 'text' ? c.accentWeak : c.surface2;
    Color tagFg(String k) => k == 'text' ? c.accent : c.textSoft;
    String tagText(String k) =>
        k == 'text' ? 'review' : (k == 'other' ? 'other' : 'profile');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          _legendDot(c.bad),
          Text("  toward “won't recommend”   ",
              style: TextStyle(fontSize: Ty.xs, color: c.textSoft)),
          _legendDot(c.good),
          Text("  toward “recommends”",
              style: TextStyle(fontSize: Ty.xs, color: c.textSoft)),
        ]),
        const SizedBox(height: Sp.s3),
        ...rows.map((r) {
          final eff = (r['effect'] as num).toDouble();
          final neg = eff < 0;
          final frac = (eff.abs() / maxAbs).clamp(0.04, 1.0);
          return Padding(
            padding: const EdgeInsets.only(bottom: Sp.s2),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                    decoration: BoxDecoration(
                        color: tagBg(r['kind'] as String),
                        borderRadius: Rad.rSm),
                    child: Text(tagText(r['kind'] as String),
                        style: TextStyle(
                            fontSize: 9,
                            fontWeight: FontWeight.w800,
                            color: tagFg(r['kind'] as String))),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(r['label'] as String,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: Ty.xs, color: c.text, height: 1.3)),
                  ),
                  const SizedBox(width: 6),
                  Text(eff >= 0 ? '+${eff.toStringAsFixed(2)}' : eff.toStringAsFixed(2),
                      style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w800,
                          fontFeatures: const [],
                          color: neg ? c.bad : c.good)),
                ]),
                const SizedBox(height: 3),
                LayoutBuilder(builder: (context, box) {
                  final half = box.maxWidth / 2;
                  return SizedBox(
                    height: 14,
                    child: Stack(children: [
                      Positioned(
                        left: half - 1,
                        child: Container(width: 2, height: 14, color: c.border),
                      ),
                      Positioned(
                        left: neg ? half - half * frac : half,
                        child: Container(
                          width: half * frac,
                          height: 14,
                          decoration: BoxDecoration(
                            color: neg ? c.bad : c.good,
                            borderRadius: BorderRadius.horizontal(
                              left: Radius.circular(neg ? 4 : 0),
                              right: Radius.circular(neg ? 0 : 4),
                            ),
                          ),
                        ),
                      ),
                    ]),
                  );
                }),
              ],
            ),
          );
        }),
        const SizedBox(height: Sp.s2),
        Container(
          padding: const EdgeInsets.all(Sp.s3),
          decoration: BoxDecoration(
              color: c.surface2,
              borderRadius: Rad.rMd,
              border: Border.all(color: c.border)),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _wfStep(context, 'Neutral start', '$basePct%'),
              Icon(Icons.arrow_forward, size: 14, color: c.textFaint),
              _wfStep(context, 'Net pull',
                  '${delta >= 0 ? '+' : ''}$delta pts',
                  color: delta >= 0 ? c.good : c.bad),
              Icon(Icons.arrow_forward, size: 14, color: c.textFaint),
              _wfStep(context, 'Recommends', '$finalPct%'),
            ],
          ),
        ),
        
      ],
    );
  }

  Widget _legendDot(Color col) => Container(
      width: 10,
      height: 10,
      decoration: BoxDecoration(color: col, borderRadius: BorderRadius.circular(2)));

  Widget _wfStep(BuildContext context, String label, String value, {Color? color}) {
    final c = context.c;
    return Column(children: [
      Text(label.toUpperCase(),
          style: TextStyle(
              fontSize: 9, fontWeight: FontWeight.w700, color: c.textFaint)),
      const SizedBox(height: 2),
      Text(value,
          style: TextStyle(
              fontSize: Ty.md, fontWeight: FontWeight.w800, color: color ?? c.text)),
    ]);
  }
}



/// Top connection banner (skill §5 "Offline API").
class OfflineBanner extends StatelessWidget {
  const OfflineBanner({super.key});
  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: Sp.s4, vertical: Sp.s3),
      color: c.badWeak,
      child: Text(
        "API isn’t reachable. Run  python -m uvicorn api.main:app --port 8000  in customer_behaviour/",
        style: TextStyle(fontSize: Ty.xs, color: c.bad, fontWeight: FontWeight.w600),
      ),
    );
  }
}
