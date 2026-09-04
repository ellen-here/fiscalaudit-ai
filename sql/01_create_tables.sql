-- FiscalAudit AI — DDL MySQL
-- Ordem de criação respeita as dependências de chaves estrangeiras

CREATE DATABASE IF NOT EXISTS fiscalaudit
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fiscalaudit;

-- Tabelas sem dependências (criadas primeiro)

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
) ENGINE=InnoDB;


CREATE TABLE fornecedores (
    id_fornecedor           INT             NOT NULL AUTO_INCREMENT,
    cnpj                    VARCHAR(18)     NOT NULL,
    razao_social            VARCHAR(150)    NOT NULL,
    categoria_fornecimento  VARCHAR(100)    NULL,
    criado_em               DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_fornecedores      PRIMARY KEY (id_fornecedor),
    CONSTRAINT uq_fornecedores_cnpj UNIQUE      (cnpj),

    INDEX idx_fornecedores_razao_social (razao_social)
) ENGINE=InnoDB;


-- Tabela central do modelo

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
                        )               NULL,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_empresas      PRIMARY KEY (id_empresa),
    CONSTRAINT uq_empresas_cnpj UNIQUE      (cnpj),

    INDEX idx_empresas_razao_social   (razao_social),
    INDEX idx_empresas_regime         (regime_tributario)
) ENGINE=InnoDB;


-- Tabelas dependentes

CREATE TABLE movimentacoes_bancarias (
    id_movimentacao         INT             NOT NULL AUTO_INCREMENT,
    id_empresa              INT             NOT NULL,
    data_movimentacao       DATE            NOT NULL,
    tipo_operacao           ENUM(
                                'Entrada',
                                'Saída'
                            )               NOT NULL,
    categoria               VARCHAR(100)    NULL,
    descricao_movimentacao  VARCHAR(255)    NULL,
    valor_movimentacao      DECIMAL(15, 2)  NOT NULL,
    conciliada              TINYINT(1)      NOT NULL DEFAULT 0,

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
) ENGINE=InnoDB;


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
    chave_acesso        VARCHAR(44)     NULL,
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
) ENGINE=InnoDB;


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
) ENGINE=InnoDB;


-- Relação 1:1 no MVP (UNIQUE em ambas as FKs)

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
    observacao          VARCHAR(500)    NULL,

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
) ENGINE=InnoDB;
