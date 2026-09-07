import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/constants/api_config.dart';
import '../core/theme/app_theme.dart';
import '../providers/prediction_provider.dart';

class SettingsModal extends StatefulWidget {
  const SettingsModal({super.key});

  @override
  State<SettingsModal> createState() => _SettingsModalState();
}

class _SettingsModalState extends State<SettingsModal> {
  late TextEditingController _urlController;

  @override
  void initState() {
    super.initState();
    final currentUrl = context.read<PredictionProvider>().baseUrl;
    _urlController = TextEditingController(text: currentUrl);
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PredictionProvider>();

    return Container(
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'API Connection Settings',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppTheme.textMain),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Close', style: TextStyle(color: AppTheme.textMuted)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text(
            'FastAPI service Base URL (Port 8002):',
            style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _urlController,
            style: const TextStyle(color: AppTheme.textMain),
            decoration: const InputDecoration(
              hintText: 'http://10.0.2.2:8002',
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Quick host preset selection:',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: ApiConfig.presetUrls.map((preset) {
              final url = preset['url']!;
              final name = preset['name']!;
              return ActionChip(
                label: Text(name, style: const TextStyle(fontSize: 12, color: AppTheme.textMain)),
                backgroundColor: const Color(0xFFF8FAFC),
                side: const BorderSide(color: AppTheme.borderColor),
                onPressed: () {
                  _urlController.text = url;
                  provider.setBaseUrl(url);
                },
              );
            }).toList(),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: () {
                    provider.setBaseUrl(_urlController.text);
                    Navigator.of(context).pop();
                  },
                  child: const Text('Save URL'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    side: const BorderSide(color: AppTheme.borderColor),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  onPressed: provider.isHealthLoading
                      ? null
                      : () {
                          provider.setBaseUrl(_urlController.text);
                          provider.checkHealth();
                        },
                  child: Text(
                    provider.isHealthLoading ? 'Checking...' : 'Test Connection',
                    style: const TextStyle(color: AppTheme.textMain, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
