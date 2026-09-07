import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'providers/prediction_provider.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const HousePriceApp());
}

class HousePriceApp extends StatelessWidget {
  const HousePriceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => PredictionProvider()),
      ],
      child: MaterialApp(
        title: 'VN Real Estate Valuation',
        debugShowCheckedModeBanner: false,
        theme: buildAppTheme(Brightness.light),
        home: const HomeScreen(),
      ),
    );
  }
}
