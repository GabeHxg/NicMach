import streamlit as st

def app():
    # Set page title
    st.markdown('Raciocínio e Estratégia')

    ##### Exploração Live ######
    with st.expander('Exploração | Live API'):
        st.markdown('''
        Na página de exploração Live existe uma conexão direta com a API do Yahoo Finance. Nesta página o usuário pode 
        selecionar as empresas que deseja comparar, selecionando também o período de análise entre 1 mês e 20 anos. 

        As condições de padronização e decomposição criam modelos estatíscos de comparação de dados em série (Series Data), 
        tornando mais relevante tanto a visualização da ação de preços quanto a interpretação de **Momentum Value**.

        Decidir as condições do período de análise, padronização e docomposição serão relevantes para a composição do portfólio
        na página **Multi Fator | Estático**. 
        ''')

    ##### Momentum ######
    with st.expander('Momentum | Static'):
        st.markdown('''
        Na página de Momentum existe uma conexão em batch com a API do Yahoo Finance, contendo 20 anos de ação de preço para os 92 ativos
        que compõe o índice Ibovespa. Nesta página o usuário deve selecionar os inputs da estratégia, o número de ativos que compõe a carteira, 
        e a proporção (peso) desejada para cada ativo. 

        É possível então verificar o comparativo de preço para as ações do portfólio durante o período de análise, verificar os múltiplos
        de valorização no período e o desempenho da carteira em relação ao benchmark (BVSP).
        ''')

    ##### Value & Size ######
    with st.expander('Value & Size | Static'):
        st.markdown('''
        Na página de Value & Size o usuário pode interagir com indicadores de análise fundamentalistas, que estão disponíveis pela 
        API do Yahoo Fin. 

        Em Inputs da Estratégia é possível definir um do indicadores (Trailing PriceToEarnings, Forward PriceToEarnings, Capitalização de
        Mercado e PriceToBook), Definir o número de ativos na carteira e então visualizar as métricas resultantes. 

        Na seção de Backtesting, a carteira selecionada pelo rank do indicador fundamentalista tem sua performance comparada
        ao benchmark. 
    ''')

    ##### Multi Fator ######
    with st.expander('Multi Fator | Static'):
        st.markdown('''
        Por fim, na página de Multi Fator, o investidor pode filtrar, através do menu lateral, os ativos que se encaixam 
        na análise fundamentalista acordada pela tese de investimento (Size & Value Analysis), e então adicionar a análise
        de **Momentum** dos ativos, ranqueando aqueles de melhor fundamento e Quality Momentum para o portfólio.

        Ao final, é possível realizar o Backtest da estratégia e sua comparação ao benchmark de referência.
    ''')

    with st.expander('Encontrando o melhor modelo'):
        st.markdown('''
        O objetivo deste aplicativo é a otimização da interação com estratégias de investimento em ações, 
        buscando realçar a interpretabilidade do modelo ideal. 

        Com os processos estatíscos é possível por exemplo reconhecer a Tendência e a Sazonalidade do Price Action, 
        que amplificam a qualidade de Momentum para ativos voláteis.

        Seria um prazer apresentar a usabilidade e a configuração técnica que comportam esse projeto. 
    ''')


