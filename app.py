import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import difflib

# Function to generate sample data if Excel fails
def generate_sample_data():
    dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='D')
    data = {
        'Date': dates,
        'Santos': [random.uniform(50, 70) for _ in dates],
        'Montevideo': [random.uniform(50, 70) for _ in dates],
        'Balboa': [random.uniform(50, 70) for _ in dates],
        'Buenos Aires': [random.uniform(50, 70) for _ in dates],
        'Singapore 1': [random.uniform(50, 70) for _ in dates],
        'Singapore 2': [random.uniform(50, 70) for _ in dates],
        'ARA': [random.uniform(50, 70) for _ in dates],
        'SGP': [random.uniform(50, 70) for _ in dates],
        'USGC': [random.uniform(50, 70) for _ in dates],
        'Fujairah': [random.uniform(50, 70) for _ in dates],
        'Rotterdam': [random.uniform(50, 70) for _ in dates],
        'AMRAM01': [random.uniform(50, 70) for _ in dates],
        'FOFSB00': [random.uniform(50, 70) for _ in dates],
        'MOPS': [random.uniform(50, 70) for _ in dates],
    }
    return pd.DataFrame(data)

# Function to load data with fallbacks
def load_data():
    try:
        df = pd.read_excel('dashboard.xlsx')
        st.success('Dados carregados do arquivo Excel com sucesso.')
    except Exception as e:
        st.warning(f'Erro ao carregar o arquivo Excel: {str(e)}. Usando dados de exemplo.')
        df = generate_sample_data()
    return df

# Function to auto-detect date column
def detect_date_column(df):
    possible_dates = ['date', 'data', 'dt', 'time', 'timestamp']
    for col in df.columns:
        if any(difflib.SequenceMatcher(None, col.lower(), pd.lower()).ratio() > 0.8 for pd in possible_dates):
            try:
                df[col] = pd.to_datetime(df[col])
                return col
            except:
                pass
    # Fallback: assume first column if datetime-like
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
                return col
            except:
                pass
    st.error('Coluna de data não encontrada. Verifique o arquivo Excel.')
    return None

# Function to auto-detect price columns with fuzzy matching
def detect_price_columns(df, required_columns):
    detected = {}
    for req in required_columns:
        best_match = None
        best_ratio = 0
        for col in df.columns:
            ratio = difflib.SequenceMatcher(None, req.lower(), col.lower()).ratio()
            if ratio > best_ratio and ratio > 0.6:  # Threshold for match
                best_match = col
                best_ratio = ratio
        if best_match:
            detected[req] = best_match
        else:
            st.warning(f'Coluna para {req} não encontrada. Usando valores padrão.')
            detected[req] = None
    return detected

# Main app
def main():
    st.set_page_config(page_title='Dashboard de Preços', layout='wide')
    st.title('Dashboard de Preços de Bunker e Combustíveis')

    # Load data
    df = load_data()
    if df.empty:
        st.error('Dados não disponíveis.')
        return

    # Detect date column
    date_col = detect_date_column(df)
    if not date_col:
        return

    # Required columns for bunkers and cores
    bunker_cols = ['Santos', 'Montevideo', 'Balboa', 'Buenos Aires', 'Singapore 1', 'Singapore 2']
    core_cols = ['ARA', 'SGP', 'USGC', 'Fujairah', 'Rotterdam', 'AMRAM01', 'FOFSB00', 'MOPS']
    all_required = bunker_cols + core_cols

    # Detect price columns
    detected_cols = detect_price_columns(df, all_required)

    # Tabs
    tab1, tab2 = st.tabs(['Bunker Benchmarks', 'Core Flat Prices'])

    with tab1:
        st.header('Benchmarks de Bunker')
        cols = st.columns(3)
        for i, bunker in enumerate(bunker_cols):
            col = detected_cols.get(bunker)
            if col and col in df.columns:
                latest = df[col].iloc[-1]
                prev = df[col].iloc[-2] if len(df) > 1 else latest
                change = ((latest - prev) / prev) * 100 if prev != 0 else 0
                delta_color = 'normal' if change >= 0 else 'inverse'
                arrow = '🔺' if change >= 0 else '🔻'
                cols[i % 3].metric(f'{bunker} {arrow}', f'{latest:.2f}', f'{change:.2f}%', delta_color=delta_color)
            else:
                cols[i % 3].metric(bunker, 'N/A', 'Dados indisponíveis')

    with tab2:
        st.header('Preços Flat de Core')
        chart_cols = ['ARA', 'SGP', 'USGC', 'Fujairah', 'Rotterdam+AMRAM01', 'FOFSB00+MOPS']
        for chart in chart_cols:
            if '+' in chart:
                parts = chart.split('+')
                cols = [detected_cols.get(p) for p in parts if detected_cols.get(p)]
                if cols:
                    fig = px.line(df, x=date_col, y=cols, title=chart)
                    st.plotly_chart(fig)
                else:
                    st.warning(f'Dados para {chart} não disponíveis.')
            else:
                col = detected_cols.get(chart)
                if col and col in df.columns:
                    fig = px.line(df, x=date_col, y=col, title=chart)
                    st.plotly_chart(fig)
                else:
                    st.warning(f'Dados para {chart} não disponíveis.')

    # Debug info
    if st.checkbox('Mostrar informações de debug'):
        st.write('Colunas detectadas:', detected_cols)
        st.write('Primeiras linhas do DataFrame:', df.head())

if __name__ == '__main__':
    main()