/// Typed representations of the frozen Django JSON response objects.
class Candidate {
  const Candidate(
      {required this.id,
      required this.attemptNumber,
      required this.problemStatement,
      required this.verdict,
      required this.failureReason});
  final int id;
  final int attemptNumber;
  final String problemStatement;
  final String verdict;
  final String failureReason;
  factory Candidate.fromJson(Map<String, dynamic> json) => Candidate(
      id: json['id'] as int,
      attemptNumber: json['attempt_number'] as int,
      problemStatement: json['problem_statement'] as String,
      verdict: json['verdict'] as String,
      failureReason: json['failure_reason'] as String);
}

class GenerationRun {
  const GenerationRun(
      {required this.id,
      required this.topic,
      required this.difficulty,
      required this.requestedCount,
      required this.status,
      required this.candidates});
  final int id;
  final String topic;
  final String difficulty;
  final int requestedCount;
  final String status;
  final List<Candidate> candidates;
  factory GenerationRun.fromJson(Map<String, dynamic> json) => GenerationRun(
      id: json['id'] as int,
      topic: json['topic'] as String,
      difficulty: json['difficulty'] as String,
      requestedCount: json['requested_count'] as int,
      status: json['status'] as String,
      candidates: (json['candidates'] as List<dynamic>)
          .map((item) => Candidate.fromJson(item as Map<String, dynamic>))
          .toList());
}

class Exercise {
  const Exercise(
      {required this.id,
      required this.problemStatement,
      required this.publishedAt,
      required this.winningCandidateId});
  final int id;
  final String problemStatement;
  final String publishedAt;
  final int winningCandidateId;
  factory Exercise.fromJson(Map<String, dynamic> json) => Exercise(
      id: json['id'] as int,
      problemStatement: json['problem_statement'] as String,
      publishedAt: json['published_at'] as String,
      winningCandidateId: json['winning_candidate_id'] as int);
}
class Discard {
  const Discard({
    required this.id,
    required this.topic,
    required this.problemStatement,
    required this.failureReason,
  });
  final int id;
  final String topic;
  final String problemStatement;
  final String failureReason;
  factory Discard.fromJson(Map<String, dynamic> json) => Discard(
      id: json['id'] as int,
      topic: json['topic'] as String,
      problemStatement: json['problem_statement'] as String,
      failureReason: json['failure_reason'] as String);
}

class CorpusSummary {
  const CorpusSummary({
    required this.generated,
    required this.kept,
    required this.discarded,
    required this.discards,
  });
  final int generated;
  final int kept;
  final int discarded;
  final List<Discard> discards;
  factory CorpusSummary.fromJson(Map<String, dynamic> json) => CorpusSummary(
      generated: json['generated'] as int,
      kept: json['kept'] as int,
      discarded: json['discarded'] as int,
      discards: (json['discards'] as List<dynamic>)
          .map((item) => Discard.fromJson(item as Map<String, dynamic>))
          .toList());
}