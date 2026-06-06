import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Carga de datos
base_dir = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(base_dir, 'data', 'processed', 'egresos_hospitalarios_limpio.csv')
df = pd.read_csv(ruta, sep=';')

# Título principal
st.title("Egresos Hospitalarios Uruguay")
st.markdown("Exploración interactiva de datos hospitalarios 2021-2024")

# Sidebar
st.sidebar.markdown("## Filtros")

# Filtro por año con slider
anio_min = int(df['AÑO'].min())
anio_max = int(df['AÑO'].max())

anio_rango = st.sidebar.slider(
    "Seleccioná el rango de años",
    min_value=anio_min,
    max_value=anio_max,
    value=(anio_min, anio_max)
)

# Filtro de género
generos = ['Todos'] + sorted(df['GENERO'].unique().tolist())
genero_sel = st.sidebar.selectbox("Seleccioná el género", generos)

# Filtro de grupo etario
grupos = ['Todos'] + sorted(df['GRUPO ETAREO'].unique().tolist())
grupo_sel = st.sidebar.selectbox("Seleccioná el grupo etario", grupos)

# Filtro de causa externa
causas = ['Todos'] + sorted(df['CAUSA EXTERNA'].unique().tolist())
causa_sel = st.sidebar.selectbox("Seleccioná la causa externa", causas)

# Aplicar todos los filtros
df_filtrado = df[df['AÑO'].between(anio_rango[0], anio_rango[1])]

if genero_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['GENERO'] == genero_sel]

if grupo_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['GRUPO ETAREO'] == grupo_sel]

if causa_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['CAUSA EXTERNA'] == causa_sel]

st.markdown(f"**Registros seleccionados: {len(df_filtrado):,}**")

# Resumen descriptivo
st.markdown("## Resumen Descriptivo")

egresos_por_anio = df_filtrado.groupby('AÑO').size()
egresos_montevideo = len(df_filtrado[df_filtrado['REGION'] == 'MONTEVIDEO'])
egresos_interior = len(df_filtrado[df_filtrado['REGION'] == 'INTERIOR'])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total registros", f"{len(df_filtrado):,}")

with col2:
    st.metric("Egresos Montevideo", f"{egresos_montevideo:,}")

with col3:
    st.metric("Egresos Interior", f"{egresos_interior:,}")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Media de egresos", f"{egresos_por_anio.mean():,.0f}")

with col5:
    st.metric("Mediana de egresos", f"{egresos_por_anio.median():,.0f}")

with col6:
    st.metric("Desvío estándar", f"{egresos_por_anio.std():,.0f}")

st.markdown("### Estadísticas por año")
tabla = df_filtrado.groupby('AÑO').size().reset_index(name='Egresos')
tabla['Egresos'] = tabla['Egresos'].apply(lambda x: f'{x:,}')
st.dataframe(tabla, hide_index=True)

# Gráfico de distribución
st.markdown("### Distribución de Egresos por Año")

egresos_region_anio = df_filtrado[df_filtrado['REGION'].isin(['INTERIOR', 'MONTEVIDEO'])]
egresos_agrupado = egresos_region_anio.groupby(['AÑO', 'REGION']).size().reset_index(name='Egresos')

fig, ax = plt.subplots(figsize=(10, 5))

fig.patch.set_facecolor('black')
ax.set_facecolor('black')

regiones = ['INTERIOR', 'MONTEVIDEO']
colores = ['cyan', 'red']
anios = sorted(egresos_agrupado['AÑO'].unique())
x = range(len(anios))
ancho = 0.35

for i, (region, color) in enumerate(zip(regiones, colores)):
    datos = egresos_agrupado[egresos_agrupado['REGION'] == region]
    valores = [datos[datos['AÑO'] == a]['Egresos'].values[0] if a in datos['AÑO'].values else 0 for a in anios]
    posiciones = [xi + i * ancho for xi in x]
    ax.bar(posiciones, valores, width=ancho, label=region, color=color, edgecolor=color)

