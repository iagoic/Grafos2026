# README

## Projeto: Caminho Hamiltoniano – Soluções Exatas e Análise Experimental

## Visão geral do projeto

Este repositório contém a implementação e a análise experimental de duas abordagens exatas para o problema do **Caminho Hamiltoniano** na sua versão de decisão. O objetivo do problema é determinar se existe um caminho simples em um grafo não direcionado que visite todos os vértices exatamente uma vez.

Foram implementadas duas estratégias clássicas da literatura:

- **Backtracking com busca em profundidade (DFS)**
- **Programação dinâmica por subconjuntos (bitmask)**

Além das implementações dos algoritmos, o repositório inclui um script de benchmark responsável por gerar instâncias de grafos aleatórios, executar os algoritmos sobre essas instâncias e coletar métricas de desempenho, como tempo de execução e esforço computacional.

---

## Estrutura do repositório

O repositório contém os seguintes arquivos principais:

### `hp_bt.py`

Implementação do algoritmo de Caminho Hamiltoniano por **backtracking (DFS)**.

- Resolve o problema de decisão
- Pode ser executado diretamente pela linha de comando

### `hp_dp.py`

Implementação do algoritmo de Caminho Hamiltoniano por **programação dinâmica por subconjuntos**.

- Utiliza uma tabela DP indexada por subconjuntos de vértices e vértice final

### `benchmark.py`

Script de experimentos responsável por:

- Gerar grafos aleatórios esparsos e densos
- Salvar as instâncias em arquivos
- Executar `hp_bt.py` e `hp_dp.py` sobre cada instância
- Coletar métricas de tempo e contadores internos
- Salvar os resultados em arquivos CSV
- Opcionalmente gerar imagens dos grafos usando `networkx`

Durante a execução do benchmark, também são criados os diretórios:

### `instancias/`

Contém os arquivos de entrada dos grafos gerados automaticamente.

### `imagens/`

Contém imagens PNG dos grafos, quando o benchmark é executado com a opção de plotagem.

---

## Requisitos do sistema

- Python versão **3.9 ou superior**
- Sistema operacional Linux, macOS ou Windows

### Bibliotecas Python necessárias

#### Para executar apenas os algoritmos

- Nenhuma biblioteca externa além da biblioteca padrão do Python

#### Para executar o benchmark com geração de imagens

- `networkx`
- `matplotlib`

Essas bibliotecas são utilizadas apenas no benchmark para visualização e não afetam a execução dos algoritmos principais.

---

## Instalação do ambiente

Recomenda-se o uso de um ambiente virtual Python.

### Passos sugeridos

1. Criar o ambiente virtual:
```bash
python -m venv venv
```

2. Ativar o ambiente virtual:

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

3. Instalar dependências para o benchmark (opcional):
```bash
pip install networkx matplotlib
```

**Nota:** Caso apenas os algoritmos `hp_bt.py` e `hp_dp.py` sejam utilizados, nenhuma instalação adicional é necessária.

---

## Formato do arquivo de entrada

Os algoritmos esperam um grafo não direcionado no seguinte formato:

- **Primeira linha:** dois inteiros `n m`
  - `n` é o número de vértices
  - `m` é o número de arestas

- **Próximas m linhas:** dois inteiros `v u`
  - Representam uma aresta não direcionada entre os vértices `v` e `u`

### Restrições

- Os vértices devem estar rotulados de `0` a `n-1`
- Self-loops são ignorados
- Arestas duplicadas não causam erro

---

## Execução dos algoritmos

### Execução com arquivo de entrada

**Backtracking:**
```bash
python hp_bt.py entrada.txt
```

**Programação dinâmica:**
```bash
python hp_dp.py entrada.txt
```

A saída padrão será exclusivamente:

- `SIM`, se existe caminho Hamiltoniano
- `NÃO`, caso contrário

### Execução com geração de grafo aleatório

Ambos os algoritmos permitem gerar grafos aleatórios diretamente pela linha de comando.

**Grafo esparso:**
```bash
python hp_bt.py --random 10 --sparse
python hp_dp.py --random 10 --sparse
```

**Grafo denso:**
```bash
python hp_bt.py --random 10 --dense
python hp_dp.py --random 10 --dense
```

**Fixar a semente aleatória:**
```bash
python hp_bt.py --random 10 --dense --seed 42
```

### Coleta de métricas internas

Para imprimir métricas no `stderr`:

**Backtracking:**
```bash
python hp_bt.py entrada.txt --stats
```

Métrica coletada:
- Número de chamadas recursivas da DFS

**Programação dinâmica:**
```bash
python hp_dp.py entrada.txt --stats
```

Métricas coletadas:
- Número de estados DP visitados
- Número de transições avaliadas

Essas métricas são usadas automaticamente pelo benchmark.

---

## Execução do benchmark

O script `benchmark.py` automatiza os experimentos descritos na Parte D do relatório técnico.

**Execução básica:**
```bash
python benchmark.py
```

**Execução com geração de imagens dos grafos:**
```bash
python benchmark.py --plot
```

Durante a execução, o benchmark:

- Gera grafos para diferentes tamanhos de `n`
- Considera grafos esparsos e densos
- Executa múltiplas instâncias por configuração
- Aplica timeout por execução
- Salva resultados consolidados em CSV

### Arquivos de saída do benchmark

Após a execução, são gerados:

#### `results.csv`

Contém os resultados individuais de cada execução, incluindo:

- Algoritmo
- Tamanho do grafo
- Densidade
- Tempo de execução
- Métricas internas
- Status da execução (ok, timeout ou erro)

#### `summary.csv`

Contém estatísticas agregadas por algoritmo, tamanho e densidade:

- Média e mediana do tempo de execução
- Média e mediana das métricas internas

Esses arquivos são utilizados posteriormente para gerar gráficos e análises no relatório técnico.

---

## Observações sobre desempenho

- O algoritmo de **backtracking** apresenta desempenho muito eficiente em grafos densos, mas pode sofrer explosão combinatória em grafos esparsos dependendo da estrutura do grafo.

- A **programação dinâmica por subconjuntos** apresenta crescimento exponencial previsível, tanto em tempo quanto em espaço, tornando-se rapidamente inviável para valores maiores de `n`.

- A análise experimental evidencia claramente essas diferenças, justificando a comparação entre as duas abordagens.
