from typing import Tuple

from enum import Enum


class SheetNames(Enum):
    """Enumeration of sheet names"""
    AUTO_GLASS_ACCESSORIES_GLUE = 'Автостекло. Аксессуары. Клей'
    RUSSIAN_AUTO_INDUSTRY = 'Российский автопром'


class GlassCategory(Enum):
    """Enumeration of glass categories"""
    WINDSHIELD = 'ветровое'
    REAR = 'заднее'
    SIDE = 'боковое'


HEADERS_ROW_NUMBER = 4

DTYPE = {
    'Код AGC': str,
    'Еврокод': str,
    'Старый Код AGC': str
}

FIELD_EVERY_ROW_HAS = 'Код AGC'

REQUIRED_COLUMNS = ['Вид стекла', 'Еврокод', 'Код AGC', 'Старый Код AGC', 'Цена фиксирована', 'Наименование', 'ОПТ']

SHEET_NAMES_TO_CATALOG_NAMES: dict[SheetNames, str] = {
    SheetNames.AUTO_GLASS_ACCESSORIES_GLUE: 'Иномарки',
    SheetNames.RUSSIAN_AUTO_INDUSTRY: 'Отечественные'
}

COLUMNS_TO_RENAME: dict[str, str] = {
    'Код AGC': 'art',
    'Еврокод': 'eurocode',
    'Старый Код AGC': 'oldcode',
    'Наименование': 'name',
    'Вид стекла': 'category'
}

SYMBOL_DEFINING_PRICE_TYPE = '*'

CLIENT_PRICE_ADJUSTMENTS: dict[str, Tuple[float, float]] = {
    GlassCategory.WINDSHIELD.value: (1000, 1.05),
    GlassCategory.REAR.value: (800, 1.07),
    GlassCategory.SIDE.value: (0, 1.10)
}

CLIENT_COLUMNS = ['catalog', 'category', 'art', 'eurocode', 'oldcode', 'name', 'client_price']
