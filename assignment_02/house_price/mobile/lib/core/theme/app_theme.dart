import 'package:flutter/material.dart';

// ---------------------------------------------------------------- spacing scale
class Sp {
  static const double s1 = 4, s2 = 8, s3 = 12, s4 = 16, s5 = 20, s6 = 24,
      s8 = 32, s10 = 40, s12 = 48;
}

class Rad {
  static const double sm = 8, md = 12, lg = 16, pill = 999;
  static const rSm = BorderRadius.all(Radius.circular(sm));
  static const rMd = BorderRadius.all(Radius.circular(md));
  static const rLg = BorderRadius.all(Radius.circular(lg));
  static const rPill = BorderRadius.all(Radius.circular(pill));
}

// ---------------------------------------------------------------- type scale
class Ty {
  static const double xs = 12, sm = 14, md = 16, lg = 18, xl = 22, xxl = 28;
  static const double lh = 1.5;
}

// ---------------------------------------------------------------- colour tokens
@immutable
class AppColors extends ThemeExtension<AppColors> {
  final Color bg, surface, surface2, border;
  final Color text, textSoft, textFaint;
  final Color accent, accentInk, accentWeak;
  final Color good, goodWeak, warn, warnWeak, bad, badWeak;

  const AppColors({
    required this.bg,
    required this.surface,
    required this.surface2,
    required this.border,
    required this.text,
    required this.textSoft,
    required this.textFaint,
    required this.accent,
    required this.accentInk,
    required this.accentWeak,
    required this.good,
    required this.goodWeak,
    required this.warn,
    required this.warnWeak,
    required this.bad,
    required this.badWeak,
  });

  static const light = AppColors(
    bg: Color(0xFFF8FAFC),
    surface: Color(0xFFFFFFFF),
    surface2: Color(0xFFF1F5F9),
    border: Color(0xFFE2E8F0),
    text: Color(0xFF0F172A),
    textSoft: Color(0xFF64748B),
    textFaint: Color(0xFF94A3B8),
    accent: Color(0xFF4F46E5),
    accentInk: Color(0xFFFFFFFF),
    accentWeak: Color(0xFFE0E7FF),
    good: Color(0xFF10B981),
    goodWeak: Color(0xFFD1FAE5),
    warn: Color(0xFFF59E0B),
    warnWeak: Color(0xFFFEF3C7),
    bad: Color(0xFFEF4444),
    badWeak: Color(0xFFFEE2E2),
  );

  static const dark = AppColors(
    bg: Color(0xFF0F172A),
    surface: Color(0xFF1E293B),
    surface2: Color(0xFF334155),
    border: Color(0xFF334155),
    text: Color(0xFFF8FAFC),
    textSoft: Color(0xFF94A3B8),
    textFaint: Color(0xFF64748B),
    accent: Color(0xFF6366F1),
    accentInk: Color(0xFFFFFFFF),
    accentWeak: Color(0xFF312E81),
    good: Color(0xFF34D399),
    goodWeak: Color(0xFF064E3B),
    warn: Color(0xFFFBBF24),
    warnWeak: Color(0xFF78350F),
    bad: Color(0xFFF87171),
    badWeak: Color(0xFF7F1D1D),
  );

  @override
  AppColors copyWith({
    Color? bg,
    Color? surface,
    Color? surface2,
    Color? border,
    Color? text,
    Color? textSoft,
    Color? textFaint,
    Color? accent,
    Color? accentInk,
    Color? accentWeak,
    Color? good,
    Color? goodWeak,
    Color? warn,
    Color? warnWeak,
    Color? bad,
    Color? badWeak,
  }) =>
      AppColors(
        bg: bg ?? this.bg,
        surface: surface ?? this.surface,
        surface2: surface2 ?? this.surface2,
        border: border ?? this.border,
        text: text ?? this.text,
        textSoft: textSoft ?? this.textSoft,
        textFaint: textFaint ?? this.textFaint,
        accent: accent ?? this.accent,
        accentInk: accentInk ?? this.accentInk,
        accentWeak: accentWeak ?? this.accentWeak,
        good: good ?? this.good,
        goodWeak: goodWeak ?? this.goodWeak,
        warn: warn ?? this.warn,
        warnWeak: warnWeak ?? this.warnWeak,
        bad: bad ?? this.bad,
        badWeak: badWeak ?? this.badWeak,
      );

  @override
  AppColors lerp(ThemeExtension<AppColors>? other, double t) {
    if (other is! AppColors) return this;
    Color m(Color a, Color b) => Color.lerp(a, b, t)!;
    return AppColors(
      bg: m(bg, other.bg),
      surface: m(surface, other.surface),
      surface2: m(surface2, other.surface2),
      border: m(border, other.border),
      text: m(text, other.text),
      textSoft: m(textSoft, other.textSoft),
      textFaint: m(textFaint, other.textFaint),
      accent: m(accent, other.accent),
      accentInk: m(accentInk, other.accentInk),
      accentWeak: m(accentWeak, other.accentWeak),
      good: m(good, other.good),
      goodWeak: m(goodWeak, other.goodWeak),
      warn: m(warn, other.warn),
      warnWeak: m(warnWeak, other.warnWeak),
      bad: m(bad, other.bad),
      badWeak: m(badWeak, other.badWeak),
    );
  }
}

extension AppColorsX on BuildContext {
  AppColors get c => Theme.of(this).extension<AppColors>()!;
}

// ---------------------------------------------------------------- ThemeData
ThemeData buildAppTheme(Brightness brightness) {
  final isDark = brightness == Brightness.dark;
  final ac = isDark ? AppColors.dark : AppColors.light;
  final base = ThemeData(brightness: brightness, useMaterial3: true, fontFamily: 'Inter');

  return base.copyWith(
    scaffoldBackgroundColor: ac.bg,
    extensions: [ac],
    colorScheme: base.colorScheme.copyWith(
      primary: ac.accent,
      onPrimary: ac.accentInk,
      surface: ac.surface,
      onSurface: ac.text,
      error: ac.bad,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: ac.surface,
      foregroundColor: ac.text,
      elevation: 0,
      scrolledUnderElevation: 1,
      centerTitle: false,
      titleTextStyle: TextStyle(
        color: ac.text,
        fontSize: Ty.lg,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.2,
      ),
      shape: Border(bottom: BorderSide(color: ac.border.withValues(alpha: 0.5))),
      iconTheme: IconThemeData(color: ac.text),
    ),
    textTheme: base.textTheme.apply(bodyColor: ac.text, displayColor: ac.text, fontFamily: 'Inter'),
    dividerColor: ac.border,
    splashFactory: NoSplash.splashFactory,
  );
}


// Compatibility Layer
class AppTheme {
  static const primaryColor = Color(0xFF4F46E5);
  static const textMain = Color(0xFF0F172A);
  static const textMuted = Color(0xFF64748B);
  static const borderColor = Color(0xFFE2E8F0);
  static const surfaceColor = Color(0xFFFFFFFF);
  static const backgroundColor = Color(0xFFF8FAFC);
}
