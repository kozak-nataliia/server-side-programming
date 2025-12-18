from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional, Sequence

import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from django.db import close_old_connections, connection


Mode = Literal["threads", "processes"]


@dataclass(frozen=True)
class BenchmarkPoint:
    mode: Mode
    workers: int
    batch_size: int
    total_queries: int
    total_sec: float
    avg_ms: float


def _run_single_query() -> None:
    """One cheap DB query used for benchmarking.

    We intentionally use raw SQL to avoid ORM overhead differences between versions
    and to keep the task focused on *parallel DB access*.
    """
    # Ensure each worker uses a valid connection for its thread/process.
    close_old_connections()
    with connection.cursor() as cur:
        # Any stable query works; COUNT(*) exists in every dataset size.
        cur.execute('SELECT COUNT(*) FROM recipes_recipe')
        cur.fetchone()


def _run_batch(n: int) -> int:
    """Run n queries sequentially in the current worker."""
    for _ in range(n):
        _run_single_query()
    return n


def _process_worker(batch_size: int) -> int:
    """Worker entrypoint for ProcessPoolExecutor.

    We call django.setup() here to ensure settings/apps are ready in the child.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'cookbook.settings'))
    import django  # noqa: WPS433 (local import is intentional in subprocess)
    django.setup()
    close_old_connections()
    return _run_batch(batch_size)


def run_benchmark(
    *,
    mode: Mode,
    workers: int,
    total_queries: int = 200,
    batch_size: int = 10,
) -> BenchmarkPoint:
    """Run total_queries DB queries using parallel workers.

    - We split work into tasks of size batch_size.
    - Each task is executed by one worker (thread/process).
    """
    if workers < 1:
        raise ValueError('workers must be >= 1')
    if total_queries < 1:
        raise ValueError('total_queries must be >= 1')
    if batch_size < 1:
        raise ValueError('batch_size must be >= 1')

    tasks = (total_queries + batch_size - 1) // batch_size

    # Close any old/stale connections before parallel work starts.
    close_old_connections()

    t0 = time.perf_counter()

    if mode == 'threads':
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_run_batch, batch_size) for _ in range(tasks)]
            # drain futures
            done = 0
            for f in as_completed(futures):
                done += int(f.result())
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_process_worker, batch_size) for _ in range(tasks)]
            done = 0
            for f in as_completed(futures):
                done += int(f.result())

    total_sec = time.perf_counter() - t0
    done = min(done, total_queries)  # last batch may overshoot
    avg_ms = (total_sec / max(done, 1)) * 1000.0

    return BenchmarkPoint(
        mode=mode,
        workers=workers,
        batch_size=batch_size,
        total_queries=total_queries,
        total_sec=total_sec,
        avg_ms=avg_ms,
    )


def grid_search_optimal(
    *,
    modes: Sequence[Mode] = ('threads', 'processes'),
    workers_grid: Sequence[int] = (1, 2, 4, 8),
    batch_sizes: Sequence[int] = (1, 5, 10, 20),
    total_queries: int = 200,
) -> tuple[list[BenchmarkPoint], BenchmarkPoint]:
    """Try many (mode, workers, batch_size) and return all points + best point.

    "Best" is minimal total_sec.
    """
    points: list[BenchmarkPoint] = []
    best: Optional[BenchmarkPoint] = None

    for mode in modes:
        for batch in batch_sizes:
            for w in workers_grid:
                pt = run_benchmark(mode=mode, workers=w, batch_size=batch, total_queries=total_queries)
                points.append(pt)
                if best is None or pt.total_sec < best.total_sec:
                    best = pt

    assert best is not None
    return points, best
