# 🏗️ Modelagem do Banco de Dados — FiscalAudit AI

### Fase 1 — Planejamento e Modelagem Relacional

Antes de começar a implementação do FiscalAudit AI, defini a estrutura do banco de dados e os relacionamentos entre as entidades.

A ideia nesta primeira etapa foi criar uma base organizada para armazenar informações financeiras, fiscais e bancárias, deixando o modelo preparado para as próximas etapas do projeto.

## 🎯 Decisões de Design

Algumas decisões tomadas durante a modelagem:

* **DECIMAL para valores monetários:** escolhi `DECIMAL(15,2)` para armazenar valores financeiros, evitando problemas de precisão que podem acontecer com tipos como `FLOAT` e `DOUBLE`.

* **ENUM para alguns campos de classificação:** utilizei `ENUM` em campos com opções mais limitadas, como status, tipo de operação e regime tributário. Para o MVP, isso mantém a estrutura mais simples.

* **Relacionamento 1:1 nas conciliações:** nesta primeira versão, uma conta financeira pode ser relacionada a apenas uma movimentação bancária, e uma movimentação pode participar de apenas uma conciliação. Essa escolha simplifica a implementação do MVP.

* **Chaves estrangeiras opcionais:** em `documentos_fiscais` e `contas_financeiras`, `id_cliente` e `id_fornecedor` podem ser `NULL`, já que uma operação pode envolver um cliente ou um fornecedor, dependendo do tipo de lançamento.

## 📐 Normalização

A estrutura foi pensada seguindo os princípios de normalização até a **Terceira Forma Normal (3FN)**.

Durante a modelagem, procurei evitar a repetição desnecessária de informações e separar os dados de acordo com sua responsabilidade.

Por exemplo, os dados de clientes, fornecedores e empresas ficam em suas próprias tabelas, enquanto documentos fiscais, contas financeiras e movimentações bancárias armazenam apenas as informações relacionadas a cada entidade.

De forma resumida:

* **1FN:** os campos armazenam valores atômicos, sem listas ou conjuntos de valores dentro de uma mesma coluna.
* **2FN:** os atributos dependem da chave da própria entidade.
* **3FN:** procurei evitar dependências entre atributos que não fazem parte da chave, mantendo cada informação no lugar mais adequado.

A normalização também facilita futuras alterações no sistema e reduz a possibilidade de inconsistências nos dados.

## 📋 Tabelas e Relacionamentos

### 1. clientes

Representa os clientes das empresas atendidas pelo escritório.

| Campo        | Tipo         | Restrição          | Descrição            |
| ------------ | ------------ | ------------------ | -------------------- |
| id_cliente   | INT          | PK, AUTO_INCREMENT | Identificador único  |
| cnpj_cpf     | VARCHAR(18)  | UNIQUE, NOT NULL   | CPF ou CNPJ          |
| nome_cliente | VARCHAR(150) | NOT NULL           | Nome ou Razão Social |
| email        | VARCHAR(150) | —                  | Contato              |
| telefone     | VARCHAR(20)  | —                  | Telefone             |
| criado_em    | DATETIME     | DEFAULT NOW()      | Data de cadastro     |

### 2. fornecedores

Armazena as empresas que fornecem produtos ou serviços.

| Campo                  | Tipo         | Restrição          | Descrição                           |
| ---------------------- | ------------ | ------------------ | ----------------------------------- |
| id_fornecedor          | INT          | PK, AUTO_INCREMENT | Identificador único                 |
| cnpj                   | VARCHAR(18)  | UNIQUE, NOT NULL   | CNPJ do fornecedor                  |
| razao_social           | VARCHAR(150) | NOT NULL           | Nome da empresa                     |
| categoria_fornecimento | VARCHAR(100) | —                  | Ex: Tecnologia, Transporte, Insumos |
| criado_em              | DATETIME     | DEFAULT NOW()      | Data de cadastro                    |

### 3. empresas

É a tabela central do modelo. Representa as empresas cujos dados serão analisados pelo sistema.

| Campo             | Tipo         | Restrição          | Descrição                              |
| ----------------- | ------------ | ------------------ | -------------------------------------- |
| id_empresa        | INT          | PK, AUTO_INCREMENT | Identificador único                    |
| razao_social      | VARCHAR(150) | NOT NULL           | Razão social                           |
| cnpj              | VARCHAR(18)  | UNIQUE, NOT NULL   | CNPJ da empresa                        |
| ramo_atividade    | VARCHAR(100) | —                  | Setor de atuação                       |
| regime_tributario | ENUM         | —                  | Simples / Lucro Presumido / Lucro Real |
| criado_em         | DATETIME     | DEFAULT NOW()      | Data de cadastro                       |

Uma empresa pode possuir várias movimentações bancárias, documentos fiscais e contas financeiras.

### 4. movimentacoes_bancarias

Registra as entradas e saídas identificadas nas contas bancárias da empresa.

| Campo                  | Tipo          | Restrição          | Descrição                        |
| ---------------------- | ------------- | ------------------ | -------------------------------- |
| id_movimentacao        | INT           | PK, AUTO_INCREMENT | Identificador único              |
| id_empresa             | INT           | FK → empresas      | Empresa relacionada              |
| data_movimentacao      | DATE          | NOT NULL           | Data da movimentação             |
| tipo_operacao          | ENUM          | NOT NULL           | Entrada / Saída                  |
| categoria              | VARCHAR(100)  | —                  | Ex: Salário, Fornecedor, Receita |
| descricao_movimentacao | VARCHAR(255)  | —                  | Descrição do extrato             |
| valor_movimentacao     | DECIMAL(15,2) | NOT NULL           | Valor da movimentação            |
| conciliada             | TINYINT(1)    | DEFAULT 0          | Indica se já foi conciliada      |

