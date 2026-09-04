# 🧾 FiscalAudit AI

> **Plataforma de Engenharia de Dados e Inteligência Artificial para conciliação e identificação de inconsistências em dados contábeis e financeiros.**

---

## 🎯 Problema que este projeto resolve

Escritórios de contabilidade recebem dados financeiros de dezenas de clientes e precisam conferir manualmente se:

- Entradas e saídas estão coerentes entre si
- Receitas estão compatíveis com os registros fiscais
- Notas fiscais não estão duplicadas
- Existem valores fora do padrão histórico
- Informações de diferentes fontes divergem (banco × NF-e × sistema financeiro)
- Determinadas movimentações precisam de revisão antes do fechamento

O **FiscalAudit AI** automatiza esse processo: organiza, cruza e analisa os dados, entregando ao contador exatamente o que merece atenção.

---

## 🏗️ Arquitetura do Pipeline

```
        Arquivos dos Clientes
               ↓
           Python (ETL)
               ↓
      Limpeza e Validação
               ↓
            MySQL
               ↓
      Motor de Regras de Auditoria
               ↓
        Machine Learning
        (Detecção de Anomalias)
               ↓
          IA Generativa
          (LLM Assistente)
               ↓
    Relatório de Inconsistências
         para o Contador
```

---

## 📁 Estrutura do Projeto

```
fiscalaudit-ai/
│
├── docs/                          # Documentação e modelagem
│   ├── modelagem.md               # Modelo de dados completo
│   └── diagramas/                 # Diagramas ER e de fluxo
│
├── sql/                           # Scripts SQL
│   ├── 01_create_tables.sql       # DDL — criação das tabelas
│   ├── 02_seed_data.sql           # Dados fictícios para testes
│   └── 03_audit_queries.sql       # Queries de auditoria e conciliação
│
├── data/                          # Dados gerados (CSV)
│   ├── raw/                       # Dados brutos simulados
│   └── processed/                 # Dados após limpeza
│
├── notebooks/                     # Jupyter Notebooks por fase
│   ├── 01_geracao_dados.ipynb
│   ├── 02_etl_pipeline.ipynb
│   ├── 03_regras_auditoria.ipynb
│   ├── 04_machine_learning.ipynb
│   └── 05_ia_generativa.ipynb
│
├── src/                           # Código-fonte Python
│   ├── gerador/                   # Geração de dados fictícios
│   ├── etl/                       # Pipeline ETL
│   ├── auditoria/                 # Motor de regras
│   ├── ml/                        # Modelos de Machine Learning
│   └── relatorio/                 # Geração de relatórios com IA
│
├── tests/                         # Testes unitários
│
├── docker-compose.yml             # MySQL + Streamlit em containers
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| 🐍 Python | Linguagem principal |
| 🐼 Pandas | Manipulação e análise de dados |
| 🗄️ MySQL | Banco de dados relacional |
| 🔄 ETL Pipeline | Ingestão, limpeza e transformação |
| 🤖 Scikit-learn | Detecção de anomalias (Isolation Forest) |
| 🧠 LLM / IA Generativa | Assistente inteligente para o contador |
| 📊 Streamlit | Dashboard interativo |
| 🐳 Docker | Containerização do ambiente |
| 📚 Git / GitHub | Controle de versão |

---

## 🗺️ Roadmap de Desenvolvimento

| Fase | Descrição | Status |
|---|---|---|
| 1 | Planejamento e modelagem do banco de dados | ✅ Concluído |
| 2 | DDL MySQL — criação das tabelas | ✅ Concluído |
| 3 | Geração de dados fictícios com Python + Faker | 🔄 Em andamento |
| 4 | Pipeline ETL (CSV → MySQL) | ⏳ Pendente |
| 5 | Motor de regras de auditoria e conciliação | ⏳ Pendente |
| 6 | Análise exploratória de dados | ⏳ Pendente |
| 7 | Machine Learning — detecção de anomalias | ⏳ Pendente |
| 8 | IA Generativa — relatório assistido por LLM | ⏳ Pendente |
| 9 | Dashboard Streamlit | ⏳ Pendente |
| 10 | Docker + documentação final | ⏳ Pendente |

---

## 🔎 Exemplos de Inconsistências Detectadas

### 🔴 Alta Prioridade
```
R$ 18.450 em entradas bancárias sem correspondência com receitas registradas.
→ Verificar extratos dos dias 05, 12 e 23 do mês.
```

### 🟠 Média Prioridade
```
Faturamento informado: R$ 82.000
Documentos encontrados: R$ 91.300
⚠️ Diferença: R$ 9.300 — revisar NF-e do período.
```

### 🟡 Baixa Prioridade
```
Despesa com combustível aumentou 74% em relação à média dos últimos 6 meses.
→ Solicitar comprovantes ao cliente.
```

---

## 🚀 Como Executar

```bash
# Clone o repositório
git clone https://github.com/ellen-xploit/fiscalaudit-ai.git
cd fiscalaudit-ai

# Instale as dependências
pip install -r requirements.txt

# Suba o banco de dados com Docker
docker-compose up -d

# Execute o DDL para criar as tabelas
mysql -u root -p fiscalaudit < sql/01_create_tables.sql
```

---

## 📄 Licença

MIT License — sinta-se livre para usar e adaptar.

---

*Desenvolvido como projeto de portfólio em Engenharia de Dados e Inteligência Artificial.*
