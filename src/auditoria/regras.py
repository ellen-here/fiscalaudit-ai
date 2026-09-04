"""
Motor de regras de auditoria do FiscalAudit AI
Identifica inconsistências nos dados contábeis e financeiros
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def conectar():
    host = os.getenv('DB_HOST', 'localhost')
    porta = os.getenv('DB_PORT', '3306')
    banco = os.getenv('DB_NAME', 'fiscalaudit')
    usuario = os.getenv('DB_USER', 'root')
    senha = os.getenv('DB_PASSWORD', '')

    url = f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}"
    return create_engine(url)


def divergencias_pagamento(engine):
    """Contas pagas onde o valor pago é diferente do valor original"""
    query = text("""
        SELECT 
            c.id_conta,
            e.razao_social AS empresa,
            c.tipo_titulo,
            c.valor_original,
            c.valor_pago,
            c.valor_original - c.valor_pago AS diferenca,
            c.data_vencimento,
            c.data_pagamento
        FROM contas_financeiras c
        JOIN empresas e ON c.id_empresa = e.id_empresa
        WHERE c.status_pagamento = 'Pago'
          AND c.valor_pago != c.valor_original
        ORDER BY ABS(c.valor_original - c.valor_pago) DESC
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df


def conciliacoes_inconsistentes(engine):
    """Conciliações marcadas como inconsistentes ou com diferença de valor"""
    query = text("""
        SELECT 
            conc.id_conciliacao,
            e.razao_social AS empresa,
            cf.tipo_titulo,
            cf.valor_pago AS valor_conta,
            mb.valor_movimentacao AS valor_banco,
            conc.diferenca_valor,
            conc.status_conciliacao,
            conc.data_conciliacao,
            conc.observacao
        FROM conciliacoes conc
        JOIN contas_financeiras cf ON conc.id_conta = cf.id_conta
        JOIN movimentacoes_bancarias mb ON conc.id_movimentacao = mb.id_movimentacao
        JOIN empresas e ON cf.id_empresa = e.id_empresa
        WHERE conc.status_conciliacao = 'Inconsistente'
           OR conc.diferenca_valor != 0
        ORDER BY ABS(conc.diferenca_valor) DESC
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df


def movimentacoes_sem_conciliacao(engine):
    """Movimentações bancárias que não foram conciliadas com nenhum título"""
    query = text("""
        SELECT 
            mb.id_movimentacao,
            e.razao_social AS empresa,
            mb.data_movimentacao,
            mb.tipo_operacao,
            mb.categoria,
            mb.valor_movimentacao,
            mb.descricao_movimentacao
        FROM movimentacoes_bancarias mb
        JOIN empresas e ON mb.id_empresa = e.id_empresa
        WHERE mb.conciliada = 0
        ORDER BY mb.valor_movimentacao DESC
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df


def documentos_problema(engine):
    """Documentos cancelados ou inutilizados que podem precisar de revisão"""
    query = text("""
        SELECT 
            d.id_documento,
            e.razao_social AS empresa,
            d.tipo_documento,
            d.numero_documento,
            d.data_emissao,
            d.tipo_operacao,
            d.valor,
            d.status_documento
        FROM documentos_fiscais d
        JOIN empresas e ON d.id_empresa = e.id_empresa
        WHERE d.status_documento IN ('Cancelada', 'Inutilizada')
        ORDER BY d.data_emissao DESC
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    
    return df


def salvar_relatorio(df, nome):
    if df.empty:
        return
    
    caminho = os.path.join(OUTPUT_DIR, f'{nome}.csv')
    df.to_csv(caminho, index=False, encoding='utf-8-sig')
    print(f"  → Salvo em {nome}.csv")


def main():
    print("\n" + "="*60)
    print("FiscalAudit AI — Motor de Regras de Auditoria")
    print("="*60 + "\n")
    
    engine = conectar()
    
    # 1. Divergências de pagamento
    print("1. Divergências em valores pagos:")
    df_div = divergencias_pagamento(engine)
    if not df_div.empty:
        print(f"   ⚠️  {len(df_div)} conta(s) com divergência encontrada(s)")
        salvar_relatorio(df_div, 'divergencias_pagamento')
    else:
        print("   ✓ Nenhuma divergência encontrada")
    print()
    
    # 2. Conciliações inconsistentes
    print("2. Conciliações inconsistentes:")
    df_conc = conciliacoes_inconsistentes(engine)
    if not df_conc.empty:
        print(f"   ⚠️  {len(df_conc)} conciliação(ões) inconsistente(s)")
        salvar_relatorio(df_conc, 'conciliacoes_inconsistentes')
    else:
        print("   ✓ Todas as conciliações estão consistentes")
    print()
    
    # 3. Movimentações sem conciliação
    print("3. Movimentações bancárias sem conciliação:")
    df_mov = movimentacoes_sem_conciliacao(engine)
    if not df_mov.empty:
        print(f"   ⚠️  {len(df_mov)} movimentação(ões) sem conciliação")
        total = df_mov['valor_movimentacao'].sum()
        print(f"   💰 Valor total: R$ {total:,.2f}")
        salvar_relatorio(df_mov, 'movimentacoes_sem_conciliacao')
    else:
        print("   ✓ Todas as movimentações estão conciliadas")
    print()
    
    # 4. Documentos com problema
    print("4. Documentos cancelados ou inutilizados:")
    df_doc = documentos_problema(engine)
    if not df_doc.empty:
        print(f"   ℹ️  {len(df_doc)} documento(s) para revisar")
        salvar_relatorio(df_doc, 'documentos_problema')
    else:
        print("   ✓ Nenhum documento cancelado/inutilizado")
    print()
    
    print("="*60)
    print("Auditoria concluída.")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
