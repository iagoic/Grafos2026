#!/usr/bin/env python3

from __future__ import annotations

import sys
import random
from typing import List, Set, Tuple, Optional


def parse_graph(path: str) -> Tuple[int, List[Set[int]]]:
    with open(path, "r", encoding="utf-8") as f:
        raw = [line.strip() for line in f if line.strip()]

    n, m = map(int, raw[0].split())
    adj: List[Set[int]] = [set() for _ in range(n)]

    for i in range(1, m + 1):
        v, u = map(int, raw[i].split())
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


def has_hamiltonian_path_dp(n: int, adj: List[Set[int]]) -> Tuple[bool, int, int]:
    if n <= 1:
        return n == 1, 1 if n == 1 else 0, 0

    max_mask = 1 << n
    dp = [[False] * n for _ in range(max_mask)]

    states = 0
    transitions = 0

    for v in range(n):
        dp[1 << v][v] = True
        states += 1

    for mask in range(max_mask):
        for v in range(n):
            if not (mask & (1 << v)) or not dp[mask][v]:
                continue
            for u in adj[v]:
                if mask & (1 << u):
                    continue
                next_mask = mask | (1 << u)
                transitions += 1
                if not dp[next_mask][u]:
                    dp[next_mask][u] = True
                    states += 1

    full_mask = (1 << n) - 1
    return any(dp[full_mask][v] for v in range(n)), states, transitions


def main() -> int:
    args = sys.argv[1:]

    stats = "--stats" in args
    if stats:
        args.remove("--stats")

    if args[0] == "--random":
        n = int(args[1])
        mode = args[2]
        seed = None
        if "--seed" in args:
            seed = int(args[args.index("--seed") + 1])
        n, adj = generate_random_graph(n, dense=(mode == "--dense"), seed=seed)
    else:
        n, adj = parse_graph(args[0])

    ok, states, transitions = has_hamiltonian_path_dp(n, adj)

    print("SIM" if ok else "NÃO")
    if stats:
        print(f"[stats] states={states} transitions={transitions}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
