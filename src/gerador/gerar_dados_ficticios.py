"""
Gerador de dados fictícios para o FiscalAudit AI
Cria dados de teste para as 7 tabelas do banco, incluindo inconsistências propositais
"""

import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker('pt_BR')
random.seed(42)
Faker.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def gerar_cnpj():
    """Gera um CNPJ fictício formatado"""
    return f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/0001-{random.randint(10, 99)}"


def gerar_cpf():
    """Gera um CPF fictício formatado"""
    return f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"


def gerar_cnpj_ou_cpf():
    """Retorna CNPJ ou CPF aleatoriamente"""
    return gerar_cnpj() if random.random() > 0.3 else gerar_cpf()


def gerar_chave_nfe():
    """Gera uma chave de acesso de NF-e (44 dígitos)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(44)])


# Clientes
def gerar_clientes(n=50):
    print(f"Gerando {n} clientes...")
    
    clientes = []
    for i in range(1, n + 1):
        cliente = {
            'id_cliente': i,
            'cnpj_cpf': gerar_cnpj_ou_cpf(),
            'nome_cliente': fake.company() if random.random() > 0.4 else fake.name(),
            'email': fake.email(),
            'telefone': fake.phone_number(),
            'criado_em': fake.date_time_between(start_date='-2y', end_date='now')
        }
        clientes.append(cliente)
    
    return pd.DataFrame(clientes)


# Fornecedores
def gerar_fornecedores(n=40):
    print(f"Gerando {n} fornecedores...")
    
    categorias = [
        'Tecnologia', 'Transporte', 'Insumos', 'Serviços',
        'Alimentos', 'Construção', 'Marketing', 'Consultoria'
    ]
    
    fornecedores = []
    for i in range(1, n + 1):
        fornecedor = {
            'id_fornecedor': i,
            'cnpj': gerar_cnpj(),
            'razao_social': fake.company(),
            'categoria_fornecimento': random.choice(categorias),
            'criado_em': fake.date_time_between(start_date='-2y', end_date='now')
        }
        fornecedores.append(fornecedor)
    
    return pd.DataFrame(fornecedores)


# Empresas
def gerar_empresas(n=10):
    print(f"Gerando {n} empresas...")
    
    ramos = [
        'Comércio', 'Serviços', 'Indústria', 'Tecnologia',
        'Alimentação', 'Saúde', 'Educação', 'Construção'
    ]
    
    regimes = [
        'Simples Nacional', 'Lucro Presumido', 'Lucro Real', 'MEI'
    ]
    
    empresas = []
    for i in range(1, n + 1):
        empresa = {
            'id_empresa': i,
            'razao_social': fake.company(),
            'cnpj': gerar_cnpj(),
            'ramo_atividade': random.choice(ramos),
            'regime_tributario': random.choice(regimes),
            'criado_em': fake.date_time_between(start_date='-3y', end_date='-1y')
        }
        empresas.append(empresa)
    
    return pd.DataFrame(empresas)


# Movimentações bancárias
def gerar_movimentacoes_bancarias(empresas_df, n_por_empresa=50):
    print(f"Gerando ~{n_por_empresa} movimentações por empresa...")
    
    categorias_entrada = [
        'Receita de Venda', 'Recebimento de Cliente', 'Empréstimo',
        'Aporte de Capital', 'Recebimento de Serviços'
    ]
    
    categorias_saida = [
        'Pagamento de Fornecedor', 'Salário', 'Aluguel', 'Impostos',
        'Combustível', 'Manutenção', 'Marketing', 'Despesas Administrativas'
    ]
    
    movimentacoes = []
    id_mov = 1
    
    for _, empresa in empresas_df.iterrows():
        data_inicio = datetime.now() - timedelta(days=365)
        data_fim = datetime.now()
        
        for _ in range(n_por_empresa):
            tipo = random.choice(['Entrada', 'Saída'])
            
            if tipo == 'Entrada':
                categoria = random.choice(categorias_entrada)
                valor = round(random.uniform(500, 50000), 2)
            else:
                categoria = random.choice(categorias_saida)
                valor = round(random.uniform(100, 30000), 2)
            
            movimentacao = {
                'id_movimentacao': id_mov,
                'id_empresa': empresa['id_empresa'],
                'data_movimentacao': fake.date_between(start_date=data_inicio, end_date=data_fim),
                'tipo_operacao': tipo,
                'categoria': categoria,
                'descricao_movimentacao': fake.sentence(nb_words=6),
                'valor_movimentacao': valor,
                'conciliada': 0  # Inicialmente nenhuma está conciliada
            }
            movimentacoes.append(movimentacao)
            id_mov += 1
    
    return pd.DataFrame(movimentacoes)


# Documentos fiscais
def gerar_documentos_fiscais(empresas_df, clientes_df, fornecedores_df, n_por_empresa=30):
    print(f"Gerando ~{n_por_empresa} documentos fiscais por empresa...")
    
    tipos_doc = ['NF-e', 'NFS-e', 'CT-e', 'NFC-e']
    status_doc = ['Ativa', 'Cancelada', 'Inutilizada']
    
    documentos = []
    id_doc = 1
    
    for _, empresa in empresas_df.iterrows():
        data_inicio = datetime.now() - timedelta(days=365)
        data_fim = datetime.now()
        
        for _ in range(n_por_empresa):
            tipo_operacao = random.choice(['Entrada', 'Saída'])
            
            if tipo_operacao == 'Saída':
                id_cliente = random.choice(clientes_df['id_cliente'].tolist())
                id_fornecedor = None
            else:
                id_cliente = None
                id_fornecedor = random.choice(fornecedores_df['id_fornecedor'].tolist())
            
            # Ocasionalmente cria documentos duplicados (inconsistência proposital)
            chave = gerar_chave_nfe()
            if random.random() < 0.02:  # 2% de chance de duplicar
                chave = documentos[-1]['chave_acesso'] if documentos else chave
            
            documento = {
                'id_documento': id_doc,
                'id_empresa': empresa['id_empresa'],
                'id_cliente': id_cliente,
                'id_fornecedor': id_fornecedor,
                'tipo_documento': random.choice(tipos_doc),
                'numero_documento': str(random.randint(1000, 999999)),
                'serie_documento': str(random.randint(1, 10)),
                'chave_acesso': chave,
                'data_emissao': fake.date_between(start_date=data_inicio, end_date=data_fim),
                'tipo_operacao': tipo_operacao,
                'valor': round(random.uniform(200, 80000), 2),
                'status_documento': random.choices(status_doc, weights=[0.9, 0.08, 0.02])[0]
            }
            documentos.append(documento)
            id_doc += 1
    
    return pd.DataFrame(documentos)


# Contas financeiras
def gerar_contas_financeiras(empresas_df, clientes_df, fornecedores_df, n_por_empresa=40):
    print(f"Gerando ~{n_por_empresa} contas financeiras por empresa...")
    
    status_pagamento = ['Pendente', 'Pago', 'Vencido', 'Cancelado']
    
    contas = []
    id_conta = 1
    
    for _, empresa in empresas_df.iterrows():
        data_inicio = datetime.now() - timedelta(days=365)
        data_fim = datetime.now() + timedelta(days=60)
        
        for _ in range(n_por_empresa):
            tipo_titulo = random.choice(['A Pagar', 'A Receber'])
            
            if tipo_titulo == 'A Receber':
                id_cliente = random.choice(clientes_df['id_cliente'].tolist())
                id_fornecedor = None
            else:
                id_cliente = None
                id_fornecedor = random.choice(fornecedores_df['id_fornecedor'].tolist())
            
            valor_original = round(random.uniform(300, 50000), 2)
            status = random.choices(status_pagamento, weights=[0.3, 0.5, 0.15, 0.05])[0]
            
            if status == 'Pago':
                # Ocasionalmente cria divergência (inconsistência proposital)
                if random.random() < 0.1:  # 10% de divergência
                    valor_pago = round(valor_original * random.uniform(0.85, 0.95), 2)
                else:
                    valor_pago = valor_original
                
                data_vencimento = fake.date_between(start_date=data_inicio, end_date=data_fim)
                data_pagamento = data_vencimento + timedelta(days=random.randint(-5, 15))
            else:
                valor_pago = 0.00
                data_vencimento = fake.date_between(start_date=data_inicio, end_date=data_fim)
                data_pagamento = None
            
            conta = {
                'id_conta': id_conta,
                'id_empresa': empresa['id_empresa'],
                'id_cliente': id_cliente,
                'id_fornecedor': id_fornecedor,
                'tipo_titulo': tipo_titulo,
                'valor_original': valor_original,
                'valor_pago': valor_pago,
                'data_vencimento': data_vencimento,
                'data_pagamento': data_pagamento,
                'status_pagamento': status,
                'descricao_pagamento': fake.sentence(nb_words=5)
            }
            contas.append(conta)
            id_conta += 1
    
    return pd.DataFrame(contas)


# Conciliações
def gerar_conciliacoes(contas_df, movimentacoes_df, taxa_conciliacao=0.6):
    print(f"Gerando conciliações (~{taxa_conciliacao*100}% das contas pagas)...")
    
    contas_pagas = contas_df[contas_df['status_pagamento'] == 'Pago'].copy()
    n_conciliacoes = int(len(contas_pagas) * taxa_conciliacao)
    contas_para_conciliar = contas_pagas.sample(n=n_conciliacoes, random_state=42)
    
    conciliacoes = []
    id_conc = 1
    movimentacoes_disponiveis = movimentacoes_df.copy()
    
    for _, conta in contas_para_conciliar.iterrows():
        # Busca movimentação da mesma empresa que ainda não foi conciliada
        candidatas = movimentacoes_disponiveis[
            (movimentacoes_disponiveis['id_empresa'] == conta['id_empresa']) &
            (movimentacoes_disponiveis['conciliada'] == 0)
        ]
        
        if len(candidatas) == 0:
            continue
        
        movimentacao = candidatas.sample(n=1).iloc[0]
        
        # Ocasionalmente cria inconsistência (valores diferentes)
        if random.random() < 0.15:  # 15% de inconsistência
            status_conc = 'Inconsistente'
            diferenca = round(abs(conta['valor_pago'] - movimentacao['valor_movimentacao']), 2)
        else:
            status_conc = 'Conciliado'
            diferenca = 0.00
        
        conciliacao = {
            'id_conciliacao': id_conc,
            'id_conta': conta['id_conta'],
            'id_movimentacao': movimentacao['id_movimentacao'],
            'data_conciliacao': max(conta['data_pagamento'], movimentacao['data_movimentacao']),
            'status_conciliacao': status_conc,
            'diferenca_valor': diferenca,
            'observacao': 'Conciliação automática' if status_conc == 'Conciliado' else f'Divergência de R$ {diferenca}'
        }
        conciliacoes.append(conciliacao)
        
        # Marca movimentação como conciliada
        movimentacoes_disponiveis.loc[
            movimentacoes_disponiveis['id_movimentacao'] == movimentacao['id_movimentacao'],
            'conciliada'
        ] = 1
        
        id_conc += 1
    
    return pd.DataFrame(conciliacoes), movimentacoes_disponiveis


def main():
    print("\n" + "="*60)
    print("FiscalAudit AI - Gerador de Dados Fictícios")
    print("="*60 + "\n")
    
    clientes_df = gerar_clientes(n=50)
    clientes_df.to_csv(f'{OUTPUT_DIR}/clientes.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Clientes salvos: {len(clientes_df)} registros\n")
    
    fornecedores_df = gerar_fornecedores(n=40)
    fornecedores_df.to_csv(f'{OUTPUT_DIR}/fornecedores.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Fornecedores salvos: {len(fornecedores_df)} registros\n")
    
    empresas_df = gerar_empresas(n=10)
    empresas_df.to_csv(f'{OUTPUT_DIR}/empresas.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Empresas salvas: {len(empresas_df)} registros\n")
    
    movimentacoes_df = gerar_movimentacoes_bancarias(empresas_df, n_por_empresa=50)
    movimentacoes_df.to_csv(f'{OUTPUT_DIR}/movimentacoes_bancarias.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Movimentações bancárias salvas: {len(movimentacoes_df)} registros\n")
    
    documentos_df = gerar_documentos_fiscais(empresas_df, clientes_df, fornecedores_df, n_por_empresa=30)
    documentos_df.to_csv(f'{OUTPUT_DIR}/documentos_fiscais.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Documentos fiscais salvos: {len(documentos_df)} registros\n")
    
    contas_df = gerar_contas_financeiras(empresas_df, clientes_df, fornecedores_df, n_por_empresa=40)
    contas_df.to_csv(f'{OUTPUT_DIR}/contas_financeiras.csv', index=False, encoding='utf-8-sig')
    print(f"✓ Contas financeiras salvas: {len(contas_df)} registros\n")
    
    conciliacoes_df, movimentacoes_atualizadas_df = gerar_conciliacoes(
        contas_df, movimentacoes_df, taxa_conciliacao=0.6
    )
    conciliacoes_df.to_csv(f'{OUTPUT_DIR}/conciliacoes.csv', index=False, encoding='utf-8-sig')
    movimentacoes_atualizadas_df.to_csv(
        f'{OUTPUT_DIR}/movimentacoes_bancarias.csv', index=False, encoding='utf-8-sig'
    )
    print(f"✓ Conciliações salvas: {len(conciliacoes_df)} registros\n")
    
    print("="*60)
    print("RESUMO DA GERAÇÃO")
    print("="*60)
    print(f"Clientes:                {len(clientes_df):>6}")
    print(f"Fornecedores:            {len(fornecedores_df):>6}")
    print(f"Empresas:                {len(empresas_df):>6}")
    print(f"Movimentações Bancárias: {len(movimentacoes_df):>6}")
    print(f"Documentos Fiscais:      {len(documentos_df):>6}")
    print(f"Contas Financeiras:      {len(contas_df):>6}")
    print(f"Conciliações:            {len(conciliacoes_df):>6}")
    print("="*60)
    print(f"\n✓ Todos os arquivos salvos em: {OUTPUT_DIR}/")
    print("\nInconsistências propositais incluídas:")
    print("  • ~2% de notas fiscais duplicadas")
    print("  • ~10% de divergências em valores pagos")
    print("  • ~15% de conciliações com diferenças")
    print("  • ~40% de movimentações sem conciliação")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    main()
