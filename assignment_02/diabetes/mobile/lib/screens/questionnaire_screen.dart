import 'package:flutter/material.dart';

import '../api_client.dart';
import '../main.dart';
import '../models.dart';
import 'history_screen.dart';
import 'result_screen.dart';

const _accent = Color(0xFF4F46E5);

/// Screen 1 — the questionnaire, laid out as a stepper wizard: one section
/// (Biometrics → Lifestyle → Medical History) at a time, matching the web app.
/// Rendered from `GET /questions`; every item has a "Not sure" option, and a
/// blank answer is sent to the API as null.
class QuestionnaireScreen extends StatefulWidget {
  const QuestionnaireScreen({super.key});

  @override
  State<QuestionnaireScreen> createState() => _QuestionnaireScreenState();
}

class _QuestionnaireScreenState extends State<QuestionnaireScreen> {
  late Future<List<Question>> _questionsF;
  final Map<String, dynamic> _answers = {}; // field -> value or null
  bool _submitting = false;
  int _step = 0;

  @override
  void initState() {
    super.initState();
    _questionsF = api.questions();
  }

  Future<void> _submit(List<Question> questions) async {
    if (_answers['Age'] == null || _answers['Sex'] == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Age group and Sex are required.')),
      );
      return;
    }
    final payload = <String, dynamic>{'session_id': sessionId};
    _answers.forEach((k, v) {
      if (v != null) payload[k] = v;
    });
    setState(() => _submitting = true);
    try {
      final result = await api.predict(payload);
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => ResultScreen(result: result, payload: payload),
        ),
      );
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message)));
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Diabetes screening'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'History',
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const HistoryScreen()),
            ),
          ),
        ],
      ),
      body: FutureBuilder<List<Question>>(
        future: _questionsF,
        builder: (context, snap) {
          if (snap.hasError) {
            return _ErrorView(
              message: 'Could not reach the API at ${ApiClient.baseUrl}.\n'
                  'Start it with:  uvicorn api.main:app --port 8000',
              onRetry: () => setState(() => _questionsF = api.questions()),
            );
          }
          if (!snap.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final questions = snap.data!;
          final sections = <String, List<Question>>{};
          for (final q in questions) {
            sections.putIfAbsent(q.section, () => []).add(q);
          }
          final sectionNames = sections.keys.toList();
          final step = _step.clamp(0, sectionNames.length - 1);
          final currentName = sectionNames[step];
          final stepQuestions = sections[currentName]!;
          final isLast = step == sectionNames.length - 1;

          return Column(
            children: [
              _StepperBar(labels: sectionNames, current: step),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  children: [
                    Text('Step ${step + 1} of ${sectionNames.length}',
                        style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: _accent)),
                    const SizedBox(height: 2),
                    Text(currentName,
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    const Text(
                      'Answer what you can. Choose "Not sure" for anything you '
                      'do not know — the estimate still works, with a note that '
                      'it is less certain.',
                      style: TextStyle(fontSize: 13, color: Colors.black54),
                    ),
                    const SizedBox(height: 12),
                    for (final q in stepQuestions) _questionField(q),
                  ],
                ),
              ),
              _FooterBar(
                onBack: step == 0 ? null : () => setState(() => _step = step - 1),
                busy: _submitting,
                isLast: isLast,
                onNext: _submitting
                    ? null
                    : () {
                        if (isLast) {
                          _submit(questions);
                        } else {
                          setState(() => _step = step + 1);
                        }
                      },
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _questionField(Question q) {
    switch (q.type) {
      case 'yesno':
        final current = _answers[q.field];
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(q.label),
              const SizedBox(height: 4),
              SegmentedButton<String>(
                showSelectedIcon: false,
                segments: const [
                  ButtonSegment(value: 'yes', label: Text('Yes')),
                  ButtonSegment(value: 'no', label: Text('No')),
                  ButtonSegment(value: 'na', label: Text('Not sure')),
                ],
                selected: {
                  current == 1
                      ? 'yes'
                      : current == 0
                          ? 'no'
                          : 'na'
                },
                onSelectionChanged: (s) => setState(() {
                  _answers[q.field] =
                      s.first == 'yes' ? 1 : (s.first == 'no' ? 0 : null);
                }),
              ),
            ],
          ),
        );

      case 'choice':
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: DropdownButtonFormField<dynamic>(
            value: _answers[q.field],
            isExpanded: true,
            decoration: InputDecoration(
              labelText: q.label,
              border: const OutlineInputBorder(),
            ),
            items: [
              const DropdownMenuItem(value: null, child: Text('Not sure')),
              for (final o in q.options)
                DropdownMenuItem(value: o[0], child: Text('${o[1]}')),
            ],
            onChanged: (v) => setState(() => _answers[q.field] = v),
          ),
        );

      default: // number
        final na = _answers['${q.field}__na'] == true;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(
            children: [
              Expanded(
                child: TextFormField(
                  enabled: !na,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: q.label,
                    helperText: q.note,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (t) =>
                      _answers[q.field] = t.trim().isEmpty ? null : num.tryParse(t),
                ),
              ),
              const SizedBox(width: 8),
              Column(
                children: [
                  const Text('N/A', style: TextStyle(fontSize: 11)),
                  Switch(
                    value: na,
                    onChanged: (v) => setState(() {
                      _answers['${q.field}__na'] = v;
                      if (v) _answers[q.field] = null;
                    }),
                  ),
                ],
              ),
            ],
          ),
        );
    }
  }
}

/// Horizontal stepper: numbered dots joined by connector lines, indigo for the
/// active and completed steps. Mirrors the web sidebar `.stepper.vert`.
class _StepperBar extends StatelessWidget {
  final List<String> labels;
  final int current;
  const _StepperBar({required this.labels, required this.current});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(bottom: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Row(
        children: [
          for (var i = 0; i < labels.length; i++) ...[
            if (i > 0)
              Expanded(
                child: Container(
                  height: 2,
                  color: i <= current ? _accent : Colors.grey.shade300,
                ),
              ),
            Column(
              children: [
                CircleAvatar(
                  radius: 15,
                  backgroundColor:
                      i <= current ? _accent : Colors.grey.shade300,
                  child: i < current
                      ? const Icon(Icons.check, size: 16, color: Colors.white)
                      : Text('${i + 1}',
                          style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: i <= current
                                  ? Colors.white
                                  : Colors.black54)),
                ),
                const SizedBox(height: 4),
                SizedBox(
                  width: 76,
                  child: Text(
                    labels[i],
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 10.5,
                      fontWeight:
                          i == current ? FontWeight.w700 : FontWeight.w400,
                      color: i <= current ? _accent : Colors.black54,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

/// Sticky bottom bar with Back and Next / Predict buttons.
class _FooterBar extends StatelessWidget {
  final VoidCallback? onBack;
  final VoidCallback? onNext;
  final bool busy;
  final bool isLast;
  const _FooterBar({
    required this.onBack,
    required this.onNext,
    required this.busy,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.shade200)),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            OutlinedButton(
              onPressed: onBack,
              child: const Text('← Back'),
            ),
            const Spacer(),
            FilledButton(
              onPressed: onNext,
              child: busy
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : Text(isLast ? 'Predict' : 'Next →'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});
  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.cloud_off, size: 40),
              const SizedBox(height: 12),
              Text(message, textAlign: TextAlign.center),
              const SizedBox(height: 12),
              OutlinedButton(onPressed: onRetry, child: const Text('Retry')),
            ],
          ),
        ),
      );
}