### 5. documentos_fiscais

Armazena documentos fiscais, como NF-e, NFS-e e CT-e.

| Campo            | Tipo          | Restrição               | Descrição                       |
| ---------------- | ------------- | ----------------------- | ------------------------------- |
| id_documento     | INT           | PK, AUTO_INCREMENT      | Identificador único             |
| id_empresa       | INT           | FK → empresas           | Empresa relacionada             |
| id_cliente       | INT           | FK → clientes, NULL     | Cliente, quando aplicável       |
| id_fornecedor    | INT           | FK → fornecedores, NULL | Fornecedor, quando aplicável    |
| tipo_documento   | ENUM          | NOT NULL                | NF-e, NFS-e, CT-e, Outros       |
| numero_documento | VARCHAR(50)   | NOT NULL                | Número do documento             |
| serie_documento  | VARCHAR(10)   | —                       | Série                           |
| chave_acesso     | VARCHAR(44)   | UNIQUE                  | Chave de acesso                 |
| data_emissao     | DATE          | NOT NULL                | Data de emissão                 |
| tipo_operacao    | ENUM          | NOT NULL                | Entrada / Saída                 |
| valor            | DECIMAL(15,2) | NOT NULL                | Valor total                     |
| status_documento | ENUM          | DEFAULT 'Ativa'         | Ativa / Cancelada / Inutilizada |

### 6. contas_financeiras

Representa títulos financeiros a pagar ou a receber.

| Campo               | Tipo          | Restrição               | Descrição                             |
| ------------------- | ------------- | ----------------------- | ------------------------------------- |
| id_conta            | INT           | PK, AUTO_INCREMENT      | Identificador único                   |
| id_empresa          | INT           | FK → empresas           | Empresa relacionada                   |
| id_cliente          | INT           | FK → clientes, NULL     | Cliente, quando for a receber         |
| id_fornecedor       | INT           | FK → fornecedores, NULL | Fornecedor, quando for a pagar        |
| tipo_titulo         | ENUM          | NOT NULL                | A Pagar / A Receber                   |
| valor_original      | DECIMAL(15,2) | NOT NULL                | Valor original                        |
| valor_pago          | DECIMAL(15,2) | DEFAULT 0               | Valor pago                            |
| data_vencimento     | DATE          | NOT NULL                | Data de vencimento                    |
| data_pagamento      | DATE          | NULL                    | Data do pagamento                     |
| status_pagamento    | ENUM          | NOT NULL                | Pago / Pendente / Vencido / Cancelado |
| descricao_pagamento | VARCHAR(255)  | —                       | Descrição do título                   |

**Regra de negócio:** títulos a pagar são normalmente relacionados a fornecedores, enquanto títulos a receber são normalmente relacionados a clientes.

### 7. conciliacoes

Relaciona uma conta financeira com uma movimentação bancária para verificar se o valor registrado no sistema corresponde ao que realmente entrou ou saiu do banco.

| Campo              | Tipo          | Restrição                            | Descrição                             |
| ------------------ | ------------- | ------------------------------------ | ------------------------------------- |
| id_conciliacao     | INT           | PK, AUTO_INCREMENT                   | Identificador único                   |
| id_conta           | INT           | FK → contas_financeiras, UNIQUE      | Conta conciliada                      |
| id_movimentacao    | INT           | FK → movimentacoes_bancarias, UNIQUE | Movimentação conciliada               |
| data_conciliacao   | DATE          | NOT NULL                             | Data da conciliação                   |
| status_conciliacao | ENUM          | NOT NULL                             | Conciliado / Pendente / Inconsistente |
| diferenca_valor    | DECIMAL(15,2) | DEFAULT 0                            | Diferença encontrada                  |
| observacao         | VARCHAR(500)  | —                                    | Observações do auditor ou sistema     |

No MVP, a relação foi definida como **1:1**. Assim, uma conta financeira e uma movimentação bancária podem participar de apenas uma conciliação.

## 🔗 Diagrama de Relacionamentos

```text
                         ┌─────────────────┐
                         │    EMPRESAS     │
                         │ PK id_empresa   │
                         └────────┬────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
 MOVIMENTAÇÕES             DOCUMENTOS FISCAIS      CONTAS FINANCEIRAS
 PK id_movimentacao        PK id_documento        PK id_conta
 FK id_empresa             FK id_empresa           FK id_empresa
                           FK id_cliente            FK id_cliente
                           FK id_fornecedor         FK id_fornecedor
                                   │                       │
                                   │                       │
                         ┌─────────┴─────────┐             │
                         ▼                   ▼             │
                    CLIENTES          FORNECEDORES         │
                    PK id_cliente     PK id_fornecedor    │
                                                          │
                                  ┌────────────────────────┘
                                  ▼
                            CONCILIAÇÕES
                            PK id_conciliacao
                            FK id_conta
                            FK id_movimentacao
```

## 📐 Ordem de Criação das Tabelas

A ordem de criação considera as dependências entre as chaves estrangeiras:

1. `clientes`
2. `fornecedores`
3. `empresas`
4. `movimentacoes_bancarias`
5. `documentos_fiscais`
6. `contas_financeiras`
7. `conciliacoes`

Dessa forma, quando uma tabela é criada com uma chave estrangeira, a tabela que ela referencia já existe no banco.

## 🚀 Próximas Etapas

Com a modelagem definida, as próximas etapas do projeto serão a implementação do banco de dados, criação das consultas e desenvolvimento da lógica responsável pelas análises e auditorias.
