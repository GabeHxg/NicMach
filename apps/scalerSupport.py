### Modules ### 
import pandas as pd
import numpy as np

from statsmodels.tsa.seasonal import seasonal_decompose

# Bibliotecas para Standardization 
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler


def observed(df):
    return df

# First | Natural Log
def logScaler(df):
    '''For a given df, returns a new df with 100-log version for each of the chosen tokens.
    '''
    
    # Create an empty df
    stand_ts = pd.DataFrame()
    stand_ts.name = df.name
    
    # Iterate for columns 
    for token in df.columns:
        scale = df[token][0]
        stand = df[token]/scale * 100
        stand = np.log(stand) * (100/np.log(100))
        stand_ts[token]=stand

    return stand_ts


# Second | Standard Scaler
def standardScaler(df):
    '''For a given df, returns a new dataframe with Standard Scaler version for each of the chosen tokens.
    '''
    # Assign model
    standard_scaler = StandardScaler()
    
    # Fit_transform the model
    stand_ts = standard_scaler.fit_transform(df)
    
    # Define dataframe 
    stand_ts = pd.DataFrame(data=stand_ts, columns=df.columns, index=df.index)
    stand_ts.name = df.name

    # Return dataframe 
    return stand_ts


# Third | MinMax Scaler
def mmScaler(df):
    '''For a given df, returns a new dataframe with Min Max Scaler version for each of the chosen tokens.
    '''
    # Assign model
    min_max_scaler = MinMaxScaler()
    
    # Fit_transform the model
    stand_ts = min_max_scaler.fit_transform(df)
    
    # Define dataframe 
    stand_ts = pd.DataFrame(data=stand_ts, columns=df.columns, index=df.index)
    stand_ts.name = df.name

    # Return dataframe 
    return stand_ts

# Fourth | robust Scaler
def rbstScaler(df):
    '''For a given df, returns a new dataframe with Robust Scaler version for each of the chosen tokens.
    '''   
    
    # Assign model
    robust_scaler = RobustScaler()
    
    # Fit_transform the model
    stand_ts = robust_scaler.fit_transform(df)
    
    # Define dataframe 
    stand_ts = pd.DataFrame(data=stand_ts, columns=df.columns, index=df.index)
    stand_ts.name = df.name
    
    # Return dataframe 
    return stand_ts


# last | pct_change
def pctChangeScaler(df):
    '''For a given df, returns a new df with 100-standard version for each of the chosen tokens.'''

    # Iterate for columns 
    df_pct = df.pct_change().fillna(100)
    for i in range(1,len(df_pct.index)):
        df_pct.iloc[i] = df_pct.iloc[i-1]*(df_pct.iloc[i]+1)

    df_pct.name = df.name
    return df_pct