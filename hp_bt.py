#!/usr/bin/env python3

from __future__ import annotations

import sys
import random
from collections import deque
from typing import List, Set, Tuple, Optional


def parse_graph(path: str) -> Tuple[int, List[Set[int]]]:
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    first = raw_lines[0].split()
    n, m = map(int, first)

    adj: List[Set[int]] = [set() for _ in range(n)]

    for i in range(1, m + 1):
        v, u = map(int, raw_lines[i].split())
        if v == u:
            continue
        adj[v].add(u)
        adj[u].add(v)

    return n, adj


def generate_random_graph(n: int, dense: bool, seed: Optional[int]) -> Tuple[int, List[Set[int]]]:
    rng = random.Random(seed)
    adj: List[Set[int]] = [set() for _ in range(n)]

    p = 0.8 if dense else min(4.0 / n, 0.2)

    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j)
                adj[j].add(i)

    return n, adj


def is_connected(n: int, adj: List[Set[int]]) -> bool:
    if n <= 1:
        return True

    start = next((v for v in range(n) if adj[v]), None)
    if start is None:
        return False

    seen = [False] * n
    q = deque([start])
    seen[start] = True

    while q:
        v = q.popleft()
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True
                q.append(u)

    return all(seen)


def has_hamiltonian_path(n: int, adj: List[Set[int]]) -> Tuple[bool, int]:
    if n <= 1:
        return n == 1, 0

    if any(len(adj[v]) == 0 for v in range(n)):
        return False, 0

    if not is_connected(n, adj):
        return False, 0

    visited = [False] * n
    calls = 0
    neighbors = [sorted(adj[v], key=lambda x: len(adj[x])) for v in range(n)]

    def dfs(v: int, depth: int) -> bool:
        nonlocal calls
        calls += 1
        if depth == n:
            return True
        for u in neighbors[v]:
            if not visited[u]:
                visited[u] = True
                if dfs(u, depth + 1):
                    return True
                visited[u] = False
        return False

    for start in range(n):
        visited[start] = True
        if dfs(start, 1):
            return True, calls
        visited[start] = False

    return False, calls


def main() -> int:
    args = sys.argv[1:]

    stats = "--stats" in args
    if stats:
        args.remove("--stats")

    if args[0] == "--random":
