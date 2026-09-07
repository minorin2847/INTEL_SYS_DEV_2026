import 'package:flutter/material.dart';

import 'api_client.dart';
import 'screens/questionnaire_screen.dart';

void main() => runApp(const DiabetesApp());

final ApiClient api = ApiClient();

/// One id per app launch, used to group this device's screenings in /history.
final String sessionId = 'mob-${DateTime.now().millisecondsSinceEpoch}';

class DiabetesApp extends StatelessWidget {
  const DiabetesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Diabetes Screening',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF4F46E5),
        useMaterial3: true,
      ),
      home: const QuestionnaireScreen(),
    );
  }
}

/// Shared colour for a risk band.
Color bandColor(String band) {
  switch (band) {
    case 'High':
      return Colors.red.shade600;
    case 'Moderate':
      return Colors.orange.shade700;
    default:
      return Colors.green.shade600;
  }
}