ax.set_title("Egresos por Año — Interior vs Montevideo", fontsize=16, color='white')
ax.set_xlabel("Año", fontsize=12, color='white')
ax.set_ylabel("Cantidad de Egresos", fontsize=12, color='white')
ax.set_xticks([xi + ancho / 2 for xi in x])
ax.set_xticklabels(anios, color='white')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{int(val):,}'))
ax.tick_params(axis='y', colors='white')
ax.spines['bottom'].set_color('white')
ax.spines['left'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['right'].set_color('white')
ax.legend(facecolor='black', labelcolor='white')

st.pyplot(fig)

# Gráfico Público vs Privado

st.markdown("### Egresos por Sector")
egresos_sector = df.groupby(['AÑO', 'SECTOR']).size().reset_index(name='Egresos')

fig_sector, ax_sector = plt.subplots(figsize=(10, 5))
fig_sector.patch.set_facecolor('black')
ax_sector.set_facecolor('black')

for sector, color in zip(['PRIVADO', 'PUBLICO'], ['orange', 'lime']):
    datos = egresos_sector[egresos_sector['SECTOR'] == sector]
    ax_sector.plot(datos['AÑO'], datos['Egresos'], marker='o', label=sector, color=color, linewidth=2)

ax_sector.set_title("Público vs Privado", fontsize=13, color='white')
ax_sector.set_xlabel("Año", fontsize=10, color='white')
ax_sector.set_ylabel("Egresos", fontsize=10, color='white')
ax_sector.set_xticks([2021, 2022, 2023, 2024])
ax_sector.set_xticklabels(['2021', '2022', '2023', '2024'], color='white')
ax_sector.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{int(val):,}'))
ax_sector.tick_params(axis='y', colors='white')
ax_sector.spines['bottom'].set_color('white')
ax_sector.spines['left'].set_color('white')
ax_sector.spines['top'].set_color('white')
ax_sector.spines['right'].set_color('white')
ax_sector.legend(facecolor='black', labelcolor='white')
st.pyplot(fig_sector)

# Gráfico de Dispersión
st.markdown("## Relación Egresos Montevideo vs Interior por Grupo Etario")

egresos_mv = df_filtrado[df_filtrado['REGION'] == 'MONTEVIDEO'].groupby(['AÑO', 'GRUPO ETAREO']).size().reset_index(name='Egresos_MV')
egresos_int = df_filtrado[df_filtrado['REGION'] == 'INTERIOR'].groupby(['AÑO', 'GRUPO ETAREO']).size().reset_index(name='Egresos_INT')

df_cruce = pd.merge(egresos_mv, egresos_int, on=['AÑO', 'GRUPO ETAREO'])

fig_scatter, ax_scatter = plt.subplots(figsize=(10, 6))
fig_scatter.patch.set_facecolor('black')
ax_scatter.set_facecolor('black')

grupos = df_cruce['GRUPO ETAREO'].unique()
colores_scatter = ['red', 'cyan', 'yellow', 'lime', 'orange', 'hotpink', 'dodgerblue', 'white', 'violet', 'gold']

for grupo, color in zip(grupos, colores_scatter):
    datos = df_cruce[df_cruce['GRUPO ETAREO'] == grupo]
    ax_scatter.scatter(datos['Egresos_MV'], datos['Egresos_INT'], label=grupo, color=color, s=120)

ax_scatter.set_title("Egresos Montevideo vs Interior por Grupo Etario", fontsize=13, color='white')
ax_scatter.set_xlabel("Egresos Montevideo", fontsize=10, color='white')
ax_scatter.set_ylabel("Egresos Interior", fontsize=10, color='white')
ax_scatter.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{int(val):,}'))
ax_scatter.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'{int(val):,}'))
ax_scatter.tick_params(axis='x', colors='white')
ax_scatter.tick_params(axis='y', colors='white')
ax_scatter.spines['bottom'].set_color('white')
ax_scatter.spines['left'].set_color('white')
ax_scatter.spines['top'].set_color('white')
ax_scatter.spines['right'].set_color('white')
ax_scatter.legend(facecolor='black', labelcolor='white', fontsize=8)

plt.tight_layout()
st.pyplot(fig_scatter)

# Mapa geográfico
st.markdown("### Distribución Geográfica de Egresos")

import plotly.express as px

egresos_mapa = df_filtrado.groupby('REGION').size().reset_index(name='Egresos')

# Coordenadas aproximadas de cada región de Uruguay
coordenadas = {
    'MONTEVIDEO': {'lat': -34.9011, 'lon': -56.1645},
    'INTERIOR':   {'lat': -32.5228, 'lon': -55.7658},
    'EXTERIOR':   {'lat': -34.0,   'lon': -60.0},
    'Sin datos':  {'lat': -33.0,   'lon': -57.0}
}

egresos_mapa['lat'] = egresos_mapa['REGION'].map(lambda r: coordenadas[r]['lat'])
egresos_mapa['lon'] = egresos_mapa['REGION'].map(lambda r: coordenadas[r]['lon'])

fig3 = px.scatter_mapbox(
    egresos_mapa,
    lat='lat',
    lon='lon',
    size='Egresos',
    color='REGION',
    hover_name='REGION',
    hover_data={'Egresos': True, 'lat': False, 'lon': False},
    title='Egresos por Región',
    size_max=60,
    zoom=6,
    center={"lat": -32.5, "lon": -56.0},
    mapbox_style="carto-darkmatter"
)

fig3.update_layout(height=600, template='plotly_dark')
st.plotly_chart(fig3, use_container_width=True)

