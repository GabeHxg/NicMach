import streamlit as st
import pandas as pd
import plotly.express as px

from apps.funcSupport import *
from apps.scalerSupport import *
from apps.decomposerSupport import *


def app():

    st.title("Yahoo API Live Connection")

    st.markdown('**Estudo considerando as 92 empresas que compõem o índice Ibovespa**')
    ########### Set data ##########
    ibov_full = pd.read_csv('portIbov.csv')
    ibov_full.set_index(ibov_full.empresa, inplace=True)
    ibov_full.drop(columns=('empresa'),inplace=True)
    
    # set ticket dropdown list 
    empresas = ibov_full.index.to_list()

    with st.expander('Selecione as empresas e o período para análise'):
        port = st.multiselect('Códigos', empresas, 'IBOVESPA')
        # Set analysis period
        slider = st.slider('Dias de análise:', 1, 7000, 7000)
    
    # set df 
    chosen_port = ibov_full.loc[port]
    chosen_port.name = port

    ### Set chosen DataFrame
    port_hist = get_hist(chosen_port, slider) 
    

    ################## Create selection with type of scaler #######
    scalers_dict    = {
                'Observado':observed,
                'Retorno Percentual': pctChangeScaler,
                'Metcalfe Scale' :logScaler,
                'Standard Scale': standardScaler,
                'MinMax Scale': mmScaler,
                'Robust Scale': rbstScaler
                }
    scalers = [i for i in scalers_dict]

    ################## Create selection with type of Decomposer and Period#######
    decomp_dict    = {
                'Observado':Observed,
                'Tendência' :Trend,
                'Sazonalidade': Seasonal,
                'Resíduo': Resid
                }   
    decomposers = [i for i in decomp_dict]

    with st.expander('Condições de padronização e decomposição do histórico de preços'):
        scaler = st.selectbox('Selecione o método de padronização', scalers)
        decomposer = st.selectbox('Selecione o método de decomposição', decomposers)
        dec_period = st.slider('Defina o periodo de decomposição | dias', int(slider/100), int(slider/4), 365)    

    # NULL handling 
    if len(port_hist) > 0:
        df = port_hist.copy()
    else:
        st.write('Por favor, selecione os ativos.')
        st.stop()

    # NULL handling
    df.name = port_hist.name
    for t in df.columns.to_list():
        no_nulls = df[t].dropna()
        first_value = no_nulls[0]
        df[t].fillna(first_value, inplace = True)
    

    ################################ Shared Graph ########################################
    
    # Scaler and decomposer
    sca_df = scalers_dict.get(scaler)(df)
    dec_df = decomp_dict.get(decomposer)(sca_df, dec_period)

    st.subheader('Visualização de Momentum')
    fig = px.line(dec_df, 
                        x=dec_df.index, 
                        y=dec_df.columns,
                        color_discrete_sequence=px.colors.qualitative.Set1, 
                        line_dash_sequence=['longdashdot','dash'],
                        template="plotly_dark")
                        
    st.plotly_chart(fig, use_container_width=True)
    
   

    
    



 