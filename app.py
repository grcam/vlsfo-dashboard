import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import difflib
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="VLSFO Dashboard", layout="wide")

# Função para correspondência difusa de colunas
def fuzzy_match_column(df, target):
    matches = difflib.get_close_matches(target, df.columns, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Função para carregar dados do Excel com tratamento de erros
def load_data():
    try:
        df = pd.read_excel('dashboard.xlsx')
        return df
    except FileNotFoundError:
        st.error("Erro: Arquivo 'dashboard.xlsx' não encontrado. Verifique o caminho do arquivo.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Carregar dados
df = load_data()
if df is None:
    st.stop()

# Definir abas
tab1, tab2 = st.tabs(["Bunker Benchmarks", "Core Flat Prices"])

# TAB 1: Bunker Benchmarks
with tab1:
    st.header("Bunker Benchmarks")
    
    # Definir os portos e seus códigos
    ports = {
        "Santos": "MFSAD00",
        "Montevideo": "AMFMT00",
        "Balboa": "MFBAE00",
        "Buenos Aires": "MFBAD00",
        "Singapore": "PUAFT00",
        "Singapore Ex-wharf": "MFSPE00"
    }
    
    # Layout: 2 linhas de 3 colunas
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    columns = [col1, col2, col3, col4, col5, col6]
    
    for i, (port, code) in enumerate(ports.items()):
        with columns[i]:
            # Correspondência difusa para a coluna do preço
            price_col = fuzzy_match_column(df, f"{code}_price")
            if price_col is None:
                st.error(f"Coluna para {port} não encontrada.")
                continue
            
            # Assumir que há uma coluna de data para ordenar
            date_col = fuzzy_match_column(df, "date")
            if date_col:
                df_sorted = df.sort_values(by=date_col)
            else:
                df_sorted = df
            
            # Último preço
            latest_price = df_sorted[price_col].iloc[-1]
            
            # Preço anterior (assumir diário)
            if len(df_sorted) > 1:
                prev_price = df_sorted[price_col].iloc[-2]
                change_pct = ((latest_price - prev_price) / prev_price) * 100
            else:
                change_pct = 0
            
            # Cor da seta
            delta_color = "normal" if change_pct >= 0 else "inverse"
            
            # Exibir como métrica
            st.metric(label=f"{port} ({code})", value=f"{latest_price:.2f}", delta=f"{change_pct:.2f}%", delta_color=delta_color)

# TAB 2: Core Flat Prices
with tab2:
    st.header("Core Flat Prices")
    
    # Chart 1: FOB ARA, SGP (MOPS), USGC, Fujairah
    st.subheader("FOB ARA, SGP (MOPS), USGC, Fujairah")
    fig1 = go.Figure()
    for col in ["FOB_ARA", "SGP_MOPS", "USGC", "Fujairah"]:
        matched_col = fuzzy_match_column(df, col)
        if matched_col:
            fig1.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[matched_col], mode='lines', name=col))
    fig1.update_layout(title="Preços FOB ARA, SGP (MOPS), USGC, Fujairah", xaxis_title="Data", yaxis_title="Preço")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: FO 1% Rotterdam + AMRAM01 together
    st.subheader("FO 1% Rotterdam + AMRAM01")
    fig2 = go.Figure()
    for col in ["FO_1_Rotterdam", "AMRAM01"]:
        matched_col = fuzzy_match_column(df, col)
        if matched_col:
            fig2.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[matched_col], mode='lines', name=col))
    fig2.update_layout(title="FO 1% Rotterdam + AMRAM01", xaxis_title="Data", yaxis_title="Preço")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Chart 3: FOFSB00 (strip) + MOPS together
    st.subheader("FOFSB00 (strip) + MOPS")
    fig3 = go.Figure()
    for col in ["FOFSB00", "MOPS"]:
        matched_col = fuzzy_match_column(df, col)
        if matched_col:
            fig3.add_trace(go.Scatter(x=df[date_col] if date_col else df.index, y=df[matched_col], mode='lines', name=col))
    fig3.update_layout(title="FOFSB00 (strip) + MOPS", xaxis_title="Data", yaxis_title="Preço")
    st.plotly_chart(fig3, use_container_width=True)