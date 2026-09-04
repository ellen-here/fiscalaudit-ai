"""
Gera um relatório de auditoria em linguagem natural a partir dos achados
das fases anteriores (regras + machine learning).

Se tiver uma chave da OpenAI no .env, ele usa a IA pra deixar o texto mais
fluido. Se não tiver, ele mesmo monta o texto — funciona do mesmo jeito,
só fica um pouco mais "template".
"""

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')


def ler_csv(nome):
    """Lê um csv de data/processed. Se não existir, devolve um df vazio."""
    caminho = os.path.join(PROCESSED_DIR, nome)
    if os.path.exists(caminho):
        return pd.read_csv(caminho, encoding='utf-8-sig')
    return pd.DataFrame()


def reais(valor):
    """Formata um número no padrão brasileiro: 1234.5 -> 1.234,50"""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def juntar_achados():
    """Junta tudo que as fases anteriores acharam num resumo só."""
    div = ler_csv('divergencias_pagamento.csv')
    conc = ler_csv('conciliacoes_inconsistentes.csv')
    mov = ler_csv('movimentacoes_sem_conciliacao.csv')
    docs = ler_csv('documentos_problema.csv')
    dup = ler_csv('documentos_duplicados.csv')
    anom = ler_csv('anomalias_ml.csv')

    resumo = {
        'divergencias': len(div),
        'valor_divergencias': div['diferenca'].sum() if 'diferenca' in div else 0,
        'conciliacoes': len(conc),
        'mov_sem_conciliacao': len(mov),
        'valor_mov_sem_conciliacao': mov['valor_movimentacao'].sum() if 'valor_movimentacao' in mov else 0,
        'docs_problema': len(docs),
        'docs_duplicados': len(dup),
        'anomalias_ml': len(anom),
    }

    # guardo os dfs também pra quem quiser detalhar depois
    return resumo, {'divergencias': div, 'anomalias': anom, 'movimentacoes': mov}


