import 'package:flutter/material.dart';

import '../main.dart';
import '../models.dart';
import '../theme.dart';
import '../widgets/primitives.dart';
import '../widgets/result_parts.dart';
import 'result_screen.dart';

/// 3-step wizard: skin profile → product → review. Fields render from
/// GET /questions; POST /predict on the last step.
class ReviewFormScreen extends StatefulWidget {
  const ReviewFormScreen({super.key});

  @override
  State<ReviewFormScreen> createState() => _ReviewFormScreenState();
}

class _ReviewFormScreenState extends State<ReviewFormScreen> {
  List<FormFieldSpec>? _fields;
  List<String> _sections = const [];
  String? _loadError;
  bool? _apiUp;
  Map<String, dynamic> _modelInfo = const {};
  Map<String, dynamic>? _samples;

  int _step = 0;
  bool _touched = false;
  bool _busy = false;

  final Map<String, dynamic> _values = {
    'skin_type': 'oily',
    'skin_tone': 'light',
    'eye_color': 'brown',
    'hair_color': 'brown',
    'secondary_category': 'Moisturizers',
    'brand_name': 'Skinfix',
    'price_usd': '32',
    'loves_count': '21000',
    'reviews': '1800',
    'review_title': 'Not for oily skin',
    'review_text':
        'Broke me out within a week and felt greasy all day. Smells strongly '
            'of perfume. Wanted to love it but returned it.',
  };

