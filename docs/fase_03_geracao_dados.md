# 📊 Fase 3 — Geração de Dados Fictícios

Nesta etapa, criei um script Python para gerar dados fictícios realistas que simulam o ambiente de um escritório contábil com múltiplos clientes.

O objetivo foi criar uma base de dados completa para testar o sistema de auditoria, incluindo **inconsistências propositais** que o motor de regras deverá identificar nas próximas fases.

---

## 🎯 Objetivo da Fase

Gerar dados fictícios para as 7 tabelas do banco de dados, simulando:

- Empresas clientes do escritório contábil
- Seus clientes e fornecedores
- Movimentações bancárias (extratos)
- Documentos fiscais (NF-e, NFS-e, CT-e)
- Contas a pagar e a receber
- Conciliações entre contas e movimentações

Além disso, incluir **inconsistências propositais** para validar as regras de auditoria que serão implementadas.

---

## 📁 Estrutura dos Dados Gerados

### Volume de Dados

| Tabela                     | Quantidade |
| -------------------------- | ---------- |
| Empresas                   | 10         |
| Clientes                   | 50         |
| Fornecedores               | 40         |
| Movimentações Bancárias    | 500        |
| Documentos Fiscais         | 300        |
| Contas Financeiras         | 400        |
| Conciliações               | 112        |

### Distribuição por Empresa

- **~50 movimentações bancárias** por empresa (extratos de 12 meses)
- **~30 documentos fiscais** por empresa (NF-e, NFS-e, CT-e)
- **~40 contas financeiras** por empresa (títulos a pagar e a receber)
- **~60% das contas pagas** possuem conciliação

---

## 🔧 Tecnologias Utilizadas

- **Python 3.x**
- **Pandas** — manipulação e exportação de dados para CSV
- **Faker** — geração de dados fictícios realistas (nomes, empresas, datas, CNPJs)

---

## ⚠️ Inconsistências Propositais

Para testar o sistema de auditoria, incluí as seguintes inconsistências intencionais:

### 1. Notas Fiscais Duplicadas (~2%)

Algumas chaves de acesso de NF-e aparecem mais de uma vez, simulando emissão duplicada acidental.

**Impacto esperado:** o motor de regras deve identificar documentos com `chave_acesso` duplicada.

### 2. Divergências em Valores Pagos (~10%)

Em aproximadamente 10% das contas com status "Pago", o `valor_pago` é diferente do `valor_original` (valores entre 85% e 95% do original).

**Impacto esperado:** a auditoria deve sinalizar títulos onde o valor pago diverge do valor original sem justificativa.

### 3. Conciliações com Diferenças (~15%)

Cerca de 15% das conciliações têm status `Inconsistente`, com diferenças entre o valor da conta financeira e o valor da movimentação bancária.

**Impacto esperado:** o sistema deve listar todas as conciliações inconsistentes para revisão do contador.

### 4. Movimentações sem Conciliação (~40%)

Aproximadamente 40% das movimentações bancárias **não** possuem conciliação, ou seja, são entradas/saídas no extrato sem correspondência com títulos registrados.

**Impacto esperado:** o motor de auditoria deve identificar movimentações bancárias sem correspondência no financeiro.

---

## 🚀 Como Executar o Script

### Pré-requisitos

```bash
pip install pandas faker
```

### Execução

```bash
cd fiscalaudit-ai
python src/gerador/gerar_dados_ficticios.py
```

### Saída

Os arquivos CSV serão gerados em `data/raw/`:

```
data/raw/
├── clientes.csv
├── fornecedores.csv
├── empresas.csv
├── movimentacoes_bancarias.csv
├── documentos_fiscais.csv
├── contas_financeiras.csv
└── conciliacoes.csv
```

---

## 📌 Decisões Técnicas

### Uso de `random.seed(42)` e `Faker.seed(42)`

Garante que os dados gerados sejam **reprodutíveis** — executar o script novamente produz exatamente os mesmos dados. Isso facilita testes e validações.

### CNPJs e CPFs Simplificados

Os CNPJs e CPFs gerados **não** passam pela validação de dígitos verificadores. Para o propósito deste projeto (auditoria de dados financeiros), o formato é suficiente.

Se necessário, uma validação real pode ser implementada futuramente.

### Relacionamentos Respeitados

- Documentos de **saída** → vinculados a `clientes`
- Documentos de **entrada** → vinculados a `fornecedores`
- Títulos **a receber** → vinculados a `clientes`
- Títulos **a pagar** → vinculados a `fornecedores`

Isso garante coerência com as regras de negócio definidas na modelagem.

### Encoding UTF-8 com BOM

Os CSVs são salvos com `encoding='utf-8-sig'` para garantir compatibilidade com Excel e ferramentas que exigem BOM (Byte Order Mark).

---

## 📊 Exemplo de Dados Gerados

### Empresa

```csv
id_empresa,razao_social,cnpj,ramo_atividade,regime_tributario,criado_em
1,Silva e Rodrigues Ltda,12.345.678/0001-90,Comércio,Simples Nacional,2023-05-12 14:30:00
```

### Movimentação Bancária

```csv
id_movimentacao,id_empresa,data_movimentacao,tipo_operacao,categoria,descricao_movimentacao,valor_movimentacao,conciliada
1,1,2024-08-15,Entrada,Receita de Venda,Recebimento ref. NF 12345,15800.50,1
```

### Documento Fiscal

```csv
id_documento,id_empresa,id_cliente,id_fornecedor,tipo_documento,numero_documento,chave_acesso,data_emissao,tipo_operacao,valor,status_documento
1,1,23,NULL,NF-e,123456,12345678901234567890123456789012345678901234,2024-08-14,Saída,15800.50,Ativa
```

---

## 🔍 Próximos Passos

Com os dados gerados, as próximas etapas serão:

1. **Fase 4** — Pipeline ETL para carregar os CSVs no MySQL
2. **Fase 5** — Motor de regras de auditoria para identificar as inconsistências
3. **Fase 6** — Análise exploratória dos dados
4. **Fase 7** — Modelo de Machine Learning para detecção de anomalias

---

**Fase concluída!** Os dados fictícios estão prontos para alimentar o banco de dados e validar o sistema de auditoria.
