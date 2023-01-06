import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)
from pandas.errors import IntCastingNaNError

from melpoi.dataframe.metadata import (
    Column,
    DataFrameInfo,
    DatetimeDataType,
    FloatDataType,
    IntegerDataType,
    StringDataType,
)


class DataFrameAnalyzer:
    def __init__(
        self,
        df: pd.DataFrame,
        alpha: float = 0.05,
    ):
        self.__df = df
        self.__df_info = DataFrameInfo([])
        self.alpha = alpha

    @property
    def df(self):
        return self.__df

    @property
    def df_info(self):
        return self.__df_info

    @property
    def columns_info(self):
        return self.__column_info_df

    def _assign_columns(self):
        out_columns = {}
        for col in self.__df.columns:
            out_columns[col] = Column(col, dtype=self._detect_column_type(col))
        self.__df_info = DataFrameInfo(out_columns)

    def _detect_column_type(self, col):
        if is_string_dtype(self.__df[col]):
            return StringDataType()
        elif is_integer_dtype(self.__df[col]):
            return IntegerDataType()
        elif is_float_dtype(self.__df[col]):
            return FloatDataType()
        elif is_datetime64_any_dtype(self.__df[col]):
            return DatetimeDataType()

    def _count_na(self):
        na_df = self.__df.isna().sum()
        for col in na_df.index:
            self.__df_info.columns[col].na_count = na_df[col]
            self.__df_info.columns[col].na_percentage = round(
                na_df[col] / self.__df.shape[0] * 100, 1
            )

    def _count_highest_na_per_row(self):
        highest_na_per_row = self.__df.transpose().isna().sum().max()
        self.__df_info.max_na_count_per_row = highest_na_per_row
        self.__df_info.max_na_percentage_per_row = round(
            highest_na_per_row / len(self.__df_info.columns) * 100, 1
        )
        if highest_na_per_row > 0:
            self.__df_info.max_na_count_ids = self.__df[
                self.__df.transpose().isna().sum() == highest_na_per_row
            ].index.tolist()

    def _count_distinct(self):
        for col in self.__df.columns:
            self.__df_info.columns[col].distinct_count = (
                self.__df[col].unique().shape[0]
            )

    def _log_remarks(self, col, logs):
        if self.__df_info.columns[col].remarks == "":
            self.__df_info.columns[col].remarks = logs
        else:
            self.__df_info.columns[col].remarks += ", " + logs

    def _generate_columns_remarks(self):
        for col, col_info in self.__df_info.columns.items():
            # manually added possible problems
            ## high na count
            if col_info.na_percentage > 50:
                self._log_remarks(col, "High NaN % found!")
            elif col_info.na_percentage > 20:
                self._log_remarks(col, "Moderate NaN % found!")
            elif col_info.na_percentage > 0:
                self._log_remarks(col, "Slight NaN % found!")

            ## if convertable from float to int
            if (col_info.dtype == "float") and (col_info.na_count > 0):
                try:
                    col_without_na = self.__df[~self.__df[col].isna()][col]
                    int_col_without_na = col_without_na.astype(int)
                    if ((col_without_na - int_col_without_na) == 0).all():
                        self._log_remarks(col, "Possible float cause by NaN values")
                except IntCastingNaNError:
                    pass

            ##

    def _generate_df_remarks(self):
        ...

    def _set_column_info_df(self):
        data = []
        for col, col_info in self.__df_info.columns.items():
            row = col_info.unpack()
            row["dtype"] = row["dtype"]["name"]
            data.append(row)
        self.__column_info_df = pd.DataFrame(data)

    def run(self):
        # assign columns
        self._assign_columns()

        # quality check
        ## count na per columns
        self._count_na()

        ## count highest na count per row
        self._count_highest_na_per_row()

        ## distinct
        self._count_distinct()

        # add remarks to certain columns
        self._generate_columns_remarks()

        # add remarks for df
        self._generate_df_remarks()

        # in depth analysis

        # convert df_info.columns into column_info
        ## set column info df
        self._set_column_info_df()
