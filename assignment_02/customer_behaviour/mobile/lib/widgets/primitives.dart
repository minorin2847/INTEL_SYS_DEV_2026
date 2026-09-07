import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models.dart';
import '../theme.dart';

/// Surface card — 1px border, radius lg, soft shadow (skill §4 Card).
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  const AppCard({super.key, required this.child, this.padding = const EdgeInsets.all(Sp.s5)});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: Rad.rLg,
        border: Border.all(color: c.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: child,
    );
  }
}

/// Small uppercase section caption (skill §4 `.card > h2`).
class SectionLabel extends StatelessWidget {
  final String text;
  const SectionLabel(this.text, {super.key});

  @override
  Widget build(BuildContext context) => Text(
        text.toUpperCase(),
        style: TextStyle(
          fontSize: Ty.xs,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.6,
          color: context.c.textFaint,
        ),
      );
}

/// Primary / ghost button (skill §4 Button). One primary per screen.
class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool primary;
  final bool busy;
  final IconData? icon;
  const AppButton(
      {super.key,
      required this.label,
      this.onPressed,
      this.primary = false,
      this.busy = false,
      this.icon});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final disabled = onPressed == null || busy;
    final fg = primary ? c.accentInk : c.text;
    return Opacity(
      opacity: disabled ? 0.55 : 1,
      child: Material(
        color: primary ? c.accent : c.surface,
        borderRadius: Rad.rMd,
        child: InkWell(
          borderRadius: Rad.rMd,
          onTap: disabled ? null : onPressed,
          child: Container(
            height: 44,
            padding: const EdgeInsets.symmetric(horizontal: Sp.s4),
            decoration: BoxDecoration(
              borderRadius: Rad.rMd,
              border: Border.all(color: primary ? Colors.transparent : c.border),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (busy)
                  SizedBox(
                    width: 15,
                    height: 15,
                    child: CircularProgressIndicator(strokeWidth: 2, color: fg),
                  )
                else if (icon != null)
                  Icon(icon, size: 17, color: fg),
                if (busy || icon != null) const SizedBox(width: Sp.s2),
                Text(label,
                    style: TextStyle(
                        color: fg, fontWeight: FontWeight.w600, fontSize: Ty.sm)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Neutral / good / bad pill (skill §4 Pill).
class Pill extends StatelessWidget {
  final String text;
  final String tone; // 'neutral' | 'good' | 'bad' | 'accent'
  final IconData? icon;
  const Pill(this.text, {super.key, this.tone = 'neutral', this.icon});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    late Color bg, fg;
    switch (tone) {
      case 'good':
        bg = c.goodWeak;
        fg = c.good;
        break;
      case 'bad':
        bg = c.badWeak;
        fg = c.bad;
        break;
      case 'accent':
        bg = c.accentWeak;
        fg = c.accent;
        break;
      default:
        bg = c.surface2;
        fg = c.textSoft;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: Sp.s2, vertical: 3),
      decoration: BoxDecoration(color: bg, borderRadius: Rad.rPill),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        if (icon != null) ...[Icon(icon, size: 12, color: fg), const SizedBox(width: 4)],
        Text(text,
            style: TextStyle(fontSize: Ty.xs, fontWeight: FontWeight.w600, color: fg)),
      ]),
    );
  }
}

/// One labelled input driven by a /questions [FormFieldSpec] (skill §4 Field).
class AppField extends StatelessWidget {
  final FormFieldSpec spec;
  final String? value;
  final bool invalid;
  final ValueChanged<String?> onChanged;
  const AppField(
      {super.key,
      required this.spec,
      required this.value,
      required this.onChanged,
      this.invalid = false});

  InputDecoration _dec(BuildContext context) {
    final c = context.c;
    OutlineInputBorder b(Color col, [double w = 1]) => OutlineInputBorder(
        borderRadius: Rad.rMd, borderSide: BorderSide(color: col, width: w));
    return InputDecoration(
      isDense: true,
      filled: true,
      fillColor: c.surface,
      contentPadding:
          const EdgeInsets.symmetric(horizontal: Sp.s3, vertical: Sp.s3),
      enabledBorder: b(invalid ? c.bad : c.border),
      focusedBorder: b(c.accent, 1.6),
      errorBorder: b(c.bad),
      hintStyle: TextStyle(color: c.textFaint, fontSize: Ty.md),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    Widget control;
    switch (spec.type) {
      case 'choice':
        control = DropdownButtonFormField<String>(
          initialValue: (spec.options.contains(value)) ? value : null,
          isExpanded: true,
          decoration: _dec(context),
          hint: Text('— not set —', style: TextStyle(color: c.textFaint)),
          items: spec.options
              .map((o) => DropdownMenuItem(value: o, child: Text(o)))
              .toList(),
          onChanged: onChanged,
        );
        break;
      case 'number':
        control = TextFormField(
          initialValue: value,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9.]'))],
          decoration: _dec(context),
          onChanged: onChanged,
        );
        break;
      case 'textarea':
        control = TextFormField(
          initialValue: value,
          maxLines: 5,
          minLines: 4,
          decoration: _dec(context).copyWith(
              hintText: 'What was your experience with the product?'),
          onChanged: onChanged,
        );
        break;
      default: // text
        control = TextFormField(
          initialValue: value,
          decoration: _dec(context),
          onChanged: onChanged,
        );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        RichText(
          text: TextSpan(
            style: TextStyle(
                fontSize: Ty.sm, fontWeight: FontWeight.w600, color: c.text),
            children: [
              TextSpan(text: spec.label),
              if (spec.required)
                TextSpan(text: '  *', style: TextStyle(color: c.bad)),
            ],
          ),
        ),
        const SizedBox(height: Sp.s1),
        control,
        if (spec.note != null && spec.note!.isNotEmpty) ...[
          const SizedBox(height: 5),
          Text(spec.note!,
              style: TextStyle(fontSize: Ty.xs, color: c.textFaint, height: 1.45)),
        ],
        if (invalid) ...[
          const SizedBox(height: 4),
          Text('Required',
              style: TextStyle(
                  fontSize: Ty.xs, color: c.bad, fontWeight: FontWeight.w600)),
        ],
      ],
    );
  }
}
