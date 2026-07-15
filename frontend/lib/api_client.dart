import 'dart:convert';

import 'package:http/http.dart' as http;

import 'models.dart';

/// A compile-time value, set with --dart-define=API_BASE_URL=... when needed.
const apiBaseUrl = String.fromEnvironment('API_BASE_URL',
    defaultValue: 'http://localhost:8000');

class ApiClient {
  ApiClient({http.Client? client}) : _client = client ?? http.Client();
  final http.Client _client;

  Uri _uri(String path) =>
      Uri.parse('${apiBaseUrl.replaceFirst(RegExp(r'/+$'), '')}$path');

  Future<int> startRun(
      {required String topic, required String difficulty}) async {
    final response = await _client.post(_uri('/api/runs'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'topic': topic, 'difficulty': difficulty}));
    final body = _object(response);
    if (response.statusCode != 201){
      throw ApiException(body['error'] as String? ?? 'Could not start a run.');
    }
    return body['id'] as int;
  }

  Future<GenerationRun> getRun(int id) async {
    final response = await _client.get(_uri('/api/runs/$id'));
    final body = _object(response);
    if (response.statusCode != 200) {
      throw ApiException(body['error'] as String? ?? 'Could not load the run.');
    }
    return GenerationRun.fromJson(body);
  }

  Future<List<Exercise>> getExercises() async {
    final response = await _client.get(_uri('/api/exercises'));
    final body = _object(response);
    if (response.statusCode != 200) {
      throw ApiException(
          body['error'] as String? ?? 'Could not load exercises.');
    }
    return (body['exercises'] as List<dynamic>)
        .map((item) => Exercise.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Map<String, dynamic> _object(http.Response response) {
    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } on FormatException {
      throw ApiException('The server returned invalid JSON.');
    }
  }
}

class ApiException implements Exception {
  ApiException(this.message);
  final String message;
  @override
  String toString() => message;
}
