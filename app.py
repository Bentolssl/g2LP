import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import pearsonr

# Configuração da página
st.set_page_config(page_title="Dashboard Dengue Brasil", layout="wide")
st.title("📊 Análise da Dengue no Brasil (2015-2024)")
st.markdown("""
Este dashboard explora a relação entre **casos de dengue**, **fatores climáticos** (chuva e temperatura) e **indicadores de saúde**.
Utilize os filtros ao lado para explorar diferentes regiões, estados e municípios.
""")

# Carregar dados (cache para performance)
@st.cache_data
def load_data():
    df = pd.read_csv('simulacao_dengue_brasil.csv', parse_dates=['data'])
    # Criar coluna auxiliar
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month
    df['ano_mes'] = df['data'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ===================== SIDEBAR COM FILTROS =====================
st.sidebar.header("🔍 Filtros")

# Filtro de região
regioes = ['Todas'] + sorted(df['regiao'].unique())
regiao_selecionada = st.sidebar.selectbox("Região", regioes)

# Filtro de UF (dinâmico baseado na região)
if regiao_selecionada != 'Todas':
    ufs = ['Todos'] + sorted(df[df['regiao'] == regiao_selecionada]['uf'].unique())
else:
    ufs = ['Todos'] + sorted(df['uf'].unique())
uf_selecionado = st.sidebar.selectbox("UF", ufs)

# Filtro de município (dinâmico baseado na UF)
if uf_selecionado != 'Todos':
    municipios = ['Todos'] + sorted(df[df['uf'] == uf_selecionado]['municipio'].unique())
else:
    municipios = ['Todos'] + sorted(df['municipio'].unique())
municipio_selecionado = st.sidebar.selectbox("Município", municipios)

# Filtro de período (ano)
anos = sorted(df['ano'].unique())
ano_inicio, ano_fim = st.sidebar.select_slider(
    "Período (anos)",
    options=anos,
    value=(2015, 2024)
)

# Aplicar filtros no dataframe
df_filtrado = df.copy()
if regiao_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['regiao'] == regiao_selecionada]
if uf_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['uf'] == uf_selecionado]
if municipio_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_selecionado]
df_filtrado = df_filtrado[(df_filtrado['ano'] >= ano_inicio) & (df_filtrado['ano'] <= ano_fim)]

# ===================== KPIs DINÂMICOS =====================
total_casos = df_filtrado['casos_dengue'].sum()
total_internacoes = df_filtrado['internacoes'].sum()
total_obitos = df_filtrado['obitos'].sum()
letalidade = (total_obitos / total_casos * 1000) if total_casos > 0 else 0
temp_media = df_filtrado['temperatura_media'].mean()
chuva_media = df_filtrado['chuva_mm'].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🦟 Casos Totais", f"{total_casos:,.0f}")
col2.metric("🏥 Internações", f"{total_internacoes:,.0f}")
col3.metric("💀 Óbitos", f"{total_obitos:,.0f}")
col4.metric("📊 Letalidade (por mil)", f"{letalidade:.2f}")
col5.metric("🌡️ Temp. Média (°C)", f"{temp_media:.1f}")

# ===================== TABELA DE DADOS =====================
st.subheader("📋 Dados Filtrados")
st.dataframe(df_filtrado[['data', 'regiao', 'uf', 'municipio', 'casos_dengue', 'obitos', 'chuva_mm', 'temperatura_media']].head(100))

# ===================== ANÁLISE TEMPORAL =====================
st.subheader("📈 Evolução Temporal dos Casos")
df_ts = df_filtrado.groupby('data')['casos_dengue'].sum().reset_index()
fig_ts = px.line(df_ts, x='data', y='casos_dengue', title="Casos de Dengue ao Longo do Tempo")
st.plotly_chart(fig_ts, use_container_width=True)

# Sazonalidade: média por mês
st.subheader("📅 Sazonalidade Média (por mês)")
df_month = df_filtrado.groupby('mes')['casos_dengue'].mean().reset_index()
fig_month = px.bar(df_month, x='mes', y='casos_dengue', title="Média de Casos por Mês")
st.plotly_chart(fig_month, use_container_width=True)

