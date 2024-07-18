from typing import Union

import pandas as pd

from constants import *


def xlsx_to_processed_dataframes(
        file_path: str,
        sheet_names_enum: SheetNames,
        headers_row_number: int,
        dtype: dict,
        field_every_row_has: str,
        required_columns: list,
        sheet_names_to_catalog_names: dict[SheetNames, str],
) -> list[pd.DataFrame]:
    """
    Loads data from an Excel file and writes each sheet into a separate DataFrame

    :param file_path: Excel file path
    :param sheet_names_enum: Enum of sheet names to load
    :param headers_row_number: Number of string Pandas will use for column headings when reading an Excel sheets
    :param dtype: Column data types
    :param field_every_row_has: A field that every record in a table has
    :param required_columns: Columns that should be in DataFrames
    :param sheet_names_to_catalog_names: A dict containing sheet names corresponding to catalog names
    :return: DataFrames (each DataFrame corresponds to each sheet)
    """

    xlsx = pd.ExcelFile(file_path)
    frames = [
        _add_catalog_field(
            pd.read_excel(
                xlsx,
                sheet_name=sheet_name.value,
                header=headers_row_number,
                dtype=dtype
            ).dropna(subset=field_every_row_has)[required_columns],
            sheet_name=sheet_name,
            sheet_names_to_catalog_names=sheet_names_to_catalog_names
        )
        for sheet_name in sheet_names_enum
    ]

    return frames


def _add_catalog_field(
        df: pd.DataFrame,
        sheet_name: SheetNames,
        sheet_names_to_catalog_names: dict[SheetNames, str]
) -> pd.DataFrame:
    """
    Adds a catalog field to the given DataFrame

    :param df: pd.DataFrame to add the catalog field
    :param sheet_name: Name of the catalog field
    :param sheet_names_to_catalog_names: A dict containing sheet names corresponding to catalog names
    :return: DataFrame with catalog field added
    """

    df['catalog'] = sheet_names_to_catalog_names[sheet_name]
    return df


def choose_price(wholesale_price: Union[str, float], fixed_price: float, symbol_defining_the_price_type: str) -> float:
    """
    Returns a fixed_price if the wholesale_price is symbol_defining_the_price_type,
    otherwise returns the wholesale_price

    :param wholesale_price: Wholesale price or symbol defining the price type
    :param fixed_price: Fixed price
    :param symbol_defining_the_price_type: Symbol from the 'ОПТ' column that defines a type of price
    :return: Chosen price
    """

    try:
        price = float(fixed_price if wholesale_price == symbol_defining_the_price_type else wholesale_price)
        return price
    except ValueError:
        raise ValueError(f'Price must be a number or "{symbol_defining_the_price_type}" symbol')


def calculate_client_price(
        original_price: float,
        category: str,
        client_price_adjustments: dict[str, Tuple[float, float]]
) -> float:
    """
    Calculates the price for the client depending on the category of glass

    :param original_price: Original price
    :param category: Glass category
    :param client_price_adjustments: Dictionary containing the client price adjustments
    :return: Client price
    """

    try:
        extra, multiplier = client_price_adjustments[category]
        return (original_price + extra) * multiplier
    except ValueError:
        raise ValueError(f'Unknown glass category: {category}')


def main():
    try:
        df_all = pd.concat(
            xlsx_to_processed_dataframes(
                file_path='files/Прайс-лист AGC 2024.03.04 Опт.xlsx',
                sheet_names_enum=SheetNames,
                headers_row_number=HEADERS_ROW_NUMBER,
                dtype=DTYPE,
                field_every_row_has=FIELD_EVERY_ROW_HAS,
                required_columns=REQUIRED_COLUMNS,
                sheet_names_to_catalog_names=SHEET_NAMES_TO_CATALOG_NAMES
            ),
            ignore_index=True
        ).rename(columns=COLUMNS_TO_RENAME)

        df_all['price'] = df_all.apply(
            lambda row: choose_price(
                row['ОПТ'],
                row['Цена фиксирована'],
                symbol_defining_the_price_type=SYMBOL_DEFINING_PRICE_TYPE
            ),
            axis=1)
        df_all = df_all.drop(columns=['ОПТ', 'Цена фиксирована'])

        df_all.to_json('jsons/all.json', orient='records', force_ascii=False, indent=4)

        df_client = df_all[df_all['category'].isin([gc.value for gc in GlassCategory])]
        df_client['client_price'] = df_client.apply(
            lambda row: calculate_client_price(
                row['price'],
                row['category'],
                client_price_adjustments=CLIENT_PRICE_ADJUSTMENTS
            ),
            axis=1
        )
        df_client = df_client[CLIENT_COLUMNS]

        df_client.to_excel('files/client_catalog.xlsx', index=False)

    except Exception as e:
        print(f'Произошла ошибка: {e}')


if __name__ == '__main__':
    main()
