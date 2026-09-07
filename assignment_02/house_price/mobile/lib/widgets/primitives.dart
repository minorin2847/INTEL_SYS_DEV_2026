import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final bool borderless;
  const AppCard({super.key, required this.child, this.padding, this.borderless = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding ?? const EdgeInsets.all(Sp.s4),
      decoration: BoxDecoration(
        color: context.c.surface,
        borderRadius: Rad.rLg,
        border: borderless ? null : Border.all(color: context.c.border),
      ),
      child: child,
    );
  }
}

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool primary, busy;
  final IconData? icon;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.primary = false,
    this.busy = false,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final bg = primary ? c.accent : c.surface2;
    final fg = primary ? c.accentInk : c.text;

    return GestureDetector(
      onTap: busy ? null : onPressed,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 200),
        opacity: (onPressed == null || busy) ? 0.6 : 1.0,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: Sp.s5, vertical: Sp.s3),
          decoration: BoxDecoration(
            color: bg,
            borderRadius: Rad.rLg,
            border: primary ? null : Border.all(color: c.border),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (busy) ...[
                SizedBox(
                  width: 16, height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2, color: fg),
                ),
                const SizedBox(width: Sp.s2),
              ] else if (icon != null) ...[
                Icon(icon, size: 18, color: fg),
                const SizedBox(width: Sp.s2),
              ],
              Text(
                label,
                style: TextStyle(color: fg, fontWeight: FontWeight.w600, fontSize: Ty.sm),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class Pill extends StatelessWidget {
  final String text;
  final String tone; // 'neutral' | 'accent' | 'good' | 'warn' | 'bad'
  final IconData? icon;

  const Pill(this.text, {super.key, this.tone = 'neutral', this.icon});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    Color bg, fg;
    switch (tone) {
      case 'accent': bg = c.accentWeak; fg = c.accent; break;
      case 'good': bg = c.goodWeak; fg = c.good; break;
      case 'warn': bg = c.warnWeak; fg = c.warn; break;
      case 'bad': bg = c.badWeak; fg = c.bad; break;
      default: bg = c.surface2; fg = c.textSoft; break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Sp.s2, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: Rad.rSm),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 12, color: fg),
            const SizedBox(width: 4),
          ],
          Text(
            text.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.5,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }
}
