import streamlit as st
import pandas as pd
import math
import plotly.express as px

from apps.funcSupport import *
from apps.scalerSupport import *




def app():
    # Set page title
    st.title("Performance Estática | Value")
    st.markdown("""Estudo de **Value & Size factors** considerando os **92 ativos** que compõem o índice **Ibovespa**""")

    # Import data
    ibov = pd.read_csv('portIbov.csv')
    ibovValue = pd.read_csv('portIbov_value.csv')
    ibovValue.dropna()

    # Format
    assets = ibov.empresa.to_list()
    assets.remove('IBOVESPA')
    ibovValue.rename(columns={"Unnamed: 0": "ticket",
                              "lasrPrice": "lastPrice"}, inplace=True)
    ibovValue['name'] = assets
    ibovValue.set_index('ticket', inplace=True)
    
    # Feature engineerng
    ibovValue['priceToBook'] = ibovValue['lastPrice']/ibovValue['bookValue']
    ibovValue['last12mEarnings']  = ibovValue['marketCap']/ibovValue['trailingPE']
    ibovValue['next12mEarnings']  = ibovValue['marketCap']/ibovValue['forwardPE']


    with st.expander('Inputs da estratégia'):
        ######## Sorting by choice ######
        # Fundamentals indicator 
        indic = ['trailingPE','forwardPE','priceToBook', 'marketCap']
        indic_choice = st.selectbox('Selecione o Indicador Fundamentalista', indic)

        # Number of assets
        nAssets = st.slider('Ativos no Portfólio', 1, 92, 4)


        sorted_ibov = ibovValue[ibovValue[indic_choice]>0].sort_values(by=indic_choice).head(nAssets)
        top_list = sorted_ibov.index.to_list()

        st.write(f'Portfólio composto pelos ativos:')
        st.write(f'{sorted_ibov.name.to_list()}')
        st.markdown('---')

        # Layout
        st.write(f'Order ascendente de **{indic_choice}**')
        linhas = math.ceil(nAssets/4)
        for l in range(linhas):
            cols = st.columns(4)
            i=0
            for ativo in sorted_ibov.index[l*4:(l+1)*4]:
                ratio = round(sorted_ibov.loc[ativo][indic_choice],2)
                
                if indic_choice != 'marketCap':
                    cols[i].metric(f'{ativo}', f'{ratio}')
                
                else:
                    ratio = round(ratio/(10**9),2)
                    cols[i].metric(f'{ativo}', f'{ratio} Bi')

                i+=1
    st.markdown("""---""")


    ################################ Set Weights for Strategy portfolio ########################################
    st.subheader(f"""**Backtest do portfólio**""")
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
            for ativo in sorted_ibov.index[l*4:(l+1)*4]:
                value = round(weights_df.T.loc[ativo]['portfolio_%']*100,2)
                cols[i].metric(f'Proporção: {ativo}', f'{value}%')
                i+=1

    with st.expander('Definição do período'):
        # Set backtest period
        slider_fim_m = st.slider('Meses de Backtest:',1, 180, 12)
    
    ########### Set data ##########
    ibov_full = pd.read_csv('histAll.csv')
    ibov_full.set_index('Date', inplace=True)

    # Set backtest period
    slider_fim_d = slider_fim_m * 22

    ibov_full_test = ibov_full.iloc[-slider_fim_d:]
    ibov_full_test.name = 'Ibov historico'

    # Communicate
    st.write(f'Período de backtest | **{ibov_full_test.index[0]} à {ibov_full_test.index[-1]}** | {slider_fim_m} meses')

    
    ############## Backtest viz ####################
    # copy 
    portfolio = ibov_full_test[top_list].copy()

    # add benchmark | Ibov
    portfolio['Benchmark | ^BVSP'] = ibov_full_test['^BVSP']
    portfolio['Portfolio'] = sum([ portfolio[asset]*weights_df.loc['portfolio_%'][asset] for asset in top_list ])
    portComp = portfolio[['Benchmark | ^BVSP', 'Portfolio']]
    portComp.name = 'we'
    portComp = pctChangeScaler(portComp)

    # Set backtest graph
    fig = px.line(
                portComp, 
                x=portComp.index, 
                y=portComp.columns,
                color_discrete_sequence=px.colors.qualitative.Set1, 
                line_dash_sequence=['longdashdot','dash'],
                template="plotly_dark",
                title = 'Ibovespa X Portfólio | AUM de 100 unidades')
                        
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

    
