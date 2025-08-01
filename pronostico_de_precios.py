# -*- coding: utf-8 -*-
"""Pronostico de precios.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1U1kaWXiTNWIhgw6_ay2wkU094RXJ3Ms5

# Programa para predecir los precios de los alimentos
"""

# importamos las librarías necesarias y creación del DataFrame

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error

precios_crudos =  pd.read_excel('Precios_2013 - 2025.xlsx')

"""Verificación de que no existan datos nulos en el data frame"""

# Verificación de existencia de datos nulos en el Dataframe

print(precios_crudos.describe(include='all').head(2))

"""Posibles productos a analizar y despliegue de datos faltantes"""

# Creaos una lista de los posibles productos a analizar
Productos_seleccionados = ['Cebolla cabezona blanca', 'Banano criollo', 'Arroz de primera', 'Limón común', 'Piña gold',
                           'Plátano hartón maduro','Plátano hartón verde','Zanahoria', 'Cebolla junca', 'Aguacate papelillo',
                           'Fríjol cargamanto rojo', 'Papa criolla limpia', 'Papaya melona', 'Mango común', 'Coliflor']

Productos_seleccionados = sorted(Productos_seleccionados)
for producto in Productos_seleccionados:
    print(producto)

print('\n')

producto = input('Ingrese un producto de la lista anterior: ')
producto = producto.capitalize()
print('\n', producto)

# Creamos un nuevo DataFrame con el producto seleccionado
producto_df = precios_crudos[(precios_crudos['Producto'] == producto) & (precios_crudos['Fuente'] == 'Medellín, Central Mayorista de Antioquia')].copy()

# Creamos un rango de fechas completo desde la mínima hasta la máxima fecha en el DataFrame
full_date_range = pd.date_range(start=producto_df['Fecha'].min(),
                                 end=producto_df['Fecha'].max(), freq='MS')

# Exrtacción de las fechas presentes en el DataFrame
present_dates = producto_df['Fecha'].unique()

# Encontramos las fechas faltantes comparando las fechas completas con las presentes
missing_dates = full_date_range[~full_date_range.isin(present_dates)]

# Desplegamos las fechas faltantes
print('\n'f"Meses con registros faltantes para el producto {producto}")
for date in missing_dates:
    print(date.strftime('%Y-%m'))

# Filtramos el DataFrame por fechas entre 2013 y 2025
producto_2013_2025_df = producto_df[(producto_df['Fecha'].dt.year >= 2013) & (producto_df['Fecha'].dt.year <= 2025)].copy()

# Selección de las columnas 'Fecha' y 'Precio'
producto_precio_2013_2025_df = producto_2013_2025_df[['Fecha', 'Precio ']]

# Despliegue del nuevo DataFrame
display(producto_precio_2013_2025_df.head())

# Gráfica del nuevo DataFrame
plt.figure(figsize=(12, 6))
plt.plot(producto_precio_2013_2025_df['Fecha'], producto_precio_2013_2025_df['Precio '], 'b*-')
plt.xlabel('Año')
plt.ylabel('Precio (COP)')
plt.title(f'Precio del producto {producto} en Medellín (2013 - Presente)')
plt.grid(True)
plt.show()

# Calculamos el promedio movil doble de tres peridodos para el producto que se eligió previamente


def PMD3P(x):
    # Definicón de algunos parámetros
    # Remove the line below that redefines x
    # x = producto_df[(producto_df['Fecha'].dt.year >= 2013) & (producto_df['Fecha'].dt.year <= 2025)].copy()
    x = x[['Fecha', 'Precio ']].copy()
    x['M_prime'] = x['Precio '].rolling(window=3).mean()
    x['M_double_prime'] = x['M_prime'].rolling(window=3).mean()
    # Pronóstico
    window = 3
    x['a'] = 2 * x['M_prime'] - x['M_double_prime']
    # Correct the column access from x(['M_double_prime']) to x['M_double_prime']
    x['b'] = x['M_prime'] - x['M_double_prime'] * (2 / (window - 1))
    x['Forecast'] = x['a'] + x['b']
    # Gráfica del PMD3P
    plt.figure(figsize=(12, 6))
    plt.plot(x['Fecha'], x['Precio '], 'b*-', label='Valores originales')
    plt.plot(x['Fecha'], x['Forecast'], 'r.--', label='Valores pronosticados (suavizados)\n con promedio movil doble con tres periodos')
    plt.xlabel('Año')
    plt.ylabel('Precio (COP)')
    plt.title(f'Precio del producto {producto} en Medellín (Original vs Pronóstico)')
    plt.legend()
    plt.grid(True)
    plt.show()
    # Cálculo del error absoluto medio
    cleaned_df = x.dropna(subset=['Precio ', 'Forecast']).copy()
    mae = mean_absolute_error(cleaned_df['Precio '], cleaned_df['Forecast'])

    num_data_points = len(cleaned_df)
    last_a = cleaned_df['a'].iloc[-1]
    last_b = cleaned_df['b'].iloc[-1]
    forecasts = []
    for h in range(1, 5):
        forecast = last_a + last_b * h
        forecasts.append(forecast)
    print(f"Precios pronosticados del producto {producto} para los próximos 4 meses con PMD3P:")
    for i, forecast_value in enumerate(forecasts):
        print(f"Mes {i+1}: {forecast_value:.2f}")
    print(f"Error absoluto medio (MAE): {mae}") # Corrected the print statement here

