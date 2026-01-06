"""Time-scoped diagnostics for supplied synthetic or locally provided request rows."""
from datetime import datetime, timezone
from decimal import Decimal
import re

from inspector import summarize


def instant(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 40:
        raise ValueError('Time bound must be a bounded ISO timestamp')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError('Time bound must include a timezone')
        return result.astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        raise ValueError('Invalid timezone-aware ISO time bound') from error


def window_rows(rows, since=None, until=None):
    """Select a half-open [since, until) window using absolute instants."""
    lower = instant(since) if since is not None else None
    upper = instant(until) if until is not None else None
    if lower is not None and upper is not None and lower >= upper:
        raise ValueError('Time window must have positive duration')
    return [row for row in rows if (lower is None or instant(row['timestamp']) >= lower)
            and (upper is None or instant(row['timestamp']) < upper)]


def trace_timeline(rows, trace_id):
    if not isinstance(trace_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', trace_id):
        raise ValueError('Invalid trace ID filter')
    selected = [dict(row) for row in rows if row['trace_id'] == trace_id]
    selected.sort(key=lambda row: (instant(row['timestamp']), row['route'], row['status'], row['duration_ms']))
    return {'trace_id': trace_id, 'events': selected, 'total_requests': len(selected),
            'basis': 'observed rows; ordering does not prove causal relationships'}


def compare_samples(baseline_rows, current_rows, minimum_requests=20):
    if type(minimum_requests) is not int or not 1 <= minimum_requests <= 50000:
        raise ValueError('minimum_requests must be 1-50000')
    baseline = {row['route']: row for row in summarize(baseline_rows)['routes']}
    current = {row['route']: row for row in summarize(current_rows)['routes']}
    comparisons = []
    for route in sorted(baseline.keys() | current.keys()):
        before, after = baseline.get(route), current.get(route)
        item = {'route': route, 'baseline_requests': before['requests'] if before else 0,
                'current_requests': after['requests'] if after else 0}
        if before is None:
            item['status'] = 'new_route'
        elif after is None:
            item['status'] = 'missing_route'
        elif min(before['requests'], after['requests']) < minimum_requests:
            item['status'] = 'insufficient_sample'
        else:
            item.update(status='compared', p95_delta_ms=after['p95_ms'] - before['p95_ms'],
                        error_rate_delta_pct=format(
                            Decimal(after['errors_5xx'] * 100) / after['requests']
                            - Decimal(before['errors_5xx'] * 100) / before['requests'], '.2f'))
        comparisons.append(item)
    return {'routes': comparisons, 'minimum_requests': minimum_requests,
            'basis': 'descriptive sample comparison; no significance or production claim'}
