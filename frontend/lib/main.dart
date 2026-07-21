import 'package:flutter/material.dart';

import 'api_client.dart';
import 'models.dart';

void main() => runApp(const WhetstoneApp());

class WhetstoneApp extends StatelessWidget {
  const WhetstoneApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Whetstone',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
        home: const CorpusScreen(),
      );
}

class CorpusScreen extends StatefulWidget {
  const CorpusScreen({super.key});

  @override
  State<CorpusScreen> createState() => _CorpusScreenState();
}

class _CorpusScreenState extends State<CorpusScreen> {
  final _api = ApiClient();
  CorpusSummary? _summary;
  List<Exercise> _exercises = const [];
  String? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final summary = await _api.getDiscards();
      final exercises = await _api.getExercises();
      if (!mounted) return;
      setState(() {
        _summary = summary;
        _exercises = exercises;
        _loading = false;
      });
    } on ApiException catch (error) {
      if (mounted) {
        setState(() {
          _error = error.message;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Whetstone'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(28),
          child: Padding(
            padding: const EdgeInsets.only(left: 16, bottom: 8),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Coding exercises that carry proof of their own solvability',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: Colors.blue, fontStyle: FontStyle.italic),
              ),
            ),
          ),
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 820),
                    child: ListView(
                      padding: const EdgeInsets.all(24),
                      children: [
                        if (_summary != null) _Headline(summary: _summary!),
                        const SizedBox(height: 28),
                        if (_summary != null && _summary!.discards.isNotEmpty) ...[
                          Text('Discarded', style: theme.textTheme.titleLarge),
                          const SizedBox(height: 4),
                          Text(
                            'Candidates that failed their own tests. These never reach a student.',
                            style: theme.textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 12),
                          for (final discard in _summary!.discards)
                            _DiscardCard(discard: discard),
                          const SizedBox(height: 28),
                        ],
                        Text('Published exercises',
                            style: theme.textTheme.titleLarge),
                        const SizedBox(height: 4),
                        Text(
                          'Each one passed the tests written for it, inside an isolated sandbox.',
                          style: theme.textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 12),
                        for (final exercise in _exercises)
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Icon(Icons.check_circle,
                                          size: 18,
                                          color: Colors.green.shade600),
                                      const SizedBox(width: 8),
                                      Text('Exercise #${exercise.id}',
                                          style: theme.textTheme.titleMedium),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(exercise.problemStatement),
                                ],
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
    );
  }
}

class _Headline extends StatelessWidget {
  const _Headline({required this.summary});
  final CorpusSummary summary;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      color: theme.colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _Stat(label: 'Generated', value: summary.generated),
            _Stat(label: 'Kept', value: summary.kept),
            _Stat(label: 'Discarded', value: summary.discarded),
          ],
        ),
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value});
  final String label;
  final int value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      children: [
        Text('$value', style: theme.textTheme.displaySmall),
        Text(label, style: theme.textTheme.titleMedium),
      ],
    );
  }
}

class _DiscardCard extends StatelessWidget {
  const _DiscardCard({required this.discard});
  final Discard discard;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      color: Colors.grey.shade200,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.cancel, size: 18, color: Colors.grey.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Text('${discard.topic} — candidate #${discard.id}',
                      style: theme.textTheme.titleMedium),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(discard.problemStatement),
            const SizedBox(height: 12),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                discard.failureReason.trim(),
                style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}