import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)
from pandas.errors import IntCastingNaNError

from melpoi.dataframe.exception import MissingRunException
from melpoi.dataframe.metadata import Column, DataFrameInfo


class DataFrameAnalyzer:
    def __init__(
        self,
        df: pd.DataFrame,
        alpha: float = 0.05,
    ):
        self.__df = df
        self.__df_info = DataFrameInfo([])
        self.alpha = alpha
        self.__df_info_df = self.__info = self.__column_info_df = None

    @property
    def df(self):
        return self.__df

    @property
    def info(self):
        if self.__info is not None:
            return self.__info
        else:
            raise MissingRunException()

    @property
    def df_info(self):
        if self.__df_info_df is not None:
            columns_to_ignore = [
                "columns",
                "max_na_percentage_per_row",
                "average_na_percentage_per_row",
                "rows_percentage_with_na",
            ]
            return self.__df_info_df.loc[
                [col for col in self.__df_info_df.index if col not in columns_to_ignore]
            ]
        else:
            raise MissingRunException()

    @property
    def columns_info(self):
        if self.__column_info_df is not None:
            return self.__column_info_df
        else:
            raise MissingRunException()

    def _detect_column_type(self, col):
        if is_string_dtype(self.__df[col]):
            return "string"
        elif is_integer_dtype(self.__df[col]):
            return "integer"
        elif is_float_dtype(self.__df[col]):
            return "float"
        elif is_datetime64_any_dtype(self.__df[col]):
            return "datetime"

    def _get_row_stats(self):
        # count average na per row
        self._count_average_na_per_row()
        # count highest na count per row
        self._count_highest_na_per_row()

    def _count_average_na_per_row(self):
        average_na_per_row = self.__df.transpose().isna().sum().mean()
        self.__df_info.na["average_na_count_per_row"] = round(average_na_per_row, 2)
        self.__df_info.na["average_na_percentage_per_row"] = round(
            average_na_per_row / len(self.__df_info.columns) * 100, 1
        )

    def _count_highest_na_per_row(self):
        highest_na_per_row = self.__df.transpose().isna().sum().max()
        self.__df_info.na["max_na_count_per_row"] = highest_na_per_row
        self.__df_info.na["max_na_percentage_per_row"] = round(
            highest_na_per_row / len(self.__df_info.columns) * 100, 1
        )

    def _set_column_info_df(self):
        data = []
        for col, col_info in self.__df_info.columns.items():
            row = col_info.unpack()
            data.append(row)
        self.__column_info_df = pd.DataFrame(data)
        self.__column_info_df.set_index("name", inplace=True)

    def _set_df_info_df(self):
        data = []
        for k, v in self.__df_info.generic.items():
            data.append({"name": k, "value": v})
        for k, v in self.__df_info.na.items():
            data.append({"name": k, "value": v})
        self.__df_info_df = pd.DataFrame(data)
        self.__df_info_df.set_index("name", inplace=True)

    def _log_remarks(self, df, df_id, logs):
        if "remarks" not in df.columns:
            df["remarks"] = ""
        if df.loc[df_id, "remarks"] == "":
            df.loc[df_id, "remarks"] = logs
        else:
            df.loc[df_id, "remarks"] += ", " + logs

    def _generate_columns_remarks(self):
        for col in self.__column_info_df.itertuples():
            # manually added possible problems
            ## high na count
            if col.na_percentage > 50:
                self._log_remarks(self.__column_info_df, col.Index, "High NaN % found!")
            elif col.na_percentage > 20:
                self._log_remarks(
                    self.__column_info_df, col.Index, "Moderate NaN % found!"
                )
            elif col.na_percentage > 0:
                self._log_remarks(
                    self.__column_info_df, col.Index, "Slight NaN % found!"
                )

            ## if convertable from float to int
            if (col.dtype == "float") and (col.na_count > 0):
                try:
                    col_without_na = self.__df[~self.__df[col.Index].isna()][col.Index]
                    int_col_without_na = col_without_na.astype(int)
                    if ((col_without_na - int_col_without_na) == 0).all():
                        self._log_remarks(
                            self.__column_info_df,
                            col.Index,
                            "Possible float caused by NaN values",
                        )
                except IntCastingNaNError as e:
                    print(e)

            ## other logical checks

    def _generate_df_remarks(self):
        # if high count of rows have minimum 1 na field
        if self.__df_info_df.loc["rows_percentage_with_na", "value"] > 50:
            self._log_remarks(
                self.__df_info_df,
                "rows_with_na",
                "More than half of the rows have NA values!",
            )

        # if rows have high na count
        if self.__df_info_df.loc["max_na_percentage_per_row", "value"] > 50:
            self._log_remarks(
                self.__df_info_df,
                "max_na_count_per_row",
                "Some of the rows have NA is most fields!",
            )

    def run(self):
        # columns checks
        out_columns = {}
        for col in self.__df.columns:
            ## quality check
            out_columns[col] = Column(
                name=col,
                dtype=self._detect_column_type(col),
                distinct_count=(self.__df[col].unique().shape[0]),
                na_count=self.__df[col].isna().sum(),
                na_percentage=round(
                    self.__df[col].isna().sum() / self.__df.shape[0] * 100, 1
                ),
            )
        self.__df_info = DataFrameInfo(
            columns=out_columns,
            generic={
                "rows_count": self.__df.shape[0],
                "columns_count": self.__df.shape[1],
            },
            na={
                "rows_with_na": self.__df.isnull().values.ravel().sum(),
                "rows_percentage_with_na": round(
                    self.__df.isnull().values.ravel().sum() / self.__df.shape[0] * 100,
                    2,
                ),
            },
        )

        # rows checks
        self._get_row_stats()

        # convert df_info.columns into column_info
        ## set column info df
        self._set_column_info_df()
        ## set df info df
        self._set_df_info_df()

        # logical remarks
        ## add remarks to certain columns
        self._generate_columns_remarks()
        # ## add remarks for df
        self._generate_df_remarks()
