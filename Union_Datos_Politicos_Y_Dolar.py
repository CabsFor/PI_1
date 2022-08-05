import pandas as pd
import streamlit as st
import altair as alt
import aiohttp
import asyncio
import json

# Utilice la libreria streamlit para juntar los datos del dolar y los eventos importantes en un solo grafico, se necesita ambiente virtual configurado para
# su correcta ejecucion, entrar a https://cabsfor-pi-pianalisis-y9j89u.streamlitapp.com/ para ver el resultado final

# Tipo de pagina para que ocupe la mayoria de la hoja y titulo de la pestana
st.set_page_config(layout="wide", page_title="Dolar Blue vs Dolar Oficial")

# Declaracion de endpoints,tokens, llamadas a api, transformacion a Json y Transformacion a Dataframe

#Limpieza, combinacion y transformacion de dataframes 

Blue = pd.read_csv('Dolar_Blue.csv')
Oficial = pd.read_csv('Dolar_Oficial.csv')
df = pd.merge(Blue,Oficial[['v','d']], on='d',how='left')
df.dropna(inplace=True)
df['d'] = pd.to_datetime(df['d'])
df.rename(columns={'d':'Fecha','v_x':'Dolar_Blue', 'v_y':'Dolar_Oficial'},inplace=True)

Blue = pd.read_csv('Dolar_Blue.csv')
Oficial = pd.read_csv('Dolar_Oficial.csv')
df1 = pd.merge(Blue,Oficial[['v','d']], on='d',how='left')
df1.dropna(inplace=True)
df1['d'] = pd.to_datetime(df1['d'])
df1.rename(columns={'d':'Fecha','v_x':'Dolar_Blue', 'v_y':'Dolar_Oficial'},inplace=True)

# Parte importante, para usar streamlit lo mas recomendable es hacer un reformateo a el dataframe para que las columnas
# se conviertan en filas y adopten los valores que tenian anteriormente, revisar funcion melt de pandas
df = df.melt(id_vars=['Fecha'],value_vars=['Dolar_Blue','Dolar_Oficial'])

col1, col2, col3 = st.columns(3)

# Metricas para mostrar
with col1:
    st.subheader("Maximo Historico Dolar Blue")
    st.caption(str(df1[df1['Dolar_Blue'] == df1['Dolar_Blue'].max()].Fecha.values[0]).split('T')[0])
    st.caption(df1.Dolar_Blue.max())
    st.subheader("Minimo Historico Dolar Blue")
    st.caption(str(df1[df1['Dolar_Blue'] == df1['Dolar_Blue'].min()].Fecha.values[0]).split('T')[0])
    st.caption(df1.Dolar_Blue.min())
    

with col2:
    st.subheader("Maximo Historico Dolar Oficial")
    st.caption(str(df1[df1['Dolar_Oficial'] == df1['Dolar_Oficial'].min()].Fecha.values[0]).split('T')[0])
    st.caption(df1.Dolar_Oficial.max())
    st.subheader("Minimo Historico Dolar Oficial")
    st.caption(str(df1[df1['Dolar_Oficial'] == df1['Dolar_Oficial'].min()].Fecha.values[0]).split('T')[0])
    st.caption(df1.Dolar_Oficial.min())

with col3:
    st.subheader("Promedio Historico Dolar Blue")
    st.caption(df1.Dolar_Blue.mean())
    st.subheader("Promedio Historico Dolar Oficial")
    st.caption(df1.Dolar_Oficial.mean())



# Funcion para transformar valores de df a el grafico que necesitamos: ADAPTADO A DF CREADO
def get_chart(df):
    # Activar casilla de informacion cuando ponemos el mouse sobre las lineas
    hover = alt.selection_single(
        fields=["Fecha"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    # Declaracion de variables de lineplot, x= Fecha, y = valores de dolar, variables = dolar blue, dolar oficial
    lines = (
        alt.Chart(df, title="Dolar Blue vs Dolar Oficial")
        .mark_line()
        .encode(
            x="Fecha",
            y='value',
            color='variable'
        )
    )

    # Dibuja puntos en las graficas cuando el mouse pasa encima de las lineas
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Informacion de casilla en accion hover:mouse encima de grafico
    tooltips = (
        alt.Chart(df)
        .mark_rule()
        .encode(
            x="yearmonthdate(Fecha)",
            y="value",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Fecha", title="Fecha"),
                alt.Tooltip("value", title="Precio (Pesos ARG)"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

# Definimos el grafico con la informacion de la funcion
chart = get_chart(df)


# Creacion, transformacion y limpieza de dataframe con Eventos importantes
Marcadores = pd.read_csv('Eventos.csv')
Marcadores.rename(columns={'d':'Fecha','e':'Evento','t':'Tipo_Evento'}, inplace=True)
Marcadores.Fecha = pd.to_datetime(Marcadores.Fecha)
Marcadores = Marcadores[Marcadores['Fecha'].dt.year > 2002]
Marcadores["y"] = 10 # <------------ declaramos y para usarla mas adelante como altura en el eje y de marcadores mas adelante


annotation_layer = (
    alt.Chart(Marcadores)
    .mark_text(size=15, text="ℹ️", dx=-8, dy=-10, align="left") # <-------------------- Declaracion de tipo, tamano, y posicion de marcadores
    .encode(
        x="Fecha:T",
        y=alt.Y("y:Q"),
        tooltip=[ 
            alt.Tooltip("Fecha", title="Fecha"),                 #<----------------
            alt.Tooltip("Evento", title="Evento"),               #<----------------  Informacion de casilla en accion hover:mouse encima de marcadores
            alt.Tooltip("Tipo_Evento", title="Tipo de Evento"),  #<----------------
            ],
    )
    .interactive()
)


# Union de Grafico y marcadores
st.altair_chart(
    (chart + annotation_layer).interactive(),  #<---------------- interactive() con esta funcion podemos hacer Zoom in y Zoom out sobre el grafico
    use_container_width=True
)
