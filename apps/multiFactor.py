import streamlit as st
import pandas as pd
import math
import plotly.express as px

from apps.funcSupport import *
from apps.scalerSupport import *
from apps.decomposerSupport import *



def app():
    # Set page title
    st.title("Estratégia Multi Fatores")
    st.markdown('Composição de estratégia usando os fatores **Size, Value e Momentum** e os 92 ativos que compõem o **Ibovespa**')
    st.markdown(' ')
    ##### Value & Size ######
    

    # Import data
    ibov = pd.read_csv('portIbov.csv')
    ibovValue = pd.read_csv('portIbov_value.csv')

    # Format
    assets = ibov.empresa.to_list()
    assets.remove('IBOVESPA')
    ibovValue.rename(columns={"Unnamed: 0": "ticket",
                              "lasrPrice": "lastPrice"}, inplace=True)
    ibovValue['name'] = assets
    ibovValue.set_index('ticket', inplace=True)
    ibovValue['marketCap'] = ibovValue['marketCap']/(10**9)
    
    # Feature engineerng
    ibovValue['priceToBook'] = ibovValue['lastPrice']/ibovValue['bookValue']
    ibovValue['last12mEarnings']  = ibovValue['marketCap']/ibovValue['trailingPE']
    ibovValue['next12mEarnings']  = ibovValue['marketCap']/ibovValue['forwardPE']

    ######## Sorting by choice ######
    st.sidebar.subheader('Composição da carteira')
    with st.sidebar.expander('Portfólio'):
        #set numbber of assets
        nAssets = st.slider('Número de ativos', 1, 92, 4)

    # Fundamentals filters 
    with st.sidebar.expander('Size Analysis'):
        # market cap
        mcMin = math.floor(min(ibovValue['marketCap']))
        mcMax = math.ceil(max(ibovValue['marketCap']))
        mcMean = int(ibovValue['marketCap'].mean())
        mcRange = st.slider('Máxima Capitalização de Mercado | Bilhões R$', mcMin, mcMax, mcMax, step = 5)

    with st.sidebar.expander('Value Analysis'):
        # trailing PE 
        tpeMin = math.floor(min(ibovValue['trailingPE']))
        tpeMax = math.ceil(max(ibovValue['trailingPE']))
        tpeMean = int(ibovValue['trailingPE'].mean())
        tpeStd = ibovValue['trailingPE'].std()
        slider_max = math.ceil(tpeMean + 1*tpeStd)
        tpeRange = st.slider('Trailing Price-To-Earnings', 0, slider_max, (0, tpeMean))

        # forward PE 
        fpeMin = math.floor(min(ibovValue['forwardPE']))
        fpeMax = math.ceil(max(ibovValue['forwardPE']))
        fpeMean = int(ibovValue['forwardPE'].mean())
        fpeStd = ibovValue['forwardPE'].std()
        fpeRange = st.slider('Forward Price-To-Earnings', 0, int(fpeMean+2*fpeStd), (0, fpeMean))

        # Price to Book 
        ptbMin = math.floor(min(ibovValue['priceToBook']))
        ptbMax = math.ceil(max(ibovValue['priceToBook']))
        ptbMean = int(ibovValue['priceToBook'].mean())
        ptbRange = st.slider('Price-To-Book', 0, ptbMax, (0, ptbMean))

    filtered_ibov = ibovValue[
            # filter marcap
            (ibovValue['marketCap'] <= mcRange) &
            # filter Trailing PE
            (ibovValue['trailingPE'] >= tpeRange[0]) & (ibovValue['trailingPE'] <= tpeRange[1]) &
            # filter Forward PE
            (ibovValue['forwardPE'] >= fpeRange[0]) & (ibovValue['forwardPE'] <= fpeRange[1]) &
            # filter Price to Book
            (ibovValue['priceToBook'] >= ptbRange[0]) & (ibovValue['priceToBook'] <= ptbRange[1])
            ]  

    with st.expander('Ativos Resultantes | Value & Size Strategy'):
        st.write(f'{filtered_ibov.name.to_list()}')
    
    st.sidebar.markdown("""---""")

    ########################## Momentum #################################
    st.sidebar.subheader('Momentum analysis')

    ########### Set data ##########
    ibov_full = pd.read_csv('histAll.csv')
    ibov_full.set_index('Date', inplace=True)

    selected_assets = filtered_ibov.index.to_list()
    selected_assets.append('^BVSP')
    ibov_full_selected = ibov_full[selected_assets]

    # Set analysis period
    with st.sidebar.expander('Período de análise e de backtest'):
        slider_m = st.slider('Meses de análise:', 1, 180, 60)
        slider_d = slider_m * 22

        # Set backtest period
        slider_fim_m = st.slider('Meses de Backtest:', int(slider_m/10), int(slider_m/2), int(slider_m/5))
        slider_fim_d = slider_fim_m * 22

        ibov_sel_train = ibov_full_selected.iloc[-slider_d:-slider_fim_d]
        ibov_sel_train.name = 'Ibov Selecionado'
        ibov_sel_test = ibov_full_selected.iloc[-slider_fim_d:]


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

    with st.sidebar.expander('Momentum Analysis'):
        scaler = st.selectbox('Selecione o método de padronização', scalers)
        decomposer = st.selectbox('Selecione o método de decomposição', decomposers)
        dec_period = st.slider('Defina o periodo de decomposição | dias', int(slider_d/100), int(slider_d/4),  int(slider_d/4))    

    
    ################################ Shared Stats ########################################
    # Scaler and decomposer
    sca_df = scalers_dict.get(scaler)(ibov_sel_train)
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
    momentum_df = pd.DataFrame(index=selected_assets)
    momentum_df['multiplicadorPeriodo'] = growth_lst

    st.write(f'Portfólio | período analisado: **{dec_df.index[0]} à {dec_df.index[-1]}**')
    ######################################################################################################
    
    # joined df 
    joined = filtered_ibov.join(momentum_df, how = 'left')
    joined_sorted_top = joined.sort_values(by='multiplicadorPeriodo', ascending = False).head(nAssets)

    # Historical price for selected portfolio and visualization 
    top_assets = joined_sorted_top.index.to_list()
    hist_top = dec_df[top_assets]
    fig = px.line(      hist_top, 
                        x=hist_top.index, 
                        y=hist_top.columns,
                        color_discrete_sequence=px.colors.qualitative.Set1, 
                        line_dash_sequence=['longdashdot','dash'],
                        template="plotly_dark")
                        
    st.plotly_chart(fig, use_container_width=True)

    # Layout
    with st.expander('Múltiplos no período'):
        linhas = math.ceil(nAssets/4)
        for l in range(linhas):
            cols = st.columns(4)
            i=0
            for ativo in joined_sorted_top.index[l*4:(l+1)*4]:
                value = round(momentum_df.loc[ativo].multiplicadorPeriodo,2)
                cols[i].metric(f'Multiplicador: {ativo}', f'X {value}')
                i+=1
    
    with st.expander('Indicadores do portfólio'):
        st.write(f'Portfólio Composto por: {joined_sorted_top.name.to_list()}')
        st.dataframe(joined_sorted_top)
   
    st.markdown("""---""")

    ################################ Set Weights for Strategy portfolio ########################################
    st.subheader(f"""**Backtest do portfólio**""")
    weights_df=pd.DataFrame(index=['portfolio_%'])
    st.write(f'Período de backtest: **{ibov_sel_test.index[0]} à {ibov_sel_test.index[-1]}** | {slider_fim_m} meses')



    with st.expander('Definição dos pesos'):
        equal = st.radio('Portfolio diversificado proporcionalmente?',('Sim', 'Não'))

        if equal == 'Sim':
            w = float(1/nAssets)
            for asset in top_assets:
                weights_df[asset] = w
        else:
            rem = 1.0
            for asset in top_assets[:-1]:
                w = st.slider(f'% do portfólio para {asset}', 0.0, rem, (rem/2.0))
                weights_df[asset] = w
                rem = rem - w
            weights_df[top_assets[-1]] = rem
    
    # Layout
    with st.expander('Distribuição da Carteira'):
        linhas = math.ceil(nAssets/4)
        for l in range(linhas):
            cols = st.columns(4)
            i=0
            for ativo in joined_sorted_top.index[l*4:(l+1)*4]:
                value = round(weights_df.T.loc[ativo]['portfolio_%']*100,2)
                cols[i].metric(f'Proporção: {ativo}', f'{value}%')
                i+=1

    # copy 
    portfolio = ibov_sel_test[top_assets].copy()
    # add benchmark | Ibov
    portfolio['Benchmark | ^BVSP'] = ibov_sel_test['^BVSP']
    portfolio['Portfolio'] = sum([ portfolio[asset]*weights_df.loc['portfolio_%'][asset] for asset in top_assets ])
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
        if perf_rel > 1:
            cols[2].metric('Diferença absoluta de %', 
                      f'{perf_dif}%', 
                      f'Performance relativa: {abs(perf_rel)} X')
        else:
            cols[2].metric('Diferença absoluta de %', 
                      f'{perf_dif}%', 
                      f'Performance relativa: {abs(perf_rel)} X', delta_color='inverse')

    else:
        cols[2].metric('Diferença absoluta de %', 
                      f'{perf_dif}%', 
                      f'Performance relativa: {abs(perf_rel)} X', delta_color='inverse' )

