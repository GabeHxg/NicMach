### Modules ### 
import pandas as pd

# algumas bibliotecas para data-viz:
from statsmodels.tsa.seasonal import seasonal_decompose

###### observed #####
def Observed(df, dec_period):
    obseved_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        decomposed_col     = seasonal_decompose(df[col], period=dec_period)
        obseved_df[col] = decomposed_col.observed
    return obseved_df
  


###### trend #####
def Trend(df, dec_period):
    trend_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        decomposed_col     = seasonal_decompose(df[col], period=dec_period)
        trend_df[col] = decomposed_col.trend
    return trend_df.dropna()  


###### seasonal #####
def Seasonal(df, dec_period):
    seasonal_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        decomposed_col     = seasonal_decompose(df[col], period=dec_period)
        seasonal_df[col] = decomposed_col.seasonal
    return seasonal_df   


###### resid #####
def Resid(df, dec_period):
    resid_df = pd.DataFrame(index=df.index)
    for col in df.columns:
        decomposed_col     = seasonal_decompose(df[col], period=dec_period)
        resid_df[col] = decomposed_col.resid
    return resid_df