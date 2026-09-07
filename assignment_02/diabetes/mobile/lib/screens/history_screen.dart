import 'package:flutter/material.dart';

import '../main.dart';
import '../models.dart';

/// Screen 4 — this device's past screenings (GET /history for the launch session id).
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<HistoryItem>> _f;

  @override
  void initState() {
    super.initState();
    _f = api.history(sessionId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => setState(() => _f = api.history(sessionId)),
          ),
        ],
      ),
      body: FutureBuilder<List<HistoryItem>>(
        future: _f,
        builder: (context, snap) {
          if (snap.hasError) {
            return Center(child: Text('Could not load history:\n${snap.error}'));
          }
          if (!snap.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final items = snap.data!;
          if (items.isEmpty) {
            return const Center(
                child: Text('No screenings recorded on this device yet.'));
          }
          return ListView.separated(
            itemCount: items.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, i) {
              final h = items[i];
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: bandColor(h.band),
                  child: Text('${(h.probability * 100).round()}',
                      style: const TextStyle(
                          color: Colors.white, fontSize: 12)),
                ),
                title: Text(h.band),
                subtitle: Text(
                  '${h.time.toLocal().toString().substring(0, 16)} · '
                  'completeness ${(h.completeness * 100).round()}%',
                ),
              );
            },
          );
        },
      ),
    );
  }
}
