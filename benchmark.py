#!/usr/bin/env python3

from __future__ import annotations

import csv
import os
import random
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


N_SIZES = [5, 6, 9, 11, 16, 20]
DENSIDADES = ["esparso", "denso"]

INSTANCIAS_POR_CONFIG = 5
BASE_SEMENTE = 12345
TIMEOUT_SEC = 2.0

DIR_INSTANCIAS = "instancias"
DIR_IMAGENS = "imagens"

ARQ_RESULTADOS = "results.csv"
ARQ_RESUMO = "summary.csv"

HP_BT = os.path.join(os.path.dirname(__file__), "hp_bt.py")
HP_DP = os.path.join(os.path.dirname(__file__), "hp_dp.py")


@dataclass
class RunResult:
    algoritmo: str
    n_vertices: int
    densidade: str
    id_instancia: int
    semente: int
    status_execucao: str
    resposta: str
    tempo_segundos: float
    metrica_1: Optional[int]
    metrica_2: Optional[int]
    arquivo_instancia: str
    arquivo_imagem: str
    stderr_ultimas_linhas: str


def _p_por_densidade(n: int, densidade: str) -> float:
    if n <= 1:
        return 0.0
    if densidade == "denso":
        return 0.8
    return min(4.0 / n, 0.2)


def gerar_grafo_gnp(n: int, p: float, seed: int) -> List[Set[int]]:
    rng = random.Random(seed)
    adj: List[Set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j)
                adj[j].add(i)
    return adj


def salvar_instancia(path: str, n: int, adj: List[Set[int]]) -> None:
    edges: List[Tuple[int, int]] = []
    for v in range(n):
        for u in adj[v]:
            if v < u:
                edges.append((v, u))
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{n} {len(edges)}\n")
        for v, u in edges:
            f.write(f"{v} {u}\n")


def plotar_grafo_png(path_png: str, n: int, adj: List[Set[int]], titulo: str) -> None:
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for v in range(n):
        for u in adj[v]:
            if v < u:
                G.add_edge(v, u)

    pos = nx.spring_layout(G, seed=1)

    plt.figure()
    plt.title(titulo)
    nx.draw_networkx(G, pos=pos, with_labels=True, node_size=400, font_size=8)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path_png, dpi=150)
    plt.close()


def _stderr_tail(stderr_str: str, max_lines: int = 5) -> str:
    lines = [ln for ln in stderr_str.splitlines() if ln.strip()]
    return "\n".join(lines[-max_lines:])


def _run_solver(script_path: str, arquivo_entrada: str, timeout_sec: float) -> Tuple[str, str, str, float]:
    cmd = [sys.executable, script_path, arquivo_entrada, "--stats"]

    t0 = time.perf_counter()
    try:
        cp = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        dt = time.perf_counter() - t0
    except subprocess.TimeoutExpired as e:
        dt = time.perf_counter() - t0
        out = (e.stdout or "").strip()
        err = (e.stderr or "").strip()
        return "timeout", out, err, dt
    except Exception as e:
        dt = time.perf_counter() - t0
        return "erro", "", str(e), dt

    out = (cp.stdout or "").strip()
    err = (cp.stderr or "").strip()

    if cp.returncode != 0:
        return "erro", out, err, dt

    if out not in {"SIM", "NÃO"}:
        return "erro", out, err, dt

    return "ok", out, err, dt


def _parse_bt_metrics(stderr_str: str) -> Tuple[Optional[int], Optional[int]]:
    for line in stderr_str.splitlines():
        line = line.strip()
        if line.startswith("[stats]") and "recursive_calls=" in line:
            try:
                val = int(line.split("recursive_calls=")[-1].strip())
                return val, None
            except ValueError:
                return None, None
    return None, None