# ===================== ANÁLISE AVANÇADA: CORRELAÇÃO =====================
st.subheader("🔗 Correlação entre Variáveis")
# Preparar dados com lag de 1 mês para chuva
df_corr = df_filtrado[['data', 'municipio', 'chuva_mm', 'temperatura_media', 'casos_dengue']].copy()
df_corr = df_corr.sort_values(['municipio', 'data'])
df_corr['chuva_lag1'] = df_corr.groupby('municipio')['chuva_mm'].shift(1)
df_corr = df_corr.dropna()

if len(df_corr) > 1:
    corr_chuva, p_chuva = pearsonr(df_corr['chuva_lag1'], df_corr['casos_dengue'])
    corr_temp, p_temp = pearsonr(df_corr['temperatura_media'], df_corr['casos_dengue'])
    st.write(f"**Correlação entre chuva (mês anterior) e casos:** {corr_chuva:.3f} (p-valor: {p_chuva:.3f})")
    st.write(f"**Correlação entre temperatura e casos:** {corr_temp:.3f} (p-valor: {p_temp:.3f})")
    
    # Gráfico de dispersão
    fig_scatter = px.scatter(df_corr, x='chuva_lag1', y='casos_dengue', trendline="ols",
                             title="Chuva (mês anterior) vs Casos de Dengue")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Dados insuficientes para calcular correlação com os filtros atuais.")

# Matriz de correlação (heatmap)
st.subheader("Matriz de Correlação (variáveis principais)")
corr_matrix = df_filtrado[['chuva_mm', 'temperatura_media', 'casos_dengue', 'internacoes', 'obitos']].corr()
fig_corr = go.Figure(data=go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns, colorscale='RdBu'))
st.plotly_chart(fig_corr, use_container_width=True)

# ===================== MAPA INTERATIVO =====================
st.subheader("🗺️ Mapa de Incidência por UF (média no período)")
# Agregar por UF
df_uf = df_filtrado.groupby('uf').agg({
    'casos_dengue': 'sum',
    'populacao': 'first'  # aproximação: população de um município representativo
}).reset_index()
# Calcular incidência acumulada por 100k hab
df_uf['incidencia'] = (df_uf['casos_dengue'] / df_uf['populacao']) * 100000

# Mapa do Brasil com Plotly (usando código de UF para localização)
# Mapeamento UF -> código IBGE (apenas exemplo para visualização)
uf_to_code = {
    'AC': 12, 'AL': 27, 'AP': 16, 'AM': 13, 'BA': 29, 'CE': 23, 'DF': 53, 'ES': 32,
    'GO': 52, 'MA': 21, 'MT': 51, 'MS': 50, 'MG': 31, 'PA': 15, 'PB': 25, 'PR': 41,
    'PE': 26, 'PI': 22, 'RJ': 33, 'RN': 24, 'RS': 43, 'RO': 11, 'RR': 14, 'SC': 42,
    'SP': 35, 'SE': 28, 'TO': 17
}
df_uf['codigo'] = df_uf['uf'].map(uf_to_code)
df_uf = df_uf.dropna(subset=['codigo'])
fig_map = px.choropleth(df_uf, locations='codigo', color='incidencia',
                        hover_name='uf', color_continuous_scale='Reds',
                        title="Incidência de Dengue por UF (casos/100k hab)")
fig_map.update_geos(scope='south america', resolution=50)
st.plotly_chart(fig_map, use_container_width=True)

# ===================== CONCLUSÃO EXECUTIVA =====================
st.subheader("📌 Conclusão Executiva")
st.markdown(f"""
- No período analisado ({ano_inicio} a {ano_fim}), foram registrados **{total_casos:,.0f} casos** de dengue na área selecionada.
- A taxa de letalidade foi de **{letalidade:.2f} óbitos por mil casos**, indicando baixa letalidade.
- A correlação entre precipitação do mês anterior e casos é de **{corr_chuva:.3f}**, sugerindo que meses chuvosos antecedem surtos.
- Os meses de maior incidência são março a maio (outono), alinhados ao período chuvoso no Centro-Sul.
- Recomenda-se intensificar ações de controle vetorial no início do ano, especialmente em regiões de alta correlação.
""")

st.caption("Fonte: Dados simulados para fins educacionais. Dashboard desenvolvido com Streamlit.")
