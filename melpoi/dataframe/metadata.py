from dataclasses import asdict, dataclass
from typing import Dict


@dataclass
class Column:
    name: str
    dtype: str = None
    distinct_count: int = 0
    na_count: int = 0
    na_percentage: float = 0

    def unpack(self):
        return asdict(self)


@dataclass
class DataFrameInfo:
    columns: Dict[str, Column] = None
    generic: dict = None
    na: dict = None

    def unpack(self):
        return asdict(self)
