import pandas as pd


def choose_price(opt, fixed_price):
    return fixed_price if opt == '*' else opt


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
df_foreign, df_domestic = df_foreign[columns], df_domestic[columns]

# Add a 'catalog' column for catalog identification
df_foreign['catalog'], df_domestic['catalog'] = 'Иномарки', 'Отечественные'

# Combine the two DataFrames
df_all = pd.concat(
    [df_foreign, df_domestic],
    ignore_index=True
).rename(
    columns={
        'Код AGC': 'art',
        'Еврокод': 'eurocode',
        'Старый Код AGC': 'oldcode',
        'Наименование': 'name',
        'Вид стекла': 'category'
    }
)
df_all['price'] = df_all.apply(lambda row: choose_price(row['ОПТ'], row['Цена фиксирована']), axis=1)
df_all = df_all.drop(columns=['ОПТ', 'Цена фиксирована'])

df_all.to_json('jsons/all.json', orient='records', force_ascii=False, indent=4)

# Filter the required categories
df_client = df_all[df_all['category'].isin(['ветровое', 'заднее', 'боковое'])]

# Calculate client price
df_client['client_price'] = df_client.apply(
    lambda row: calculate_client_price(row['price'], row['category']),
    axis=1
)

# Select the required columns for the client
df_client = df_client[['catalog', 'category', 'art', 'eurocode', 'oldcode', 'name', 'client_price']]
df_client.columns = ['catalog', 'category', 'art', 'eurocode', 'oldcode', 'name', 'client_price']

df_client.to_excel('files/client_catalog.xlsx', index=False)
