import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme/app_theme.dart';
import '../providers/prediction_provider.dart';
import '../screens/settings_modal.dart';

class ServerStatusBadge extends StatelessWidget {
  const ServerStatusBadge({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PredictionProvider>();
    final health = provider.healthStatus;
    final isHealthy = health?.modelLoaded == true;
    final isLoading = provider.isHealthLoading;

    final Color statusColor = isLoading
        ? const Color(0xFFD97706)
        : isHealthy
            ? AppTheme.primaryColor
            : Color(0xFFEF4444);

    final String statusText = isLoading
        ? 'Connecting...'
        : isHealthy
            ? 'API Ready (${health?.modelName ?? "ML"})'
            : 'API Disconnected';

    return InkWell(
      onTap: () {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (_) => const SettingsModal(),
        );
      },
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: statusColor.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: statusColor.withValues(alpha: 0.3)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 7,
              height: 7,
              decoration: BoxDecoration(
                color: statusColor,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            Text(
              statusText,
              style: TextStyle(
                color: statusColor,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
