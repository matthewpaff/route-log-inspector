"""Replay generated, disclosed request-log scenarios without external services."""
import argparse
import io
import json
from pathlib import Path

from analysis import compare_samples, trace_timeline, window_rows
from inspector import evaluate_slo, read_rows, summarize


def rows(values):
    return read_rows(io.BytesIO(('\n'.join(json.dumps(row) for row in values) + '\n').encode()))


def evaluate(case):
    data = case['input']
    if case['kind'] == 'parse':
        parsed = read_rows(io.BytesIO(data['jsonl'].encode('utf-8')))
        return {'rows': len(parsed)}
    parsed = rows(data['rows'])
    if case['kind'] == 'summary':
        result = summarize(parsed, data.get('route'), data.get('trace_id'))
        return {'routes': result['routes'], 'total_requests': result['total_requests']}
    if case['kind'] == 'slo':
        result = evaluate_slo(summarize(parsed), data['p95_limit_ms'], data['error_rate_limit_pct'])
        return {'passed': result['passed'],
                'violations': [[row['route'], row['check']] for row in result['violations']]}
    if case['kind'] == 'window':
        selected = window_rows(parsed, data.get('since'), data.get('until'))
        return {'trace_ids': [row['trace_id'] for row in selected]}
    if case['kind'] == 'timeline':
        result = trace_timeline(parsed, data['trace_id'])
        return {'events': result['events'], 'total_requests': result['total_requests']}
    if case['kind'] == 'baseline':
        return {'routes': compare_samples(rows(data['baseline']), parsed, data['minimum_requests'])['routes']}
    raise ValueError('Unknown scenario kind')


def check_case(case):
    if not isinstance(case, dict) or case.get('schema_version') != 1 or case.get('synthetic') is not True:
        raise AssertionError('Expected a disclosed version-1 synthetic fixture')
    try:
        actual = evaluate(case)
    except ValueError as error:
        if 'error_contains' not in case or case['error_contains'] not in str(error):
            raise AssertionError('Unexpected validation error: ' + str(error)) from error
        return
    if 'error_contains' in case:
        raise AssertionError('Expected validation rejection')
    if actual != case['expected']:
        raise AssertionError(f"{case['id']}: expected {case['expected']!r}, received {actual!r}")


def load_cases(directory):
    paths = sorted(Path(directory).glob('*.json'))
    if not 1 <= len(paths) <= 2000:
        raise ValueError('Expected 1-2000 scenario files')
    seen = set()
    for path in paths:
        if path.stat().st_size > 256 * 1024:
            raise ValueError('Scenario exceeds 256 KiB')
        case = json.loads(path.read_text(encoding='utf-8'))
        if case['id'] in seen:
            raise ValueError('Duplicate scenario ID')
        seen.add(case['id'])
        yield path, case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=Path(__file__).resolve().parent / 'scenarios')
    args = parser.parse_args()
    count = 0
    try:
        for path, case in load_cases(args.directory):
            try:
                check_case(case)
            except (AssertionError, ValueError, KeyError, TypeError) as error:
                raise ValueError(f'{path.name}: {error}') from error
            count += 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, 'error: ' + str(error) + '\n')
    print(json.dumps({'passed': count, 'basis': 'generated synthetic regression cases; not historical work'}))


if __name__ == '__main__':
    main()