def _parse_dp_metrics(stderr_str: str) -> Tuple[Optional[int], Optional[int]]:
    for line in stderr_str.splitlines():
        line = line.strip()
        if line.startswith("[stats]") and "states=" in line and "transitions=" in line:
            try:
                parts = line.replace("[stats]", "").strip().split()
                kv = {}
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        kv[k] = v
                states = int(kv.get("states")) if "states" in kv else None
                trans = int(kv.get("transitions")) if "transitions" in kv else None
                return states, trans
            except Exception:
                return None, None
    return None, None


def run_all(plotar: bool) -> List[RunResult]:
    if not os.path.exists(HP_BT):
        raise FileNotFoundError(f"Arquivo não encontrado: {HP_BT}")
    if not os.path.exists(HP_DP):
        raise FileNotFoundError(f"Arquivo não encontrado: {HP_DP}")

    os.makedirs(DIR_INSTANCIAS, exist_ok=True)
    os.makedirs(DIR_IMAGENS, exist_ok=True)

    results: List[RunResult] = []

    for n in N_SIZES:
        for densidade in DENSIDADES:
            p = _p_por_densidade(n, densidade)

            for instance_id in range(INSTANCIAS_POR_CONFIG):
                seed = BASE_SEMENTE + (n * 1000) + (0 if densidade == "esparso" else 500) + instance_id

                nome_base = f"n{n}_{densidade}_id{instance_id}_seed{seed}"
                arq_inst = os.path.join(DIR_INSTANCIAS, f"{nome_base}.txt")
                arq_png = os.path.join(DIR_IMAGENS, f"{nome_base}.png")

                adj = gerar_grafo_gnp(n=n, p=p, seed=seed)
                salvar_instancia(arq_inst, n, adj)

                if plotar:
                    titulo = f"{nome_base} (p={p:.3f})"
                    plotar_grafo_png(arq_png, n, adj, titulo=titulo)
                else:
                    arq_png = ""

                status, out, err, dt = _run_solver(HP_BT, arq_inst, TIMEOUT_SEC)
                m1, m2 = _parse_bt_metrics(err)
                results.append(
                    RunResult(
                        algoritmo="bt",
                        n_vertices=n,
                        densidade=densidade,
                        id_instancia=instance_id,
                        semente=seed,
                        status_execucao=status,
                        resposta=out if status == "ok" else "",
                        tempo_segundos=dt,
                        metrica_1=m1,
                        metrica_2=m2,
                        arquivo_instancia=arq_inst,
                        arquivo_imagem=arq_png,
                        stderr_ultimas_linhas=_stderr_tail(err),
                    )
                )

                status, out, err, dt = _run_solver(HP_DP, arq_inst, TIMEOUT_SEC)
                m1, m2 = _parse_dp_metrics(err)
                results.append(
                    RunResult(
                        algoritmo="dp",
                        n_vertices=n,
                        densidade=densidade,
                        id_instancia=instance_id,
                        semente=seed,
                        status_execucao=status,
                        resposta=out if status == "ok" else "",
                        tempo_segundos=dt,
                        metrica_1=m1,
                        metrica_2=m2,
                        arquivo_instancia=arq_inst,
                        arquivo_imagem=arq_png,
                        stderr_ultimas_linhas=_stderr_tail(err),
                    )
                )

    return results


def write_results_csv(rows: List[RunResult], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "algoritmo",
            "n_vertices",
            "densidade",
            "id_instancia",
            "semente",
            "status_execucao",
            "resposta",
            "tempo_segundos",
            "metrica_1",
            "metrica_2",
            "arquivo_instancia",
            "arquivo_imagem",
            "stderr_ultimas_linhas",
        ])
        for r in rows:
            w.writerow([
                r.algoritmo,
                r.n_vertices,
                r.densidade,
                r.id_instancia,
                r.semente,
                r.status_execucao,
                r.resposta,
                f"{r.tempo_segundos:.6f}",
                "" if r.metrica_1 is None else r.metrica_1,
                "" if r.metrica_2 is None else r.metrica_2,
                r.arquivo_instancia,
                r.arquivo_imagem,
                r.stderr_ultimas_linhas,
