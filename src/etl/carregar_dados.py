"""
Pipeline ETL do FiscalAudit AI
Lê os CSVs de data/raw, faz uma limpeza básica e carrega no MySQL
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Ordem de carga respeitando as chaves estrangeiras
# (as tabelas sem dependência vêm primeiro)
TABELAS = [
    'clientes',
    'fornecedores',
    'empresas',
    'movimentacoes_bancarias',
    'documentos_fiscais',
    'contas_financeiras',
    'conciliacoes',
]

# Colunas de FK opcionais que podem vir vazias no CSV
COLUNAS_FK_OPCIONAIS = ['id_cliente', 'id_fornecedor']


def conectar():
    host = os.getenv('DB_HOST', 'localhost')
    porta = os.getenv('DB_PORT', '3306')
    banco = os.getenv('DB_NAME', 'fiscalaudit')
    usuario = os.getenv('DB_USER', 'root')
    senha = os.getenv('DB_PASSWORD', '')

    url = f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}"
    return create_engine(url)


def limpar(df):
    """Tira espaços sobrando e troca strings vazias por nulo"""
    for coluna in df.select_dtypes(include='object').columns:
        df[coluna] = df[coluna].str.strip()
        df[coluna] = df[coluna].replace('', None)

    # FKs opcionais precisam ir como inteiro nulo, não como texto vazio
    for coluna in COLUNAS_FK_OPCIONAIS:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors='coerce').astype('Int64')

    return df


def separar_chaves_duplicadas(df):
    """
    Nos documentos fiscais existem chaves de acesso repetidas (notas duplicadas).
    A tabela tem UNIQUE na chave_acesso, então guardo a primeira ocorrência e
    mando as repetidas para um arquivo à parte, para conferir depois.
    """
    duplicadas = df[df.duplicated(subset='chave_acesso', keep='first') & df['chave_acesso'].notna()]

    if not duplicadas.empty:
        caminho = os.path.join(PROCESSED_DIR, 'documentos_duplicados.csv')
        duplicadas.to_csv(caminho, index=False, encoding='utf-8-sig')
        print(f"  {len(duplicadas)} documento(s) com chave duplicada separados em documentos_duplicados.csv")

    return df.drop(duplicadas.index)


def carregar_tabela(engine, tabela):
    caminho = os.path.join(RAW_DIR, f'{tabela}.csv')
    df = pd.read_csv(caminho, encoding='utf-8-sig')
    df = limpar(df)

    if tabela == 'documentos_fiscais':
        df = separar_chaves_duplicadas(df)

    df.to_sql(tabela, con=engine, if_exists='append', index=False)
    print(f"✓ {tabela}: {len(df)} registros carregados")
    return len(df)


def limpar_tabelas(engine):
    """Esvazia as tabelas antes de carregar, para poder rodar o script mais de uma vez"""
    with engine.begin() as conn:
        conn.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        # apaga na ordem inversa da carga
        for tabela in reversed(TABELAS):
            conn.execute(text(f'TRUNCATE TABLE {tabela}'))
        conn.execute(text('SET FOREIGN_KEY_CHECKS = 1'))


def main():
    print("\nCarregando dados no MySQL...\n")
    engine = conectar()

    limpar_tabelas(engine)

    total = 0
    for tabela in TABELAS:
        total += carregar_tabela(engine, tabela)

    print(f"\nConcluído. {total} registros no total.\n")


if __name__ == '__main__':
    main()
