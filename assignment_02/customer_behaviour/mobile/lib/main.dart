import 'package:flutter/material.dart';

import 'api_client.dart';
import 'screens/review_form_screen.dart';
import 'theme.dart';

void main() => runApp(const RecommendationApp());

final ApiClient api = ApiClient();

class RecommendationApp extends StatelessWidget {
  const RecommendationApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Product recommendation',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(Brightness.light),
      darkTheme: buildAppTheme(Brightness.dark),
      themeMode: ThemeMode.system,
      home: const ReviewFormScreen(),
    );
  }
}
