# 🔍 Fase 5 — Motor de Regras de Auditoria

Nesta fase criei o motor de regras que identifica as inconsistências nos dados contábeis e financeiros. O objetivo é cruzar as informações entre as tabelas e apontar situações que precisam de revisão.

---

## 🎯 Objetivo da Fase

Detectar automaticamente as inconsistências que foram plantadas na Fase 3:

- Divergências entre valores originais e valores pagos
- Conciliações marcadas como inconsistentes
- Movimentações bancárias sem conciliação
- Documentos fiscais cancelados ou inutilizados

---

## 🔧 Tecnologias Utilizadas

- **Python 3.x**
- **Pandas** — análise dos resultados das queries
- **SQLAlchemy** — conexão com MySQL
- **SQL** — queries de detecção nas tabelas

---

## 🔎 Regras de Auditoria

### 1. Divergências em Valores Pagos

Busca contas com status "Pago" onde o `valor_pago` é diferente do `valor_original`.

Isso pode indicar:
- Desconto não documentado
- Pagamento parcial marcado incorretamente como pago
- Erro de digitação

**Query:**
```sql
SELECT c.id_conta, e.razao_social, c.tipo_titulo,
       c.valor_original, c.valor_pago,
       c.valor_original - c.valor_pago AS diferenca
FROM contas_financeiras c
JOIN empresas e ON c.id_empresa = e.id_empresa
WHERE c.status_pagamento = 'Pago'
  AND c.valor_pago != c.valor_original
ORDER BY ABS(diferenca) DESC
```

---

### 2. Conciliações Inconsistentes

Busca conciliações com status "Inconsistente" ou onde há diferença entre o valor da conta e o valor da movimentação bancária.

**Query:**
```sql
SELECT conc.id_conciliacao, e.razao_social,
       cf.valor_pago AS valor_conta,
       mb.valor_movimentacao AS valor_banco,
       conc.diferenca_valor,
       conc.status_conciliacao
FROM conciliacoes conc
JOIN contas_financeiras cf ON conc.id_conta = cf.id_conta
JOIN movimentacoes_bancarias mb ON conc.id_movimentacao = mb.id_movimentacao
JOIN empresas e ON cf.id_empresa = e.id_empresa
WHERE conc.status_conciliacao = 'Inconsistente'
   OR conc.diferenca_valor != 0
```

---

### 3. Movimentações Sem Conciliação

Busca movimentações bancárias (entradas ou saídas) que não foram conciliadas com nenhum título financeiro.

Isso pode indicar:
- Lançamentos no extrato sem registro no financeiro
- Receitas/despesas não contabilizadas
- Movimentações que ainda precisam ser classificadas

**Query:**
```sql
SELECT mb.id_movimentacao, e.razao_social,
       mb.data_movimentacao, mb.tipo_operacao,
       mb.categoria, mb.valor_movimentacao
FROM movimentacoes_bancarias mb
JOIN empresas e ON mb.id_empresa = e.id_empresa
WHERE mb.conciliada = 0
ORDER BY mb.valor_movimentacao DESC
```

---

### 4. Documentos com Problema

Lista documentos fiscais cancelados ou inutilizados que podem precisar de revisão ou ajuste nos registros.

**Query:**
```sql
SELECT d.id_documento, e.razao_social,
       d.tipo_documento, d.numero_documento,
       d.data_emissao, d.status_documento
FROM documentos_fiscais d
JOIN empresas e ON d.id_empresa = e.id_empresa
WHERE d.status_documento IN ('Cancelada', 'Inutilizada')
```

---

## 🚀 Como Executar

### Pré-requisitos

- Banco de dados carregado (Fase 4)
- Arquivo `.env` configurado

### Execução

```bash
python src/auditoria/regras.py
```

### Saída esperada

```
============================================================
FiscalAudit AI — Motor de Regras de Auditoria
============================================================

1. Divergências em valores pagos:
   ⚠️  23 conta(s) com divergência encontrada(s)
  → Salvo em divergencias_pagamento.csv

2. Conciliações inconsistentes:
   ⚠️  13 conciliação(ões) inconsistente(s)
  → Salvo em conciliacoes_inconsistentes.csv

3. Movimentações bancárias sem conciliação:
   ⚠️  388 movimentação(ões) sem conciliação
   💰 Valor total: R$ 7,959,599.30
  → Salvo em movimentacoes_sem_conciliacao.csv

4. Documentos cancelados ou inutilizados:
   ℹ️  30 documento(s) para revisar
  → Salvo em documentos_problema.csv

============================================================
Auditoria concluída.
============================================================
```

---

## 📊 Relatórios Gerados

Os relatórios ficam salvos em `data/processed/`:

| Arquivo | Conteúdo |
|---------|----------|
| `divergencias_pagamento.csv` | Contas pagas com divergência de valor |
| `conciliacoes_inconsistentes.csv` | Conciliações com diferenças |
| `movimentacoes_sem_conciliacao.csv` | Movimentações bancárias não conciliadas |
| `documentos_problema.csv` | Documentos cancelados/inutilizados |

Esses CSVs podem ser abertos no Excel ou importados num dashboard para análise.

---

## 📌 Resultados da Auditoria

Rodando contra os dados da Fase 3, o motor detectou:

- **23 divergências** de pagamento (~10% das contas pagas, conforme planejado)
- **13 conciliações inconsistentes** (~15% das conciliações)
- **388 movimentações sem conciliação** (~78% do total — mais que os 40% esperados, porque nem todas as contas foram conciliadas)
- **30 documentos** cancelados/inutilizados

Os percentuais batem com as inconsistências que foram plantadas propositalmente na geração de dados.

---

## 🔍 Próximos Passos

Com as regras básicas funcionando, as próximas fases podem incluir:

- **Fase 6** — Análise exploratória e visualização dos dados
- **Fase 7** — Machine Learning para detectar anomalias além das regras fixas
- **Fase 8** — IA Generativa para gerar relatórios em linguagem natural
