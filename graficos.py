# ==========================================
# 8. Geração de Gráficos
# ==========================================

# Estilo profissional
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# --- Gráfico 1: Evolução Temporal (Série Histórica) ---
plt.figure(figsize=(14, 6))
casos_serie = df.groupby('data')['casos_dengue'].sum()
plt.plot(casos_serie.index, casos_serie.values, color='darkred', linewidth=2)
plt.title('Evolução dos Casos de Dengue no Brasil (2015-2024)', fontsize=16)
plt.xlabel('Ano')
plt.ylabel('Número de Casos')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Gráfico 2: Sazonalidade (Média de Casos por Mês) ---
plt.figure(figsize=(12, 5))
media_mensal = df.groupby(df['data'].dt.month)['casos_dengue'].mean()
sns.barplot(x=media_mensal.index, y=media_mensal.values, palette='Reds_r')
plt.title('Média de Casos por Mês (Sazonalidade)', fontsize=16)
plt.xlabel('Mês')
plt.ylabel('Média de Casos')
plt.xticks(ticks=range(12), labels=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'])
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()

# --- Gráfico 3: Boxplot por Região (Distribuição) ---
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x='regiao', y='casos_dengue', palette='Set3')
plt.title('Distribuição de Casos por Região', fontsize=16)
plt.xlabel('Região')
plt.ylabel('Casos de Dengue')
plt.yscale('log')  # Escala log para melhor visualização devido à amplitude dos dados
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()

# --- Gráfico 4: Dispersão (Chuva com Lag vs Casos) + Regressão ---
plt.figure(figsize=(10, 6))
sns.regplot(data=df_lag, x='chuva_lag1', y='casos_dengue', 
            scatter_kws={'alpha':0.3, 'color':'blue'}, 
            line_kws={'color':'red'})
plt.title('Relação entre Chuva do Mês Anterior e Casos de Dengue', fontsize=14)
plt.xlabel('Chuva no mês anterior (mm)')
plt.ylabel('Casos de Dengue')
plt.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()

# --- Gráfico 5: Matriz de Correlação (Heatmap) ---
plt.figure(figsize=(8, 6))
cols_corr = ['chuva_mm', 'temperatura_media', 'casos_dengue', 'internacoes', 'obitos']
corr_matrix = df[cols_corr].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', linewidths=0.5)
plt.title('Matriz de Correlação entre Variáveis', fontsize=14)
plt.tight_layout()
plt.show()

# --- Gráfico 6: Top 10 UFs com maior incidência média ---
incidencia_uf = df.groupby('uf')['incidencia_100k'].mean().sort_values(ascending=False).head(10)
plt.figure(figsize=(12, 5))
sns.barplot(x=incidencia_uf.values, y=incidencia_uf.index, palette='viridis')
plt.title('Top 10 UFs com Maior Incidência Média (por 100k hab)', fontsize=14)
plt.xlabel('Incidência Média')
plt.ylabel('UF')
plt.tight_layout()
plt.show()