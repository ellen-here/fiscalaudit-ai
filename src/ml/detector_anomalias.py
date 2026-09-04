"""
Detector de Anomalias usando Machine Learning
Usa Isolation Forest para encontrar padrões suspeitos nas contas financeiras
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def conectar():
    host = os.getenv('DB_HOST', 'localhost')
    porta = os.getenv('DB_PORT', '3306')
    banco = os.getenv('DB_NAME', 'fiscalaudit')
    usuario = os.getenv('DB_USER', 'root')
    senha = os.getenv('DB_PASSWORD', '')

    url = f"mysql+mysqlconnector://{usuario}:{senha}@{host}:{porta}/{banco}"
    return create_engine(url)


def extrair_dados(engine=None):
    """Busca contas financeiras com informações adicionais da empresa"""
    
    # tenta carregar do banco, se falhar usa os CSVs
    try:
        if engine:
            query = """
            SELECT 
                cf.id_conta,
                cf.id_empresa,
                e.razao_social,
                cf.tipo_titulo,
                cf.valor_original,
                cf.valor_pago,
                cf.data_vencimento,
                cf.data_pagamento,
                cf.status_pagamento,
                cf.descricao_pagamento
            FROM contas_financeiras cf
            JOIN empresas e ON cf.id_empresa = e.id_empresa
            WHERE cf.status_pagamento = 'Pago'
            """
            
            df = pd.read_sql(query, engine)
            return df
    except Exception as e:
        print(f"   (MySQL indisponível, usando CSVs)")
    
    # fallback: carrega dos CSVs
    contas = pd.read_csv(os.path.join(PROJECT_ROOT, 'data/raw/contas_financeiras.csv'), encoding='utf-8-sig')
    empresas = pd.read_csv(os.path.join(PROJECT_ROOT, 'data/raw/empresas.csv'), encoding='utf-8-sig')
    
    # join manual
    df = contas.merge(empresas[['id_empresa', 'razao_social']], on='id_empresa', how='left')
    
    # filtra só os pagos
    df = df[df['status_pagamento'] == 'Pago'].copy()
    
    return df


def criar_features(df):
    """Cria features para o modelo detectar anomalias"""
    
    # diferença entre valor original e pago
    df['diferenca_valor'] = df['valor_original'] - df['valor_pago']
    df['perc_diferenca'] = (df['diferenca_valor'] / df['valor_original'] * 100).fillna(0)
    
    # dias entre vencimento e pagamento
    df['data_vencimento'] = pd.to_datetime(df['data_vencimento'])
    df['data_pagamento'] = pd.to_datetime(df['data_pagamento'])
    df['dias_atraso'] = (df['data_pagamento'] - df['data_vencimento']).dt.days
    
    # estatísticas por empresa (para detectar comportamento atípico)
    df['valor_medio_empresa'] = df.groupby('id_empresa')['valor_original'].transform('mean')
    df['desvio_da_media'] = (df['valor_original'] - df['valor_medio_empresa']) / df['valor_medio_empresa'] * 100
    
    # tipo de título como binário (1 = A Receber, 0 = A Pagar)
    df['tipo_binario'] = (df['tipo_titulo'] == 'A Receber').astype(int)
    
    return df


def treinar_modelo(df):
    """Treina o Isolation Forest para detectar anomalias"""
    
    # features numéricas para o modelo
    features = [
        'valor_original',
        'diferenca_valor',
        'perc_diferenca',
        'dias_atraso',
        'desvio_da_media',
        'tipo_binario'
    ]
    
    X = df[features].fillna(0)
    
    # normaliza os dados (importante pro Isolation Forest)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # treina o modelo
    # contamination = percentual esperado de anomalias (começando com 10%)
    modelo = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    
    modelo.fit(X_scaled)
    
    # salva modelo e scaler
    joblib.dump(modelo, os.path.join(MODELS_DIR, 'isolation_forest.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    
    print(f"✓ Modelo treinado com {len(X)} registros")
    print(f"✓ Features utilizadas: {', '.join(features)}")
    
    return modelo, scaler, features


def detectar_anomalias(df, modelo, scaler, features):
    """Aplica o modelo e retorna as anomalias detectadas"""
    
    X = df[features].fillna(0)
    X_scaled = scaler.transform(X)
    
    # predição: -1 = anomalia, 1 = normal
    df['predicao'] = modelo.predict(X_scaled)
    
    # score de anomalia (quanto mais negativo, mais anômalo)
    df['score_anomalia'] = modelo.decision_function(X_scaled)
    
    # filtra só as anomalias
    anomalias = df[df['predicao'] == -1].copy()
    anomalias = anomalias.sort_values('score_anomalia')
    
    return anomalias


def gerar_relatorio(anomalias):
    """Gera relatório das anomalias detectadas"""
    
    if anomalias.empty:
        print("\n✓ Nenhuma anomalia detectada\n")
        return
    
    # seleciona colunas relevantes pro relatório
    colunas = [
        'id_conta',
        'razao_social',
        'tipo_titulo',
        'valor_original',
        'valor_pago',
        'diferenca_valor',
        'perc_diferenca',
        'dias_atraso',
        'score_anomalia'
    ]
    
    relatorio = anomalias[colunas].copy()
    
    # salva CSV
    caminho = os.path.join(OUTPUT_DIR, 'anomalias_ml.csv')
    relatorio.to_csv(caminho, index=False, encoding='utf-8-sig')
    
    return relatorio


def main():
    print("\n" + "="*60)
    print("FiscalAudit AI — Detector de Anomalias (ML)")
    print("="*60 + "\n")
    
    # tenta conectar, mas se falhar não é problema
    try:
        engine = conectar()
    except:
        engine = None
    
    print("1. Extraindo dados...")
    df = extrair_dados(engine)
    print(f"   ✓ {len(df)} contas pagas carregadas")
    
    print("\n2. Criando features...")
    df = criar_features(df)
    print(f"   ✓ Features criadas")
    
    print("\n3. Treinando modelo Isolation Forest...")
    modelo, scaler, features = treinar_modelo(df)
    
    print("\n4. Detectando anomalias...")
    anomalias = detectar_anomalias(df, modelo, scaler, features)
    print(f"   ⚠️  {len(anomalias)} anomalias detectadas ({len(anomalias)/len(df)*100:.1f}% do total)")
    
    print("\n5. Gerando relatório...")
    relatorio = gerar_relatorio(anomalias)
    print(f"   ✓ Relatório salvo em anomalias_ml.csv")
    
    # mostra top 5 anomalias mais suspeitas
    if not anomalias.empty:
        print("\n" + "="*60)
        print("Top 5 Anomalias Mais Suspeitas:")
        print("="*60)
        
        top5 = relatorio.head(5)
        for idx, row in top5.iterrows():
            print(f"\n• Conta #{row['id_conta']} — {row['razao_social']}")
            print(f"  Tipo: {row['tipo_titulo']}")
            print(f"  Valor: R$ {row['valor_original']:,.2f} → Pago: R$ {row['valor_pago']:,.2f}")
            print(f"  Diferença: R$ {row['diferenca_valor']:,.2f} ({row['perc_diferenca']:.1f}%)")
            print(f"  Atraso: {row['dias_atraso']:.0f} dias")
            print(f"  Score de anomalia: {row['score_anomalia']:.3f}")
    
    print("\n" + "="*60)
    print("Detecção concluída.")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
