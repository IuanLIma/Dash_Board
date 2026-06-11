import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title='DashBoard de Salários',
    page_icon= '📊',
    layout = 'wide'  
)

#carregando os dados
df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv')

#criando a barra de filtros ao lado da pagina
st.sidebar.header('Filtros')

#Criando filtros-
anos= sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano',anos,default= anos)

#filtro de senioridade
senioridade= sorted(df['senioridade'].unique())
senioridade_selecionada= st.sidebar.multiselect('Senioridade',senioridade, default=senioridade)

#filtro de contratos
contratos= sorted(df['contrato'].unique())
contratos_selecionado= st.sidebar.multiselect('Contrato',contratos,default=contratos)

#filtro de tamanho de empresa
tamanho= sorted(df['tamanho_empresa'].unique())
tamanho_selecionado= st.sidebar.multiselect('Tamanho da empresa',tamanho, default=tamanho)

df_filtrado= df[
    (df['ano'].isin(anos_selecionados))&
    (df['senioridade'].isin(senioridade_selecionada))&
    (df['contrato'].isin(contratos_selecionado))&
    (df['tamanho_empresa'].isin(tamanho_selecionado))
]

#criação da pagina com titulo e subtitulo
st.title('-Analise de Salarios-')
st.markdown('Explore os salarios na area de dados nos ultimos anos')

#criando as medias do dash para entendimento
st.subheader('Metricas Principais (Salario em USD)')

if not df_filtrado.empty:
    salario_media = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    Salario_minimo = df_filtrado['usd'].min()
    Total_registros = df_filtrado.shape[0]
    #pega quantidades de linha começando do 0
    Cargo_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_maximo,salario_media,Salario_minimo,Total_registros,Cargo_frequente= 0,0,0,0,''
    
col1,col2,col3,col4,col5 = st.columns(5)
col1.metric('Salario medio', f'${salario_media:,.0f}')
col2.metric('Salario maximo', f'${salario_maximo:,.0f}')
col3.metric('Salario minimo', f'${Salario_minimo:,.0f}')
col4.metric('Total de registros', f'{Total_registros:,}')
col5.metric('Cargo mais frequente', Cargo_frequente)
st.markdown('----')

#area dos graficos

st.subheader('Graficos')
col_graf1, col_graf2 = st.columns(2)

#criando um grafico de barra para o top 10 cargos com maiores medias salariais 
with col_graf1:
    if not df_filtrado.empty:
        top_cargos= df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation= 'h' ,
            title='Top 10 cargos por salario medio',
            labels= {'usd':'Media de Salario Anual', 'cargo':'cargo'}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos,width="stretch")
    else:
        st.warning('Nenhum dado para exibir no gráfico de cargos')
    

with col_graf2:
    if not df_filtrado.empty:
        graf_hist=px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title= 'Distribuição de salarios anuais',
            labels={'usd':'Faixa salarial(USD)','count':''}
        )
        graf_hist.update_layout(title_x=0.1)
        st.plotly_chart(graf_hist,width="stretch")
    else:
        st.warning('Nenhum dado para exibir no gráfico de distribuição')
        
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5  
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, width="stretch")
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        #filtrando só o data science da tabela de cargos
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, width="stretch")
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.") 

#Tabela de Dados Detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
#mostra o df no final do dash board