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
st.title("Análisis de Egresos Hospitalarios Uruguay")
st.markdown("Exploración interactiva de datos hospitalarios 2021-2024")

# Sidebar
st.sidebar.markdown("## Filtros")
st.sidebar.markdown("Usá los filtros para explorar los datos")

# Filtro por año con slider
anio_min = int(df['AÑO'].min())
anio_max = int(df['AÑO'].max())

anio_rango = st.sidebar.slider(
    "Seleccioná el rango de años",
    min_value=anio_min,
    max_value=anio_max,
    value=(anio_min, anio_max)
)

# Aplicar filtro al dataframe
df_filtrado = df[df['AÑO'].between(anio_rango[0], anio_rango[1])]

st.markdown(f"**Registros seleccionados: {len(df_filtrado):,}**")

# Resumen descriptivo
st.markdown("## Resumen Descriptivo")

# Agrupamos por año para obtener cantidad de egresos
egresos_por_anio = df_filtrado.groupby('AÑO').size()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total registros", f"{len(df_filtrado):,}")
    st.metric("Media de egresos", f"{egresos_por_anio.mean():,.0f}")

with col2:
    st.metric("Mediana de egresos", f"{egresos_por_anio.median():,.0f}")
    st.metric("Desvío estándar", f"{egresos_por_anio.std():,.0f}")

with col3:
    st.metric("Rango", f"{egresos_por_anio.max() - egresos_por_anio.min():,}")
    st.metric("Mínimo de egresos", f"{egresos_por_anio.min():,}")

st.markdown("### Estadísticas por año")
st.dataframe(df_filtrado.groupby('AÑO').size().reset_index(name='Egresos'))

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

# Gráfico de dispersión
st.markdown("### Relación entre Región y Egresos por Año")

egresos_region = df_filtrado.groupby(['AÑO', 'REGION']).size().reset_index(name='Egresos')

fig2, ax2 = plt.subplots(figsize=(10, 5))

fig2.patch.set_facecolor('black')
ax2.set_facecolor('black')

regiones = egresos_region['REGION'].unique()
colores = ['red', 'cyan', 'yellow', 'lime']

for region, color in zip(regiones, colores):
    datos = egresos_region[egresos_region['REGION'] == region]
    ax2.scatter(datos['AÑO'], datos['Egresos'], label=region, color=color, s=100)

ax2.set_title("Egresos por Región y Año", fontsize=16, color='white')
ax2.set_xlabel("Año", fontsize=12, color='white')
ax2.set_ylabel("Cantidad de Egresos", fontsize=12, color='white')
ax2.tick_params(axis='x', colors='white')
ax2.tick_params(axis='y', colors='white')
ax2.spines['bottom'].set_color('white')
ax2.spines['left'].set_color('white')
ax2.spines['top'].set_color('white')
ax2.spines['right'].set_color('white')
ax2.legend(facecolor='black', labelcolor='white')

ax2.set_xticks([2021, 2022, 2023, 2024])
ax2.set_xticklabels(['2021', '2022', '2023', '2024'], color='white')

st.pyplot(fig2)

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

