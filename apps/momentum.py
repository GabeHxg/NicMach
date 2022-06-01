import streamlit as st
import pandas as pd
import plotly.express as px
import math

from apps.funcSupport import *
from apps.scalerSupport import *
from apps.decomposerSupport import *


def app():

    st.title("Performance Estática | Momentum ")

    st.markdown("""Estudo de **Momentum factor** considerando os **92 ativos** que compõem o índice **Ibovespa**""")

    ########### Set data ##########
    ibov_full = pd.read_csv('histAll.csv')
    ibov_full.set_index('Date', inplace=True)

    # Set analysis period
    with st.expander('Inputs da Estratégia'):
        slider_m = st.slider('Meses de análise:', 1, 180, 60)
        slider_d = slider_m * 22

        # Set backtest period
        slider_fim_m = st.slider('Meses de Backtest:', int(slider_m/10), int(slider_m/2), int(slider_m/5))
        slider_fim_d = slider_fim_m * 22

        ibov_full_train = ibov_full.iloc[-slider_d:-slider_fim_d]
        ibov_full_train.name = 'Ibov Selecionado'
        ibov_full_test = ibov_full.iloc[-slider_fim_d:]

        #set numbber of assets
        nAssets = st.slider('Número de ativos no portfolio:', 1, 92, 4)

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


    with st.expander('Métodos de Padronização e Decomposição da ação de preços'):
        scaler = st.selectbox('Selecione o método de padronização', scalers)
        decomposer = st.selectbox('Selecione o método de decomposição', decomposers)
        dec_period = st.slider('Defina o periodo de decomposição | dias', int(slider_d/100), int(slider_d/4),  int(slider_d/4))    

    
    ################################ Shared Stats ########################################
    # Scaler and decomposer
    sca_df = scalers_dict.get(scaler)(ibov_full_train)
    dec_df = decomp_dict.get(decomposer)(sca_df, dec_period)

    # Lista de valorizações 
    growth_lst = []
    # Loop and check 
    for ticket in dec_df:
        p_0 = dec_df[ticket][0]
        p_h = dec_df[ticket][-1]
        per_growth =round(p_h/p_0, 2)
        growth_lst.append(per_growth)
    
    # Momentum dataframe
    ativos = ibov_full.columns.to_list()
    momentum_df = pd.DataFrame(index=ativos)
    momentum_df['multiplicadorPeriodo'] = growth_lst

    # Set winners list
    momentum_topn = momentum_df.sort_values(by='multiplicadorPeriodo', ascending=False).head(nAssets)
    top_list = momentum_topn.index.to_list()
    
    # Viz
    st.subheader(f"""**Histórico tratado de preços**""")
    st.write(f'Período analisado: **{dec_df.index[0]} à {dec_df.index[-1]}** para os {nAssets} ativos de melhor Momentum')

    # Historical price for selected portfolio and visualization
    hist_top = dec_df[top_list]

    fig = px.line(      hist_top, 
                        x=hist_top.index, 
                        y=hist_top.columns,
                        color_discrete_sequence=px.colors.qualitative.Set1, 
                        line_dash_sequence=['longdashdot','dash'],
                        template="plotly_dark")
                        
    st.plotly_chart(fig, use_container_width=True)

    # Layout
    linhas = math.ceil(nAssets/4)
    for l in range(linhas):
        cols = st.columns(4)
        i=0
        for ativo in momentum_topn.index[l*4:(l+1)*4]:
            value = round(momentum_df.loc[ativo].multiplicadorPeriodo,2)
            cols[i].metric(f'Multiplicador: {ativo}', f'X {value}')
            i+=1
   
    st.markdown("""---""")
    ################################ Set Weights for Strategy portfolio ########################################
    st.subheader(f"""**Backtest do portfólio**""")
    st.write(f'Período de backtest: **{ibov_full_test.index[0]} à {ibov_full_test.index[-1]}** | {slider_fim_m} meses')
    weights_df=pd.DataFrame(index=['portfolio_%'])


    with st.expander('Definição dos pesos'):
        equal = st.radio('Portfolio diversificado proporcionalmente?',('Sim', 'Não'))

        if equal == 'Sim':
            w = float(1/nAssets)
            for asset in top_list:
                weights_df[asset] = w
        else:
            rem = 1.0
            for asset in top_list[:-1]:
                w = st.slider(f'% do portfólio para {asset}', 0.0, rem, (rem/2.0))
                weights_df[asset] = w
                rem = rem - w
            weights_df[top_list[-1]] = rem
    
    # Layout
    linhas = math.ceil(nAssets/4)
    for l in range(linhas):
        cols = st.columns(4)
        i=0
        for ativo in momentum_topn.index[l*4:(l+1)*4]:
            value = round(weights_df.T.loc[ativo]['portfolio_%'],2)
            cols[i].metric(f'Proporção: {ativo}', f'{value*100}%')
            i+=1

    # copy 
    portfolio = ibov_full_test[top_list].copy()
    # add benchmark | Ibov
    portfolio['Benchmark | ^BVSP'] = ibov_full_test['^BVSP']
    portfolio['Portfolio'] = sum([ portfolio[asset]*weights_df.loc['portfolio_%'][asset] for asset in top_list ])
    portComp = portfolio[['Benchmark | ^BVSP', 'Portfolio']]
    portComp.name = 'we'
    portComp = scalers_dict.get('Retorno Percentual')(portComp)

    fig = px.line(
                portComp, 
                x=portComp.index, 
                y=portComp.columns,
                color_discrete_sequence=px.colors.qualitative.Set1, 
                line_dash_sequence=['longdashdot','dash'],
                template="plotly_dark",
                title = 'Ibovespa X Portfólio | AUM de 100 unidades' )
                        
    st.plotly_chart(fig, use_container_width=True)

    ##### Metrics | Results #####
    st.write("""<style>[data-testid="stMetricDelta"] svg {display: none;}</style>""",unsafe_allow_html=True,)


    st.subheader('Performance | índice Ibovespa X Portfólio')
    cols = st.columns(3)

    vals = []
    for i in range(len(portComp.columns)):
        atv   = portComp.columns[i]
        inic  = portComp[atv][0]
        final = portComp[atv][-1]
        val   = ((final/inic) - 1)*100
        mult  = round((final/inic),2)
        vals.append(val)
        if mult > 1:
            cols[i].metric(f'Valorização do {atv}', 
                           f'{round(val, 2)}%',
                           f'Multiplicador:{mult}X')
        else:
            cols[i].metric(f'Valorização do {atv}', 
                           f'{round(val, 2)}%',
                           f'Multiplicador: {mult}X', delta_color='inverse')

    ib_growth = vals[0]
    port_growth = vals[1]
    perf_dif = round(port_growth - ib_growth,2)
    perf_rel = round(port_growth/ib_growth,2)

    if perf_dif > 0:
        cols[2].metric('Diferença absoluta de %', 
                      f'{perf_dif}%', 
                      f'Performance relativa: {abs(perf_rel)} X')
    else:
        cols[2].metric('Diferença absoluta de %', 
                      f'{perf_dif}%', 
                      f'Performance relativa: {abs(perf_rel)} X', delta_color='inverse' )


