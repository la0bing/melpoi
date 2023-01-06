import pandas as pd

from melpoi.dataframe import DataFrameAnalyzer


def load_df_assert(csv_filepath, target):
    df = pd.read_csv(csv_filepath)
    df["some_int_with_null"] = 1
    # augment
    df.loc[2:7, "sepal.length"] = pd.NA
    df.loc[5, "variety"] = pd.NA
    df.loc[4:5, "petal.length"] = pd.NA
    df.loc[1:100, "some_int_with_null"] = pd.NA
    # df
    dfa = DataFrameAnalyzer(df)
    dfa.run()
    assert dfa.columns_info.values.tolist() == target


# test1
def test_DataFrameAnalyzer1():
    target = [
        ["sepal.length", "float", 36, 6, 4.0, "Slight NaN % found!"],
        ["sepal.width", "float", 23, 0, 0.0, ""],
        ["petal.length", "float", 44, 2, 1.3, "Slight NaN % found!"],
        ["petal.width", "float", 22, 0, 0.0, ""],
        ["variety", "string", 4, 1, 0.7, "Slight NaN % found!"],
        [
            "some_int_with_null",
            "float",
            2,
            100,
            66.7,
            "High NaN % found!, Possible float caused by NaN values",
        ],
    ]
    load_df_assert("tests/dataframe/data/iris.csv", target)