x=producto_2013_2025_df
PMD3P(x)

def suavizado_exponencial_doble(df, alpha = 0.2, beta = 0.1, window=3):
    """
    Aplica el suavizado exponencial doble a los datos de precios.

    Args:
        df (pd.DataFrame): DataFrame con las columnas 'Fecha' y 'Precio '.
        alpha (float): Factor de suavizado para el nivel.
        beta (float): Factor de suavizado para la tendencia.
        window (int): Tamaño de la ventana para el cálculo inicial del nivel y la tendencia.

    Returns:
        pd.DataFrame: DataFrame con las columnas originales y las series suavizadas y pronosticadas.
    """
    df = df[['Fecha', 'Precio ']].copy()

    # Inicialización de L y T
    df['L'] = np.nan
    df['T'] = np.nan
    df['Forecast'] = np.nan

    # Cálculo inicial para L y T (usando una ventana de 3 periodos como ejemplo)
    df.loc[window - 1, 'L'] = df.loc[:window - 1, 'Precio '].mean()
    df.loc[window - 1, 'T'] = (df.loc[window - 1, 'Precio '] - df.loc[0, 'Precio ']) / (window - 1)


    # Aplicación del suavizado exponencial doble
    for i in range(window, len(df)):
        df.loc[i, 'L'] = alpha * df.loc[i, 'Precio '] + (1 - alpha) * (df.loc[i-1, 'L'] + df.loc[i-1, 'T'])
        df.loc[i, 'T'] = beta * (df.loc[i, 'L'] - df.loc[i-1, 'L']) + (1 - beta) * df.loc[i-1, 'T']
        df.loc[i, 'Forecast'] = df.loc[i-1, 'L'] + df.loc[i-1, 'T']

    # Pronóstico para los próximos 4 meses
    last_L = df['L'].iloc[-1]
    last_T = df['T'].iloc[-1]
    forecasts = []
    for h in range(1, 5):
        forecast = last_L + last_T * h
        forecasts.append(forecast)

    print(f"Precios pronosticados para los próximos 4 meses del producto {producto} con suavizado exponencial doble:")
    for i, forecast_value in enumerate(forecasts):
        print(f"mes {i+1}: {forecast_value:.2f}")

    # Cálculo del error absoluto medio (MAE)
    cleaned_df = df.dropna(subset=['Precio ', 'Forecast']).copy()
    mae = mean_absolute_error(cleaned_df['Precio '], cleaned_df['Forecast'])
    print(f"Error absoluto medio (MAE): {mae}")

    # Gráfica
    plt.figure(figsize=(12, 6))
    plt.plot(df['Fecha'], df['Precio '], 'b*-', label='Valores originales')
    plt.plot(df['Fecha'], df['Forecast'], 'g.--', label='Valores pronosticados\n con suavizado exponencial doble ')
    plt.xlabel('Año')
    plt.ylabel('Precio (COP)')
    plt.title(f'Precio del producto {producto} (Original vs Pronóstico)')
    plt.legend()
    plt.grid(True)
    plt.show()

    return df

# Aplicar la función de suavizado exponencial doble (ejemplo con alpha=0.2 y beta=0.1)
df_suavizado = suavizado_exponencial_doble(x.reset_index(drop=True).copy(), alpha=0.2, beta=0.1)