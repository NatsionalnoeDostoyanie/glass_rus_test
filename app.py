import pandas as pd


def choose_price(row):
    if '*' == row['ОПТ']:
        return row['Цена фиксирована']
    else:
        return row['ОПТ']


def calculate_client_price(price, category):
    if category == 'ветровое':
        return (price + 1000) * 1.05
    elif category == 'заднее':
        return (price + 800) * 1.07
    elif category == 'боковое':
        return price * 1.10


dtype = {
    'Код AGC': str,
    'Еврокод': str,
    'Старый Код AGC': str
}

xlsx = pd.ExcelFile('files/Прайс-лист AGC 2024.03.04 Опт.xlsx')
df_foreign = pd.read_excel(xlsx, 'Автостекло. Аксессуары. Клей', header=4, dtype=dtype).dropna(subset=['Код AGC'])
df_domestic = pd.read_excel(xlsx, 'Российский автопром', header=4, dtype=dtype).dropna(subset=['Код AGC'])

# Define the required columns
columns = ['Вид стекла', 'Еврокод', 'Код AGC', 'Старый Код AGC', 'Цена фиксирована', 'Наименование', 'ОПТ']
df_foreign = df_foreign[columns]
df_domestic = df_domestic[columns]

# Add a 'catalog' column for catalog identification
df_foreign['catalog'] = 'Иномарки'
df_domestic['catalog'] = 'Отечественные'

df_foreign['price'] = df_foreign.apply(choose_price, axis=1)
df_domestic['price'] = df_domestic.apply(choose_price, axis=1)

# Combine the two DataFrames
df_all = pd.concat(
    [df_foreign, df_domestic],
    ignore_index=True
).drop(
    columns=['ОПТ', 'Цена фиксирована']
).rename(
    columns={
        'Код AGC': 'art',
        'Еврокод': 'eurocode',
        'Старый Код AGC': 'oldcode',
        'Наименование': 'name',
        'Вид стекла': 'category'
    }
)

df_all.to_json('jsons/all.json', orient='records', force_ascii=False, indent=4)

# Filter the required categories
df_client = df_all[df_all['category'].isin(['ветровое', 'заднее', 'боковое'])]

# Calculate client price
df_client['client_price'] = df_client.apply(
    lambda row: calculate_client_price(
        row['price'],
        row['category']
    ),
    axis=1
)

# Select the required columns for the client
df_client = df_client[['catalog', 'category', 'art', 'eurocode', 'oldcode', 'name', 'client_price']]
df_client.columns = ['catalog', 'category', 'art', 'eurocode', 'oldcode', 'name', 'client_price']

df_client.to_excel('files/client_catalog.xlsx', index=False)
