import 'dart:async';

import 'package:flutter/material.dart';

import 'api_client.dart';
import 'models.dart';

void main() => runApp(const WhetstoneApp());

class WhetstoneApp extends StatelessWidget {
  const WhetstoneApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Whetstone',
        theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
        home: const GeneratorScreen(),
      );
}

class GeneratorScreen extends StatefulWidget {
  const GeneratorScreen({super.key});

  @override
  State<GeneratorScreen> createState() => _GeneratorScreenState();
}

class _GeneratorScreenState extends State<GeneratorScreen> {
  final _topicController = TextEditingController();
  final _api = ApiClient();
  Timer? _poller;
  String _difficulty = 'beginner';
  GenerationRun? _run;
  List<Exercise> _exercises = const [];
  String? _error;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _loadExercises();
  }

  @override
  void dispose() {
    _poller?.cancel();
    _topicController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final topic = _topicController.text.trim();
    if (topic.isEmpty) {
      setState(() => _error = 'Enter a topic first.');
      return;
    }
    setState(() {
      _submitting = true;
      _error = null;
      _run = null;
    });
    try {
      final id = await _api.startRun(topic: topic, difficulty: _difficulty);
      if (!mounted) return;
      await _refreshRun(id);
      _startPolling(id);
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _startPolling(int id) {
    _poller?.cancel();
    _poller =
        Timer.periodic(const Duration(seconds: 2), (_) => _refreshRun(id));
  }

  Future<void> _refreshRun(int id) async {
    try {
      final run = await _api.getRun(id);
      if (!mounted) return;
      setState(() => _run = run);
      if (run.status == 'completed' || run.status == 'failed') {
        _poller?.cancel();
        await _loadExercises();
      }
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    }
  }

  Future<void> _loadExercises() async {
    try {
      final exercises = await _api.getExercises();
      if (mounted) setState(() => _exercises = exercises);
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Whetstone exercise generator')),
        body: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 760),
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                Text('Generate an exercise',
                    style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 16),
                TextField(
                    controller: _topicController,
                    decoration: const InputDecoration(
                        labelText: 'Topic', border: OutlineInputBorder()),
                    onSubmitted: (_) => _submit()),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  key: ValueKey(_difficulty),
                  initialValue: _difficulty,
                  decoration: const InputDecoration(
                      labelText: 'Difficulty', border: OutlineInputBorder()),
                  items: const ['beginner', 'intermediate', 'advanced']
                      .map((value) =>
                          DropdownMenuItem(value: value, child: Text(value)))
                      .toList(),
                  onChanged: (value) => setState(() => _difficulty = value!),
                ),
                const SizedBox(height: 12),
                FilledButton(
                    onPressed: _submitting ? null : _submit,
                    child: Text(_submitting ? 'Starting…' : 'Generate')),
                if (_error != null) ...[
                  const SizedBox(height: 12),
                  Text(_error!,
                      style: TextStyle(
                          color: Theme.of(context).colorScheme.error)),
                ],
                if (_run != null) ...[
                  const SizedBox(height: 28),
                  Text('Run #${_run!.id}: ${_run!.status}',
                      style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  for (final candidate in _run!.candidates)
                    CandidateCard(candidate: candidate),
                  if (_run!.candidates.isEmpty)
                    const Padding(
                        padding: EdgeInsets.symmetric(vertical: 12),
                        child: Text(
                            'Waiting for the worker to generate candidates…')),
                ],
                const SizedBox(height: 28),
                Text('Published exercises',
                    style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 8),
                if (_exercises.isEmpty)
                  const Text('No exercises have been published yet.'),
                for (final exercise in _exercises)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Exercise #${exercise.id}',
                                style: Theme.of(context).textTheme.titleMedium),
                            const SizedBox(height: 8),
                            Text(exercise.problemStatement),
                          ]),
                    ),
                  ),
              ],
            ),
          ),
        ),
      );
}

class CandidateCard extends StatelessWidget {
  const CandidateCard({super.key, required this.candidate});
  final Candidate candidate;

  @override
  Widget build(BuildContext context) {
    final passed = candidate.verdict == 'pass';
    final failed = candidate.verdict == 'fail' || candidate.verdict == 'error';
    final color = passed
        ? Colors.green.shade100
        : failed
            ? Colors.grey.shade300
            : Theme.of(context).colorScheme.surfaceContainerHighest;
    return Card(
      color: color,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Candidate ${candidate.attemptNumber}: ${candidate.verdict}',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Text(candidate.problemStatement.isEmpty
              ? 'No problem statement was produced.'
              : candidate.problemStatement),
          if (failed && candidate.failureReason.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text('Failure reason: ${candidate.failureReason}'),
          ],
        ]),
      ),
    );
  }
}
