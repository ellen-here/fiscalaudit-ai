# 🧾 FiscalAudit AI

> Projeto de Engenharia de Dados e IA para conciliação e identificação de inconsistências em dados contábeis e financeiros.

## 🎯 Sobre o projeto

O FiscalAudit AI é um projeto de estudo e portfólio que estou desenvolvendo com foco em **Engenharia de Dados e Inteligência Artificial**, aplicado ao contexto contábil e financeiro.

A ideia surgiu a partir de um problema comum: empresas e escritórios de contabilidade trabalham com dados vindos de diferentes fontes e precisam conferir se essas informações estão corretas e se existe alguma inconsistência.

O projeto busca automatizar parte desse processo, organizando os dados, fazendo cruzamentos entre diferentes fontes e destacando situações que podem precisar de uma análise mais detalhada.

## 🔎 O que o projeto pretende analisar?

Entre os casos que quero identificar estão:

* Entradas e saídas que não correspondem aos registros financeiros;
* Diferenças entre movimentações bancárias e documentos fiscais;
* Notas fiscais duplicadas;
* Valores muito diferentes do histórico;
* Informações divergentes entre diferentes fontes;
* Movimentações que precisam ser revisadas antes do fechamento.

A ideia não é substituir a análise do contador, mas **facilitar o trabalho de revisão**, destacando os casos que merecem mais atenção.

---

## 🏗️ Arquitetura do projeto

O fluxo planejado atualmente é:

```text
        Dados dos clientes
               ↓
          Python / ETL
               ↓
      Limpeza e validação
               ↓
             MySQL
               ↓
       Regras de auditoria
               ↓
      Análise de dados / ML
               ↓
        Detecção de anomalias
               ↓
       IA Generativa / LLM
               ↓
       Relatório de análise
```

O projeto está sendo desenvolvido por etapas. Algumas partes ainda estão em construção e serão adicionadas conforme o desenvolvimento avançar.

---

## 📁 Estrutura do projeto

```text
fiscalaudit-ai/
│
├── docs/                          # Documentação e modelagem
│   ├── modelagem.md               # Modelo de dados
│   └── diagramas/                 # Diagramas ER e de fluxo
│
├── sql/                           # Scripts SQL
│   ├── 01_create_tables.sql       # Criação das tabelas
│   ├── 02_seed_data.sql           # Dados fictícios para testes
│   └── 03_audit_queries.sql       # Queries de auditoria
│
├── data/                          # Dados utilizados no projeto
│   ├── raw/                       # Dados brutos simulados
│   └── processed/                 # Dados após o tratamento
│
├── notebooks/                     # Notebooks de desenvolvimento
│   ├── 01_geracao_dados.ipynb
│   ├── 02_etl_pipeline.ipynb
│   ├── 03_regras_auditoria.ipynb
│   ├── 04_machine_learning.ipynb
│   └── 05_ia_generativa.ipynb
│
├── src/                           # Código-fonte Python
│   ├── gerador/                   # Geração de dados fictícios
│   ├── etl/                       # Pipeline ETL
│   ├── auditoria/                 # Regras de auditoria
│   ├── ml/                        # Machine Learning
│   └── relatorio/                 # Geração de relatórios
│
├── tests/                         # Testes
│
├── docker-compose.yml             # Configuração dos containers
├── requirements.txt               # Dependências Python
└── README.md
```

---

## 🛠️ Tecnologias

| Tecnologia             | Uso no projeto                    |
| ---------------------- | --------------------------------- |
| 🐍 Python              | Linguagem principal               |
| 🐼 Pandas              | Manipulação e análise dos dados   |
| 🗄️ MySQL              | Banco de dados relacional         |
| 🔄 ETL                 | Limpeza e transformação dos dados |
| 🤖 Scikit-learn        | Modelos de Machine Learning       |
| 🧠 LLM / IA Generativa | Análise e geração de relatórios   |
| 📊 Streamlit           | Dashboard                         |
| 🐳 Docker              | Ambiente de execução              |
| 📚 Git / GitHub        | Controle de versão                |

---

## 🗺️ Roadmap

| Fase | Descrição                                     | Status          |
| ---- | --------------------------------------------- | --------------- |
| 1    | Planejamento e modelagem do banco             | ✅ Concluído     |
| 2    | Criação das tabelas no MySQL                  | ✅ Concluído     |
| 3    | Geração de dados fictícios com Python + Faker | ✅ Concluído     |
| 4    | Pipeline ETL (CSV → MySQL)                    | ✅ Concluído     |
| 5    | Regras de auditoria e conciliação             | ✅ Concluído     |
| 6    | Análise exploratória dos dados                | ✅ Concluído     |
| 7    | Machine Learning para detecção de anomalias   | ✅ Concluído     |
| 8    | IA Generativa para apoio na análise           | ✅ Concluído     |
| 9    | Dashboard com Streamlit                       | ⏳ Pendente      |
| 10   | Docker e documentação final                   | ⏳ Pendente      |

---

## 🔎 Exemplos de inconsistências

Alguns exemplos de situações que o projeto pretende identificar:

### 🔴 Alta prioridade

```text
R$ 18.450 em entradas bancárias sem correspondência
com receitas registradas.

→ Verificar as movimentações do período.
```

### 🟠 Média prioridade

```text
Faturamento informado: R$ 82.000
Documentos encontrados: R$ 91.300

Diferença: R$ 9.300

→ Revisar os documentos fiscais do período.
```

### 🟡 Baixa prioridade

```text
Despesas com combustível aumentaram 74%
em relação à média dos últimos 6 meses.

→ Verificar os lançamentos e documentos relacionados.
```

> Os exemplos acima são fictícios e servem apenas para demonstrar o tipo de análise que o projeto pretende realizar.

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/ellen-xploit/fiscalaudit-ai.git
cd fiscalaudit-ai
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Suba o banco de dados

```bash
docker-compose up -d
```

### 4. Crie as tabelas

```bash
mysql -u root -p fiscalaudit < sql/01_create_tables.sql
```

> A forma de execução pode mudar conforme o ambiente e as próximas etapas do projeto.

---

## 🤝 Contribuições

O projeto ainda está em desenvolvimento, então **sugestões, ideias, melhorias e contribuições são muito bem-vindas**.

Se encontrar algum problema ou tiver alguma sugestão, fique à vontade para abrir uma *Issue* ou enviar um *Pull Request*.

---

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.

---

## 📌 Status

🚧 **Em desenvolvimento**

Este é um projeto de portfólio e estudo, desenvolvido por etapas. Novas funcionalidades serão adicionadas conforme o projeto evoluir.