def montar_texto(resumo, detalhes):
    """
    Monta o relatório na mão, em português. É o modo que roda sempre,
    com ou sem IA.
    """
    hoje = datetime.now().strftime('%d/%m/%Y')
    total_achados = (resumo['divergencias'] + resumo['conciliacoes'] +
                     resumo['mov_sem_conciliacao'] + resumo['docs_problema'] +
                     resumo['docs_duplicados'])

    linhas = []
    linhas.append(f"# Relatório de Auditoria — FiscalAudit AI")
    linhas.append(f"\n_Gerado em {hoje}_\n")

    # abertura
    linhas.append("## Resumo\n")
    if total_achados == 0:
        linhas.append("Boa notícia: não encontramos inconsistências relevantes desta vez.\n")
    else:
        linhas.append(
            f"Passei os dados pelas regras de auditoria e pelo modelo de anomalias. "
            f"No total, apareceram **{total_achados} pontos** que valem uma olhada antes "
            f"do fechamento. Abaixo separei por tipo, do mais crítico pro que é mais "
            f"rotina de revisão.\n"
        )

    # divergências de pagamento
    if resumo['divergencias'] > 0:
        linhas.append("## Divergências de pagamento\n")
        linhas.append(
            f"Encontrei **{resumo['divergencias']} contas** marcadas como pagas onde o "
            f"valor pago não bate com o valor original. Somando as diferenças, dá "
            f"**R$ {reais(resumo['valor_divergencias'])}**.\n"
        )
        div = detalhes['divergencias']
        if not div.empty and 'diferenca' in div:
            top = div.nlargest(3, 'diferenca')
            linhas.append("As três maiores:\n")
            for _, r in top.iterrows():
                linhas.append(
                    f"- Conta #{int(r['id_conta'])} ({r.get('empresa', 'empresa')}): "
                    f"original R$ {reais(r['valor_original'])}, pago R$ {reais(r['valor_pago'])} "
                    f"— diferença de R$ {reais(r['diferenca'])}"
                )
            linhas.append("")
        linhas.append(
            "_Vale checar se foi desconto combinado, pagamento parcial marcado errado, "
            "ou só erro de digitação._\n"
        )

    # conciliações
    if resumo['conciliacoes'] > 0:
        linhas.append("## Conciliações inconsistentes\n")
        linhas.append(
            f"Tem **{resumo['conciliacoes']} conciliações** onde o valor da conta e o "
            f"valor que caiu no banco não fecham. Normalmente é lançamento em conta "
            f"errada ou diferença de data — mas precisa conferir uma a uma.\n"
        )

    # movimentações sem conciliação
    if resumo['mov_sem_conciliacao'] > 0:
        linhas.append("## Movimentações do banco sem conciliação\n")
        linhas.append(
            f"Esse é o volume maior: **{resumo['mov_sem_conciliacao']} movimentações** no "
            f"extrato que ainda não foram ligadas a nenhum título, somando "
            f"**R$ {reais(resumo['valor_mov_sem_conciliacao'])}**.\n"
        )
        linhas.append(
            "_Não quer dizer que tem algo errado — pode ser só conciliação pendente. "
            "Mas é o que mais precisa de atenção pra fechar o mês certinho._\n"
        )

    # documentos
    if resumo['docs_problema'] > 0 or resumo['docs_duplicados'] > 0:
        linhas.append("## Documentos fiscais\n")
        if resumo['docs_duplicados'] > 0:
            linhas.append(
                f"- **{resumo['docs_duplicados']} notas com chave de acesso repetida** "
                f"(possível emissão duplicada) — foram separadas na carga pra revisão."
            )
        if resumo['docs_problema'] > 0:
            linhas.append(
                f"- **{resumo['docs_problema']} documentos** cancelados ou inutilizados "
                f"que podem precisar de ajuste no registro."
            )
        linhas.append("")

    # anomalias do ML
    if resumo['anomalias_ml'] > 0:
        linhas.append("## O que o modelo de anomalias achou\n")
        linhas.append(
            f"Além das regras, o modelo de machine learning sinalizou "
            f"**{resumo['anomalias_ml']} contas** com comportamento fora do padrão — "
            f"olhando valor, atraso e o histórico de cada empresa junto.\n"
        )
        anom = detalhes['anomalias']
        if not anom.empty and 'score_anomalia' in anom:
            top = anom.nsmallest(3, 'score_anomalia')
            linhas.append("As mais atípicas:\n")
            for _, r in top.iterrows():
                linhas.append(
                    f"- Conta #{int(r['id_conta'])} ({r.get('razao_social', '')}): "
                    f"diferença de {r.get('perc_diferenca', 0):.1f}%, "
                    f"{int(r.get('dias_atraso', 0))} dias de atraso"
                )
            linhas.append("")

    # fechamento
    linhas.append("## Sugestão de prioridade\n")
    linhas.append(
        "1. Resolver as conciliações inconsistentes (são poucas e travam o fechamento)\n"
        "2. Conferir as divergências de pagamento maiores\n"
        "3. Ir zerando as movimentações sem conciliação\n"
        "4. Ajustar os documentos duplicados/cancelados quando sobrar tempo\n"
    )

    return "\n".join(linhas)


def refinar_com_ia(texto_base, resumo):
    """
    Se tiver chave da OpenAI, pede pra ela reescrever o relatório num tom
    mais natural. Se não tiver (ou der erro), devolve o texto base mesmo.
    """
    chave = os.getenv('OPENAI_API_KEY')
    if not chave:
        return texto_base, False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=chave)

        prompt = (
            "Você é um assistente que ajuda um escritório de contabilidade. "
            "Reescreva o relatório de auditoria abaixo num tom claro e profissional, "
            "mas acessível — como se estivesse explicando pro contador o que precisa "
            "de atenção. Mantenha os números exatos. Não invente nada.\n\n"
            f"{texto_base}"
        )

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resposta.choices[0].message.content, True

    except Exception as e:
        print(f"   (não deu pra usar a IA: {e} — seguindo com o texto padrão)")
        return texto_base, False


def main():
    print("\nGerando relatório de auditoria...\n")

    resumo, detalhes = juntar_achados()
    texto = montar_texto(resumo, detalhes)

    texto_final, usou_ia = refinar_com_ia(texto, resumo)

    caminho = os.path.join(OUTPUT_DIR, 'relatorio_auditoria.md')
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(texto_final)

    origem = "com ajuda da IA" if usou_ia else "modo texto padrão (sem chave de IA)"
    print(f"Pronto ({origem}).")
    print(f"Salvo em data/processed/relatorio_auditoria.md\n")

    # mostra uma prévia
    print("-" * 60)
    print("\n".join(texto_final.split("\n")[:20]))
    print("-" * 60)


if __name__ == '__main__':
    main()
