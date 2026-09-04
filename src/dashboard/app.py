"""
Dashboard do FiscalAudit AI
Rodar com:  streamlit run src/dashboard/app.py
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="FiscalAudit AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------
# CSS customizado — tema escuro profissional
# (usando só seletores simples, sem CSS custom properties)
# ---------------------------------------------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"]          { background: #161b27; border-right: 1px solid #2a2f3e; }
[data-testid="stHeader"]           { background: #0f1117 !important; height: 0px !important; min-height: 0 !important; }
[data-testid="stToolbar"]          { display: none !important; }
section[data-testid="stSidebar"] > div:first-child { padding-top: 20px; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
html, body, [class*="css"]  { font-family: 'Inter','Segoe UI',sans-serif; color: #e2e8f0; }
.stRadio > label            { color: #cbd5e1 !important; font-size: 13px; }
.stRadio [data-baseweb="radio"] { gap: 10px; }
.block-container { padding-top: 1.5rem !important; }

/* sidebar */
.sidebar-brand   { font-size: 18px; font-weight: 700; color: #f1f5f9; padding: 4px 0 2px 0; }
.sidebar-sub     { font-size: 12px; color: #94a3b8; margin-top: 2px; margin-bottom: 4px; }
.sidebar-divider { border: none; border-top: 1px solid #2a3045; margin: 12px 0; }

/* títulos de seção */
.section-title { font-size: 22px; font-weight: 700; color: #f1f5f9; margin-bottom: 4px; }
.section-sub   { font-size: 14px; color: #94a3b8; margin-bottom: 16px; }

/* badges de prioridade */
.badge        { display: inline-block; padding: 2px 10px; border-radius: 9999px;
                font-size: 12px; font-weight: 600; margin-right: 4px; }
.badge-red    { background: #7f1d1d; color: #fca5a5; }
.badge-yellow { background: #713f12; color: #fde68a; }
.badge-blue   { background: #1e3a5f; color: #93c5fd; }

/* tabelas */
[data-testid="stDataFrame"] { color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
PROCESSED = os.path.join(PROJECT_ROOT, 'data', 'processed')

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cbd5e1', size=12),
    margin=dict(t=16, b=16, l=8, r=8),
)

COLORS = {
    'red':    '#ef4444',
    'orange': '#f97316',
    'yellow': '#eab308',
    'purple': '#a855f7',
    'blue':   '#3b82f6',
    'teal':   '#14b8a6',
    'grid':   '#2a3045',
}


@st.cache_data
def ler(nome):
    p = os.path.join(PROCESSED, nome)
    return pd.read_csv(p, encoding='utf-8-sig') if os.path.exists(p) else pd.DataFrame()


def reais(v):
    try:
        return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "—"


def card(col, label, valor, sub=None, cor="#3b82f6"):
    sub_html = (f'<div style="font-size:12px;color:#94a3b8;margin-top:5px">{sub}</div>'
                if sub else '')
    col.markdown(
        f'<div style="background:#1e2435;border:1px solid #2a3045;border-radius:12px;'
        f'padding:20px 22px;border-left:5px solid {cor};margin-bottom:4px">'
        f'<div style="font-size:11px;color:#94a3b8;text-transform:uppercase;'
        f'letter-spacing:0.8px;margin-bottom:8px;font-weight:600">{label}</div>'
        f'<div style="font-size:30px;font-weight:700;color:#f1f5f9;line-height:1">{valor}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def plotly_dark(fig, height=300):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    fig.update_xaxes(gridcolor=COLORS['grid'], zeroline=False)
    fig.update_yaxes(gridcolor=COLORS['grid'], zeroline=False)
    return fig


# ---------------------------------------------------------------
# carrega dados
# ---------------------------------------------------------------
div  = ler('divergencias_pagamento.csv')
conc = ler('conciliacoes_inconsistentes.csv')
mov  = ler('movimentacoes_sem_conciliacao.csv')
docs = ler('documentos_problema.csv')
dup  = ler('documentos_duplicados.csv')
anom = ler('anomalias_ml.csv')

# ---------------------------------------------------------------
# sidebar
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🔍 FiscalAudit AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Auditoria financeira com Python + ML</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    pagina = st.radio(
        "",
        ["Visão Geral", "Divergências de Pagamento", "Conciliações",
         "Movimentações sem Conciliação", "Documentos Fiscais", "Anomalias ML"],
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    total = len(div) + len(conc) + len(mov) + len(docs) + len(dup)
    st.markdown(f'<div style="font-size:12px;color:#475569">{total} achados encontrados</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# Visão Geral
# ---------------------------------------------------------------
if pagina == "Visão Geral":
    st.markdown('<div class="section-title">Visão Geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Resumo dos achados das regras de auditoria e do modelo de machine learning.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    card(c1, "Divergências de pagamento", len(div),
         reais(div['diferenca'].sum()) if 'diferenca' in div.columns else None,
         COLORS['red'])
    card(c2, "Conciliações inconsistentes", len(conc), cor=COLORS['orange'])
    card(c3, "Sem conciliação (banco)", len(mov),
         reais(mov['valor_movimentacao'].sum()) if 'valor_movimentacao' in mov.columns else None,
         COLORS['yellow'])
    card(c4, "Anomalias ML", len(anom), "sinalizadas pelo modelo", COLORS['purple'])

    st.markdown("")
    c5, c6 = st.columns(2)
    card(c5, "Documentos com problema", len(docs), "cancelados ou inutilizados", COLORS['red'])
    card(c6, "Notas fiscais duplicadas", len(dup), "mesma chave de acesso", COLORS['orange'])

    st.markdown("")

    # gráficos
    cats = {"Divergências": len(div), "Conciliações": len(conc),
            "Sem conciliação": len(mov), "Docs problema": len(docs),
            "Duplicados": len(dup), "Anomalias ML": len(anom)}
    df_cat = pd.DataFrame(cats.items(), columns=["Categoria", "Qtd"])
    df_cat = df_cat[df_cat.Qtd > 0]

    col_p, col_b = st.columns(2)
    with col_p:
        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Distribuição por categoria</div>', unsafe_allow_html=True)
        fig = px.pie(df_cat, values="Qtd", names="Categoria",
                     color_discrete_sequence=['#ef4444','#f97316','#eab308','#a855f7','#3b82f6','#14b8a6'])
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=11, marker=dict(line=dict(color='#0f1117', width=2)))
        plotly_dark(fig, 300)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Quantidade por categoria</div>', unsafe_allow_html=True)
        df_sorted = df_cat.sort_values("Qtd")
        bar_colors = ['#ef4444','#f97316','#eab308','#a855f7','#3b82f6','#14b8a6'][:len(df_sorted)]
        fig2 = px.bar(df_sorted, x="Qtd", y="Categoria", orientation='h',
                      color="Categoria",
                      color_discrete_sequence=bar_colors)
        fig2.update_traces(marker_line_width=0)
        plotly_dark(fig2, 300)
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    # prioridade
    st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin:8px 0 12px 0">Prioridade de resolução</div>', unsafe_allow_html=True)
    st.markdown("""
    <span class="badge badge-red">Alta</span> Conciliações inconsistentes — são poucas mas travam o fechamento<br><br>
    <span class="badge badge-red">Alta</span> Divergências de pagamento — pode ser desconto não registrado ou erro de digitação<br><br>
    <span class="badge badge-yellow">Média</span> Movimentações sem conciliação — volume alto, muitas são só atraso de baixa<br><br>
    <span class="badge badge-blue">Baixa</span> Documentos fiscais — cancelados/duplicados precisam de ajuste no registro
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Divergências de pagamento
# ---------------------------------------------------------------
elif pagina == "Divergências de Pagamento":
    st.markdown('<div class="section-title">Divergências de Pagamento</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Contas pagas onde <code>valor_pago ≠ valor_original</code>.</div>', unsafe_allow_html=True)

    if div.empty:
        st.info("Nenhuma divergência encontrada.")
    else:
        total_dif = div['diferenca'].sum() if 'diferenca' in div.columns else 0
        c1, c2, c3 = st.columns(3)
        card(c1, "Contas com divergência", len(div), cor=COLORS['red'])
        card(c2, "Soma das diferenças", reais(total_dif), cor=COLORS['red'])
        card(c3, "Maior diferença", reais(div['diferenca'].max()) if 'diferenca' in div.columns else "—", cor=COLORS['red'])

        st.markdown("")
        if 'empresa' in div.columns and 'diferenca' in div.columns:
            st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Soma das diferenças por empresa</div>', unsafe_allow_html=True)
            por = div.groupby('empresa')['diferenca'].agg(['count','sum']).reset_index()
            por.columns = ['Empresa','Qtd','Total']
            por = por.sort_values('Total', ascending=True)
            fig = px.bar(por, x='Total', y='Empresa', orientation='h',
                         color='Total', color_continuous_scale=['#7f1d1d','#ef4444'])
            fig.update_traces(marker_line_width=0)
            plotly_dark(fig, max(260, len(por)*36))
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                               xaxis_title="R$", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin:8px 0 8px 0">Detalhe</div>', unsafe_allow_html=True)
        df_show = div.sort_values('diferenca', ascending=False) if 'diferenca' in div.columns else div
        st.dataframe(df_show, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------
# Conciliações
# ---------------------------------------------------------------
elif pagina == "Conciliações":
    st.markdown('<div class="section-title">Conciliações Inconsistentes</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Conciliações onde o valor do título e o valor do banco não fecham.</div>', unsafe_allow_html=True)

    if conc.empty:
        st.info("Nenhuma conciliação inconsistente encontrada.")
    else:
        c1, c2 = st.columns(2)
        card(c1, "Conciliações com problema", len(conc), cor=COLORS['orange'])
        if 'diferenca_valor' in conc.columns:
            card(c2, "Soma das diferenças", reais(conc['diferenca_valor'].sum()), cor=COLORS['orange'])

        if 'empresa' in conc.columns:
            st.markdown("")
            st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Por empresa</div>', unsafe_allow_html=True)
            por = conc.groupby('empresa').size().reset_index(name='Qtd').sort_values('Qtd')
            fig = px.bar(por, x='Qtd', y='empresa', orientation='h',
                         color_discrete_sequence=[COLORS['orange']])
            fig.update_traces(marker_line_width=0)
            plotly_dark(fig, max(220, len(por)*36))
            fig.update_layout(xaxis_title="", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin:8px 0 8px 0">Detalhe</div>', unsafe_allow_html=True)
        st.dataframe(conc, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------
# Movimentações sem conciliação
# ---------------------------------------------------------------
elif pagina == "Movimentações sem Conciliação":
    st.markdown('<div class="section-title">Movimentações sem Conciliação</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Transações no extrato bancário que ainda não foram ligadas a nenhum título.</div>', unsafe_allow_html=True)

    if mov.empty:
        st.info("Todas as movimentações estão conciliadas.")
    else:
        total_val = mov['valor_movimentacao'].sum() if 'valor_movimentacao' in mov.columns else 0
        c1, c2, c3 = st.columns(3)
        card(c1, "Movimentações pendentes", len(mov), cor=COLORS['yellow'])
        card(c2, "Valor total", reais(total_val), cor=COLORS['yellow'])
        if 'empresa' in mov.columns:
            card(c3, "Empresas afetadas", mov['empresa'].nunique(), cor=COLORS['yellow'])

        col_a, col_b = st.columns(2)

        if 'tipo_operacao' in mov.columns:
            with col_a:
                st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Por tipo de operação</div>', unsafe_allow_html=True)
                por_tipo = mov.groupby('tipo_operacao').size().reset_index(name='Qtd')
                fig = px.pie(por_tipo, values='Qtd', names='tipo_operacao',
                             color_discrete_sequence=[COLORS['yellow'], COLORS['orange']])
                fig.update_traces(textinfo='percent+label',
                                  marker=dict(line=dict(color='#0f1117', width=2)))
                plotly_dark(fig, 280)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        if 'data_movimentacao' in mov.columns:
            with col_b:
                st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Evolução no tempo</div>', unsafe_allow_html=True)
                mov['data_movimentacao'] = pd.to_datetime(mov['data_movimentacao'], errors='coerce')
                por_mes = mov.groupby(mov['data_movimentacao'].dt.to_period('M')).size().reset_index(name='Qtd')
                por_mes['data_movimentacao'] = por_mes['data_movimentacao'].astype(str)
                fig2 = px.area(por_mes, x='data_movimentacao', y='Qtd',
                               color_discrete_sequence=[COLORS['yellow']])
                fig2.update_traces(fill='tozeroy',
                                   fillcolor='rgba(234,179,8,0.12)',
                                   line=dict(width=2))
                plotly_dark(fig2, 280)
                fig2.update_layout(xaxis_title="", yaxis_title="")
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin:8px 0 8px 0">Detalhe</div>', unsafe_allow_html=True)
        st.dataframe(mov, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------
# Documentos Fiscais
# ---------------------------------------------------------------
elif pagina == "Documentos Fiscais":
    st.markdown('<div class="section-title">Documentos Fiscais</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Documentos com situação irregular: cancelados, inutilizados ou com chave duplicada.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    card(c1, "Com problema", len(docs), "cancelados ou inutilizados", COLORS['red'])
    card(c2, "Duplicados", len(dup), "mesma chave de acesso", COLORS['orange'])

    st.markdown("")
    aba1, aba2 = st.tabs(["📋 Com problema", "📋 Duplicados"])

    with aba1:
        if docs.empty:
            st.info("Nenhum documento com problema.")
        else:
            if 'status_documento' in docs.columns and 'tipo_documento' in docs.columns:
                col_s, col_t = st.columns(2)
                with col_s:
                    por_status = docs.groupby('status_documento').size().reset_index(name='Qtd')
                    fig = px.pie(por_status, values='Qtd', names='status_documento',
                                 color_discrete_sequence=[COLORS['red'],'#7f1d1d'])
                    fig.update_traces(textinfo='percent+label',
                                      marker=dict(line=dict(color='#0f1117', width=2)))
                    plotly_dark(fig, 240)
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                with col_t:
                    por_tipo = docs.groupby('tipo_documento').size().reset_index(name='Qtd')
                    fig2 = px.bar(por_tipo, x='tipo_documento', y='Qtd',
                                  color_discrete_sequence=[COLORS['red']])
                    fig2.update_traces(marker_line_width=0)
                    plotly_dark(fig2, 240)
                    fig2.update_layout(xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(docs, use_container_width=True, hide_index=True)

    with aba2:
        if dup.empty:
            st.info("Nenhum documento duplicado encontrado.")
        else:
            st.markdown(f'<div style="font-size:13px;color:#94a3b8;margin-bottom:12px">{len(dup)} documentos com chave de acesso repetida — separados na carga ETL para revisão.</div>', unsafe_allow_html=True)
            st.dataframe(dup, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------
# Anomalias ML
# ---------------------------------------------------------------
elif pagina == "Anomalias ML":
    st.markdown('<div class="section-title">Anomalias Detectadas pelo Modelo</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Isolation Forest analisou valor, atraso e padrão histórico por empresa. Quanto mais negativo o score, mais atípica é a conta.</div>', unsafe_allow_html=True)

    if anom.empty:
        st.info("Nenhuma anomalia detectada ou modelo ainda não rodou.")
    else:
        c1, c2, c3 = st.columns(3)
        card(c1, "Anomalias detectadas", len(anom), "≈ 10% das contas pagas", COLORS['purple'])
        if 'score_anomalia' in anom.columns:
            card(c2, "Score mais baixo (mais suspeito)", f"{anom['score_anomalia'].min():.3f}", cor=COLORS['purple'])
            card(c3, "Score médio", f"{anom['score_anomalia'].mean():.3f}", cor=COLORS['purple'])

        st.markdown("")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">Score por conta (top 15 mais suspeitas)</div>', unsafe_allow_html=True)
            df_top = anom.sort_values('score_anomalia').head(15).copy()
            df_top['conta_label'] = ('Conta #' + df_top['id_conta'].astype(str)).astype(str)
            fig = go.Figure(go.Bar(
                x=df_top['score_anomalia'],
                y=df_top['conta_label'],
                orientation='h',
                marker=dict(
                    color=df_top['score_anomalia'],
                    colorscale=[[0,'#7c3aed'],[0.5,'#a855f7'],[1,'#d8b4fe']],
                    line=dict(width=0),
                ),
                text=df_top['score_anomalia'].round(3).astype(str),
                textposition='outside',
                textfont=dict(color='#94a3b8', size=11),
            ))
            plotly_dark(fig, 420)
            fig.update_layout(xaxis_title="score", yaxis_title="",
                               yaxis=dict(type='category', autorange='reversed'))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin-bottom:8px">% diferença × dias de atraso</div>', unsafe_allow_html=True)
            hover = ['id_conta', 'razao_social'] if 'razao_social' in anom.columns else ['id_conta']
            fig2 = px.scatter(anom, x='dias_atraso', y='perc_diferenca',
                              color='score_anomalia',
                              hover_data=hover,
                              color_continuous_scale=['#7c3aed','#f97316'],
                              labels={'dias_atraso':'Dias de atraso','perc_diferenca':'% diferença'})
            fig2.update_traces(marker=dict(size=10, line=dict(width=0)))
            plotly_dark(fig2, 380)
            fig2.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div style="font-size:14px;font-weight:600;color:#94a3b8;margin:8px 0 8px 0">Todas as anomalias</div>', unsafe_allow_html=True)
        df_show = anom.sort_values('score_anomalia') if 'score_anomalia' in anom.columns else anom
        st.dataframe(df_show, use_container_width=True, hide_index=True)
