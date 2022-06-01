################## REQUIREMENTS ##################
import streamlit as st
import pandas as pd

from datetime import date, datetime, timedelta
from pandas_datareader import data as wb


############ parâmetors de tempo ############
# Função para parâmetros de tempo

def temp(slider):
    # taking today's date
    hoje = str(date.today()) #2021-04-08
    
    # carry out conversion between string to datetime object
    today = datetime.strptime(hoje, '%Y-%m-%d')
    
    # calculating start date by subtracting n days
    start = today - timedelta(days = slider)
    comeco = str(start) #2021-04-08
    return comeco, hoje


############ Histórico da Ação de preços ############

@st.cache(show_spinner=False, allow_output_mutation=True)
def get_hist(port, slider): 
    range = temp(slider)
    start = range[0]
    end = range[1]
    
    hist= pd.DataFrame()
    hist.name = port.name

    for T in port['ticket']:
        hist[T] = wb.DataReader((T), data_source='yahoo', start=start, end=end)['Adj Close']

        # ^BVSP Anomally 
        if T == '^BVSP':
            hist[T] = hist[T] / 1000 # referance for thousand points

    return hist
        

############ Histórico de todos ############
@st.cache(show_spinner=False, allow_output_mutation=True)
def IndicadoresAll(ativos, slider):
    range = temp(slider)
    start = range[0]
    end = range[1]

    histAll= pd.DataFrame()
    for T in ativos:
        histAll[T] = wb.DataReader((T), data_source='yahoo', start=start, end=end)['Adj Close']
        # ^BVSP Anomally 
        if T == '^BVSP':
            histAll[T] = histAll[T] / 1000 # referance for thousand points
        
    return histAll

