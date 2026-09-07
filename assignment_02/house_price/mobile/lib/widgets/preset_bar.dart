import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme/app_theme.dart';
import '../models/property_input.dart';
import '../providers/prediction_provider.dart';

class PresetBar extends StatelessWidget {
  final Function(PropertyInput) onSelectPreset;

  const PresetBar({super.key, required this.onSelectPreset});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PredictionProvider>();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'DEMO PRESETS:',
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: AppTheme.textMuted,
            letterSpacing: 0.5,
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 36,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: provider.presets.length,
            separatorBuilder: (context, index) => const SizedBox(width: 8),
            itemBuilder: (context, index) {
              final preset = provider.presets[index];
              return ActionChip(
                label: Text(
                  preset['title'] as String,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: AppTheme.textMain,
                  ),
                ),
                backgroundColor: Colors.white,
                side: const BorderSide(color: AppTheme.borderColor),
                padding: const EdgeInsets.symmetric(horizontal: 4),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                onPressed: () {
                  final PropertyInput data = preset['data'] as PropertyInput;
                  onSelectPreset(data);
                },
              );
            },
          ),
        ),
      ],
    );
  }
}