  static const _required = {
    1: ['price_usd'],
    2: ['review_text'],
  };

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loadError = null);
    api.health().then((v) => mounted ? setState(() => _apiUp = v) : null);
    api.modelInfo().then((m) {
      if (mounted) setState(() => _modelInfo = m);
    }).catchError((_) {});
    api.samples().then((s) {
      if (mounted) setState(() => _samples = s);
    }).catchError((_) {});
    try {
      final f = await api.questions();
      final secs = <String>[];
      for (final x in f) {
        if (!secs.contains(x.section)) secs.add(x.section);
      }
      setState(() {
        _fields = f;
        _sections = secs.isEmpty
            ? ['Your skin profile', 'The product', 'The review']
            : secs;
      });
    } catch (e) {
      setState(() => _loadError = '$e');
    }
  }

  List<String> get _missing => (_required[_step] ?? const [])
      .where((k) {
        final v = _values[k];
        return v == null || (v is String && v.trim().isEmpty);
      })
      .toList();

  bool get _canNext => _missing.isEmpty;
  bool get _isLast => _step == _sections.length - 1;

  Map<String, dynamic> _payload() {
    final numFields = {
      for (final f in _fields ?? <FormFieldSpec>[])
        if (f.type == 'number') f.field
    };
    final p = <String, dynamic>{};
    _values.forEach((k, v) {
      if (v == null || (v is String && v.trim().isEmpty)) return;
      p[k] = numFields.contains(k) ? num.tryParse(v.toString()) : v;
    });
    return p;
  }

  Future<void> _submit() async {
    setState(() => _busy = true);
    try {
      final r = await api.predict(_payload());
      if (!mounted) return;
      Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ResultScreen(result: r, modelInfo: _modelInfo),
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('$e')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _next() {
    if (!_canNext) {
      setState(() => _touched = true);
      return;
    }
    setState(() => _touched = false);
    if (_isLast) {
      _submit();
    } else {
      setState(() => _step += 1);
    }
  }

  void _back() => setState(() {
        _touched = false;
        if (_step > 0) _step -= 1;
      });

  void _loadExample(Map<String, dynamic> ex) {
    setState(() {
      ex.forEach((k, v) {
        if (!k.startsWith('_')) _values[k] = v?.toString() ?? '';
      });
      _touched = false;
      _step = 2;
    });
  }

  void _pickExample() {
    final examples = (_samples?['examples'] as List?) ?? [];
    if (examples.isEmpty) return;
    final c = context.c;
    showModalBottomSheet(
      context: context,
      backgroundColor: c.surface,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(Rad.lg))),
      builder: (_) => SafeArea(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(Sp.s5, Sp.s4, Sp.s5, Sp.s2),
            child: Align(
              alignment: Alignment.centerLeft,
              child: SectionLabel('Load a real review'),
            ),
          ),
          Flexible(
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: examples.length,
              separatorBuilder: (_, __) => Divider(height: 1, color: c.border),
              itemBuilder: (_, i) {
                final ex = (examples[i] as Map).cast<String, dynamic>();
                return ListTile(
                  dense: true,
                  title: Text('${ex['_label']}',
                      style: TextStyle(fontSize: Ty.sm, color: c.text)),
                  onTap: () {
                    Navigator.pop(context);
                    _loadExample(ex);
                  },
                );
              },
            ),
          ),
        ]),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    final fields = _fields;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Will this customer recommend it?'),
        actions: [
          if ((_samples?['examples'] as List?)?.isNotEmpty ?? false)
            IconButton(
              tooltip: 'Load a real review',
              icon: const Icon(Icons.playlist_add_check_rounded),
              onPressed: _pickExample,
            ),
        ],
      ),
      body: _loadError != null
          ? _ErrorView(message: _loadError!, onRetry: _load)
          : fields == null
              ? const Center(child: CircularProgressIndicator())
              : Column(
                  children: [
                    if (_apiUp == false) const OfflineBanner(),
                    Expanded(
                      child: ListView(
                        padding: const EdgeInsets.fromLTRB(Sp.s4, Sp.s4, Sp.s4, Sp.s6),
                        children: [
                          Row(children: [
                            Expanded(
                              child: Text(
                                'Sephora skincare reviews · predicts is_recommended',
                                style: TextStyle(fontSize: Ty.xs, color: c.textSoft),
                              ),
                            ),
                            Pill(
                              _apiUp == false
                                  ? 'API offline'
                                  : _apiUp == true
                                      ? 'API connected'
                                      : 'connecting…',
                              tone: _apiUp == false
                                  ? 'bad'
                                  : _apiUp == true
                                      ? 'good'
                                      : 'neutral',
                            ),
                          ]),
                          const SizedBox(height: Sp.s5),
                          StepperBar(
                            steps: _sections,
                            current: _step,
                            onJump: (i) => setState(() {
                              _step = i;
                              _touched = false;
                            }),
                          ),
                          const SizedBox(height: Sp.s5),
                          Align(
                            alignment: Alignment.centerLeft,
                            child: Pill('STEP ${_step + 1} OF ${_sections.length}',
                                tone: 'accent'),
                          ),
                          const SizedBox(height: Sp.s2),
                          Text(_sections[_step],
                              style: TextStyle(
                                  fontSize: Ty.xl,
                                  fontWeight: FontWeight.w800,
                                  color: c.text)),
                          const SizedBox(height: Sp.s1),
                          Text(_stepSub(_step),
                              style: TextStyle(fontSize: Ty.sm, color: c.textSoft)),
                          const SizedBox(height: Sp.s4),
                          AppCard(
                            child: Column(
                              children: [
                                for (final f in fields
                                    .where((x) => x.section == _sections[_step]))
                                  Padding(
                                    padding: const EdgeInsets.only(bottom: Sp.s4),
                                    child: AppField(
                                      spec: f,
                                      value: _values[f.field]?.toString(),
                                      invalid: _touched && _missing.contains(f.field),
                                      onChanged: (v) =>
                                          setState(() => _values[f.field] = v),
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          if (_isLast) ...[
                            const SizedBox(height: Sp.s4),
                            const SectionLabel('Try a real review'),
                            const SizedBox(height: Sp.s2),
                            Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: _reviewExamples(fields).map((ex) {
                                return ActionChip(
                                  label: Text(ex[0],
                                      style: TextStyle(
                                          fontSize: Ty.xs, color: c.textSoft)),
                                  backgroundColor: c.surface2,
                                  side: BorderSide(color: c.border),
                                  shape: const StadiumBorder(),
                                  onPressed: () => setState(() {
                                    _values['review_title'] = ex[0];
                                    _values['review_text'] = ex[1];
                                  }),
                                );
                              }).toList(),
                            ),
                          ],
                        ],
                      ),
                    ),
                    _FooterBar(
                      onBack: _step == 0 || _busy ? null : _back,
                      onNext: _busy ? null : _next,
                      nextLabel: _isLast ? (_busy ? 'Scoring…' : 'Predict') : 'Next',
                      busy: _busy,
                      nextEnabled: _canNext || !_touched,
                      nextHint: _canNext ? null : 'Fill in: ${_missing.join(', ')}',
                    ),
                  ],
                ),
    );
  }

  String _stepSub(int i) {
    switch (i) {
      case 0:
        return 'Who is writing the review.';
      case 1:
        return 'Category, brand, price, popularity.';
      default:
        return 'What the customer wrote — the model leans on this.';
    }
  }

  List<List<String>> _reviewExamples(List<FormFieldSpec> fields) {
    for (final f in fields) {
      if (f.field == 'review_text') return f.examples;
    }
    return const [];
  }
}

class _FooterBar extends StatelessWidget {
  final VoidCallback? onBack, onNext;
  final String nextLabel;
  final String? nextHint;
  final bool busy, nextEnabled;
  const _FooterBar({
    required this.onBack,
    required this.onNext,
    required this.nextLabel,
    required this.busy,
    required this.nextEnabled,
    this.nextHint,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Container(
      padding: EdgeInsets.fromLTRB(
          Sp.s4, Sp.s3, Sp.s4, Sp.s3 + MediaQuery.of(context).padding.bottom),
      decoration: BoxDecoration(
        color: c.surface,
        border: Border(top: BorderSide(color: c.border)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          AppButton(label: '← Back', onPressed: onBack),
          Tooltip(
            message: nextHint ?? '',
            triggerMode:
                nextHint == null ? TooltipTriggerMode.manual : TooltipTriggerMode.tap,
            child: AppButton(
              label: nextLabel,
              primary: true,
              busy: busy,
              onPressed: nextEnabled ? onNext : null,
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final c = context.c;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Sp.s6),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off, size: 40, color: c.textFaint),
            const SizedBox(height: Sp.s3),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: Sp.s4),
            AppButton(label: 'Retry', primary: true, onPressed: onRetry),
          ],
        ),
      ),
    );
  }
}
