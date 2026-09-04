-- =============================================================
--  FiscalAudit AI — DDL MySQL
--  Fase 2: Criação das Tabelas
--  Ordem respeitando dependências de chaves estrangeiras (FK)
-- =============================================================

CREATE DATABASE IF NOT EXISTS fiscalaudit
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fiscalaudit;

-- =============================================================
-- 1. CLIENTES
--    Pessoas físicas ou jurídicas que compram das empresas.
--    Criada primeiro pois não possui FK.
-- =============================================================
CREATE TABLE clientes (
    id_cliente          INT             NOT NULL AUTO_INCREMENT,
    cnpj_cpf            VARCHAR(18)     NOT NULL,
    nome_cliente        VARCHAR(150)    NOT NULL,
    email               VARCHAR(150)    NULL,
    telefone            VARCHAR(20)     NULL,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_clientes          PRIMARY KEY (id_cliente),
    CONSTRAINT uq_clientes_cnpj_cpf UNIQUE      (cnpj_cpf),

    INDEX idx_clientes_nome (nome_cliente)
) ENGINE=InnoDB
  COMMENT='Clientes das empresas auditadas.';


-- =============================================================
-- 2. FORNECEDORES
--    Empresas que fornecem bens/serviços às empresas auditadas.
--    Criada antes de documentos_fiscais e contas_financeiras.
-- =============================================================
CREATE TABLE fornecedores (
    id_fornecedor           INT             NOT NULL AUTO_INCREMENT,
    cnpj                    VARCHAR(18)     NOT NULL,
    razao_social            VARCHAR(150)    NOT NULL,
    categoria_fornecimento  VARCHAR(100)    NULL COMMENT 'Ex: Tecnologia, Transporte, Insumos',
    criado_em               DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_fornecedores      PRIMARY KEY (id_fornecedor),
    CONSTRAINT uq_fornecedores_cnpj UNIQUE      (cnpj),

    INDEX idx_fornecedores_razao_social (razao_social)
) ENGINE=InnoDB
  COMMENT='Fornecedores das empresas auditadas.';


-- =============================================================
-- 3. EMPRESAS
--    Tabela central. Representa os clientes do escritório
--    (as empresas cujos dados financeiros serão auditados).
--    Criada antes das tabelas que a referenciam via FK.
-- =============================================================
CREATE TABLE empresas (
    id_empresa          INT             NOT NULL AUTO_INCREMENT,
    razao_social        VARCHAR(150)    NOT NULL,
    cnpj                VARCHAR(18)     NOT NULL,
    ramo_atividade      VARCHAR(100)    NULL,
    regime_tributario   ENUM(
                            'Simples Nacional',
                            'Lucro Presumido',
                            'Lucro Real',
                            'MEI'
                        )               NULL COMMENT 'Regime de tributação da empresa',
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_empresas      PRIMARY KEY (id_empresa),
    CONSTRAINT uq_empresas_cnpj UNIQUE      (cnpj),

    INDEX idx_empresas_razao_social   (razao_social),
    INDEX idx_empresas_regime         (regime_tributario)
) ENGINE=InnoDB
  COMMENT='Empresas clientes do escritório contábil (objeto da auditoria).';


