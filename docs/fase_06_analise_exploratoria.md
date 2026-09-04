# 📊 Fase 6 — Análise Exploratória de Dados

Nesta fase criei um notebook Jupyter para explorar visualmente os dados e entender padrões nas inconsistências detectadas pelas regras de auditoria.

A análise exploratória (EDA — Exploratory Data Analysis) é fundamental antes de partir para modelos de machine learning, porque ajuda a entender o que está acontecendo nos dados.

---

## 🎯 Objetivo da Fase

- Visualizar a distribuição dos dados nas tabelas
- Analisar padrões nas divergências de pagamento
- Entender o comportamento das conciliações
- Identificar empresas com mais problemas
- Observar tendências ao longo do tempo

---

## 🔧 Tecnologias Utilizadas

- **Jupyter Notebook** — ambiente interativo para análise
- **Pandas** — manipulação de dados
- **Matplotlib** — visualizações básicas
- **Seaborn** — visualizações estatísticas mais bonitas
- **SQLAlchemy** — conexão com MySQL

---

## 📈 Análises Realizadas

### 1. Visão Geral dos Dados

Contagem de registros em cada tabela e visualização em gráfico de barras horizontais.

**Resultado:**
- 10 empresas
- 500 movimentações bancárias
- 289 documentos fiscais (300 originais − 11 duplicatas separadas no ETL)
- 400 contas financeiras
- 112 conciliações

---

### 2. Divergências de Pagamento

Análise detalhada das 23 contas onde o `valor_pago` é diferente do `valor_original`.

**Gráficos gerados:**
- Histograma da diferença absoluta em R$
- Histograma do percentual de diferença
- Distribuição por tipo de título (A Receber vs A Pagar)

**Descobertas:**
- A maioria das divergências está entre 5% e 15% do valor original
- Tanto títulos a receber quanto a pagar apresentam divergências
- O total acumulado em divergências é significativo

---

### 3. Conciliações

Análise do status das conciliações e movimentações não conciliadas.

**Gráficos gerados:**
- Pizza do status (Consistente vs Inconsistente)
- Distribuição de movimentações não conciliadas por tipo

**Descobertas:**
- ~12% das conciliações estão marcadas como "Inconsistente"
- ~78% das movimentações bancárias ainda não foram conciliadas
- A maioria das movimentações sem conciliação é de entrada

---

### 4. Análise por Empresa

Identificação de quais empresas concentram mais divergências.

**Gráfico gerado:**
- Barras com quantidade de divergências por empresa

**Descobertas:**
- As divergências estão distribuídas entre várias empresas
- Algumas empresas concentram mais problemas e precisam de atenção especial

---

### 5. Análise Temporal

Visualização de movimentações bancárias ao longo do tempo (por mês).

**Gráfico gerado:**
- Barras agrupadas mostrando entradas e saídas por mês

**Descobertas:**
- O volume de movimentações varia ao longo do ano
- Entrada e saída seguem padrões relativamente equilibrados

---

### 6. Documentos Fiscais

Distribuição dos documentos por tipo (NF-e, NFS-e, CT-e, NFC-e) e status (Ativa, Cancelada, Inutilizada).

**Gráfico gerado:**
- Barras empilhadas mostrando quantidade por tipo e status

**Descobertas:**
- ~10% dos documentos estão cancelados ou inutilizados
- A distribuição entre os tipos de documento parece balanceada

---

## 🚀 Como Executar o Notebook

### 1. Instalar dependências adicionais

```bash
pip install matplotlib seaborn jupyter
```

### 2. Subir o Jupyter

```bash
cd fiscalaudit-ai
jupyter notebook
```

Isso abrirá o Jupyter no navegador.

### 3. Abrir o notebook

Navegue até `notebooks/analise_exploratoria.ipynb` e execute as células sequencialmente (Shift + Enter).

**Importante:** o arquivo `.env` precisa estar configurado para o notebook conectar no banco.

---

## 📌 Principais Conclusões

### Volume de Dados
- Base com 10 empresas, 1.401 registros totais distribuídos nas 7 tabelas
- Volume suficiente para análise e modelagem

### Qualidade dos Dados
- As inconsistências propositais da Fase 3 foram confirmadas:
  - 23 divergências de pagamento (~10% das contas pagas)
  - 13 conciliações inconsistentes (~12%)
  - 388 movimentações sem conciliação (~78%)

### Padrões Identificados
- Divergências concentradas na faixa de 5-15%
- Algumas empresas concentram mais problemas
- Movimentações não conciliadas são oportunidade de melhoria

---

## 🔍 Próximos Passos

Com a análise exploratória concluída, as próximas etapas naturais são:

- **Fase 7** — Treinar modelo de Machine Learning para detectar anomalias além das regras fixas
- **Fase 8** — IA Generativa para gerar relatórios em linguagem natural
- **Fase 9** — Dashboard interativo com Streamlit para visualizar tudo de forma amigável