-- =============================================================
-- 4. MOVIMENTACOES_BANCARIAS
--    Registra entradas e saídas do extrato bancário.
--    FK → empresas
-- =============================================================
CREATE TABLE movimentacoes_bancarias (
    id_movimentacao         INT             NOT NULL AUTO_INCREMENT,
    id_empresa              INT             NOT NULL,
    data_movimentacao       DATE            NOT NULL,
    tipo_operacao           ENUM(
                                'Entrada',
                                'Saída'
                            )               NOT NULL,
    categoria               VARCHAR(100)    NULL COMMENT 'Ex: Salário, Fornecedor, Receita de Venda',
    descricao_movimentacao  VARCHAR(255)    NULL,
    valor_movimentacao      DECIMAL(15, 2)  NOT NULL,
    conciliada              TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '0 = Não conciliada, 1 = Conciliada',

    CONSTRAINT pk_movimentacoes         PRIMARY KEY (id_movimentacao),
    CONSTRAINT fk_movimentacoes_empresa FOREIGN KEY (id_empresa)
        REFERENCES empresas (id_empresa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_mov_empresa          (id_empresa),
    INDEX idx_mov_data             (data_movimentacao),
    INDEX idx_mov_tipo             (tipo_operacao),
    INDEX idx_mov_conciliada       (conciliada),
    INDEX idx_mov_empresa_data     (id_empresa, data_movimentacao)
) ENGINE=InnoDB
  COMMENT='Extrato bancário das empresas auditadas.';


-- =============================================================
-- 5. DOCUMENTOS_FISCAIS
--    Notas fiscais (NF-e, NFS-e, CT-e etc.).
--    FK → empresas, clientes (NULL), fornecedores (NULL)
--    Um documento pertence a cliente (saída) OU fornecedor
--    (entrada), dependendo do tipo de operação.
-- =============================================================
CREATE TABLE documentos_fiscais (
    id_documento        INT             NOT NULL AUTO_INCREMENT,
    id_empresa          INT             NOT NULL,
    id_cliente          INT             NULL COMMENT 'Preenchido quando tipo_operacao = Saída',
    id_fornecedor       INT             NULL COMMENT 'Preenchido quando tipo_operacao = Entrada',
    tipo_documento      ENUM(
                            'NF-e',
                            'NFS-e',
                            'CT-e',
                            'NFC-e',
                            'Outros'
                        )               NOT NULL,
    numero_documento    VARCHAR(50)     NOT NULL,
    serie_documento     VARCHAR(10)     NULL,
    chave_acesso        VARCHAR(44)     NULL COMMENT 'Chave de acesso de 44 dígitos da NF-e',
    data_emissao        DATE            NOT NULL,
    tipo_operacao       ENUM(
                            'Entrada',
                            'Saída'
                        )               NOT NULL,
    valor               DECIMAL(15, 2)  NOT NULL,
    status_documento    ENUM(
                            'Ativa',
                            'Cancelada',
                            'Inutilizada'
                        )               NOT NULL DEFAULT 'Ativa',

    CONSTRAINT pk_documentos                PRIMARY KEY (id_documento),
    CONSTRAINT uq_documentos_chave_acesso   UNIQUE      (chave_acesso),
    CONSTRAINT fk_documentos_empresa        FOREIGN KEY (id_empresa)
        REFERENCES empresas (id_empresa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_documentos_cliente        FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_documentos_fornecedor     FOREIGN KEY (id_fornecedor)
        REFERENCES fornecedores (id_fornecedor)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    INDEX idx_doc_empresa           (id_empresa),
    INDEX idx_doc_cliente           (id_cliente),
    INDEX idx_doc_fornecedor        (id_fornecedor),
    INDEX idx_doc_data_emissao      (data_emissao),
    INDEX idx_doc_tipo_operacao     (tipo_operacao),
    INDEX idx_doc_status            (status_documento),
    INDEX idx_doc_numero_serie      (numero_documento, serie_documento),
    INDEX idx_doc_empresa_data      (id_empresa, data_emissao)
) ENGINE=InnoDB
  COMMENT='Documentos fiscais (NF-e, NFS-e, CT-e) das empresas auditadas.';


-- =============================================================
-- 6. CONTAS_FINANCEIRAS
--    Títulos a pagar e a receber.
--    FK → empresas, clientes (NULL), fornecedores (NULL)
-- =============================================================
CREATE TABLE contas_financeiras (
    id_conta            INT             NOT NULL AUTO_INCREMENT,
    id_empresa          INT             NOT NULL,
    id_cliente          INT             NULL COMMENT 'Preenchido quando tipo_titulo = A Receber',
    id_fornecedor       INT             NULL COMMENT 'Preenchido quando tipo_titulo = A Pagar',
    tipo_titulo         ENUM(
                            'A Pagar',
                            'A Receber'
                        )               NOT NULL,
    valor_original      DECIMAL(15, 2)  NOT NULL,
    valor_pago          DECIMAL(15, 2)  NOT NULL DEFAULT 0.00,
    data_vencimento     DATE            NOT NULL,
    data_pagamento      DATE            NULL,
    status_pagamento    ENUM(
                            'Pendente',
                            'Pago',
                            'Vencido',
                            'Cancelado'
                        )               NOT NULL DEFAULT 'Pendente',
    descricao_pagamento VARCHAR(255)    NULL,

    CONSTRAINT pk_contas                    PRIMARY KEY (id_conta),
    CONSTRAINT fk_contas_empresa            FOREIGN KEY (id_empresa)
        REFERENCES empresas (id_empresa)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_contas_cliente            FOREIGN KEY (id_cliente)
        REFERENCES clientes (id_cliente)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_contas_fornecedor         FOREIGN KEY (id_fornecedor)
        REFERENCES fornecedores (id_fornecedor)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    INDEX idx_contas_empresa            (id_empresa),
    INDEX idx_contas_cliente            (id_cliente),
    INDEX idx_contas_fornecedor         (id_fornecedor),
    INDEX idx_contas_tipo               (tipo_titulo),
    INDEX idx_contas_status             (status_pagamento),
    INDEX idx_contas_vencimento         (data_vencimento),
    INDEX idx_contas_empresa_status     (id_empresa, status_pagamento),
    INDEX idx_contas_empresa_vencimento (id_empresa, data_vencimento)
) ENGINE=InnoDB
  COMMENT='Títulos a pagar e a receber das empresas auditadas.';


-- =============================================================
-- 7. CONCILIACOES
--    Relaciona uma conta financeira a uma movimentação bancária.
--    Relação 1:1 para o MVP (UNIQUE em ambas as FKs).
--    Criada por último pois depende das duas tabelas acima.
-- =============================================================
CREATE TABLE conciliacoes (
    id_conciliacao      INT             NOT NULL AUTO_INCREMENT,
    id_conta            INT             NOT NULL,
    id_movimentacao     INT             NOT NULL,
    data_conciliacao    DATE            NOT NULL,
    status_conciliacao  ENUM(
                            'Conciliado',
                            'Pendente',
                            'Inconsistente'
                        )               NOT NULL DEFAULT 'Pendente',
    diferenca_valor     DECIMAL(15, 2)  NOT NULL DEFAULT 0.00
                        COMMENT 'Diferença entre valor da conta e valor da movimentação',
    observacao          VARCHAR(500)    NULL COMMENT 'Notas do auditor ou do sistema',

    CONSTRAINT pk_conciliacoes              PRIMARY KEY (id_conciliacao),
    CONSTRAINT uq_conciliacoes_conta        UNIQUE      (id_conta),
    CONSTRAINT uq_conciliacoes_movimentacao UNIQUE      (id_movimentacao),
    CONSTRAINT fk_conciliacoes_conta        FOREIGN KEY (id_conta)
        REFERENCES contas_financeiras (id_conta)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_conciliacoes_movimentacao FOREIGN KEY (id_movimentacao)
        REFERENCES movimentacoes_bancarias (id_movimentacao)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_conc_status           (status_conciliacao),
    INDEX idx_conc_data             (data_conciliacao),
    INDEX idx_conc_diferenca        (diferenca_valor)
) ENGINE=InnoDB
  COMMENT='Conciliação entre títulos financeiros e movimentações bancárias (relação 1:1 no MVP).';


-- =============================================================
--  FIM DO DDL
--  Próximo passo: 02_seed_data.sql (dados fictícios para teste)
-- =============================================================
