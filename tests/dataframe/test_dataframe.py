import pandas as pd
import pytest

from melpoi.dataframe import DataFrameAnalyzer
from melpoi.dataframe.exception import MissingRunException


def fail_scenario(csv_filepath):
    df = pd.read_csv(csv_filepath)
    dfa = DataFrameAnalyzer(df)
    with pytest.raises(MissingRunException):
        dfa.columns_info
    with pytest.raises(MissingRunException):
        dfa.df_info


def pass_scenario(csv_filepath, target1, target2):
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
    assert dfa.columns_info.to_json() == target1
    assert dfa.df_info.to_json() == target2


# test1
def test_pass():
    target1 = '{"dtype":{"sepal.length":"float","sepal.width":"float","petal.length":"float","petal.width":"float","variety":"string","some_int_with_null":"float"},"distinct_count":{"sepal.length":36,"sepal.width":23,"petal.length":44,"petal.width":22,"variety":4,"some_int_with_null":2},"na_count":{"sepal.length":6,"sepal.width":0,"petal.length":2,"petal.width":0,"variety":1,"some_int_with_null":100},"na_percentage":{"sepal.length":4.0,"sepal.width":0.0,"petal.length":1.3,"petal.width":0.0,"variety":0.7,"some_int_with_null":66.7},"remarks":{"sepal.length":"Slight NaN % found!","sepal.width":"","petal.length":"Slight NaN % found!","petal.width":"","variety":"Slight NaN % found!","some_int_with_null":"High NaN % found!, Possible float caused by NaN values"}}'
    target2 = '{"value":{"rows_count":150.0,"columns_count":6.0,"rows_with_na":109.0,"average_na_count_per_row":0.73,"max_na_count_per_row":4.0},"remarks":{"rows_count":"","columns_count":"","rows_with_na":"More than half of the rows have NA values!","average_na_count_per_row":"","max_na_count_per_row":"Some of the rows have NA is most fields!"}}'
    pass_scenario("tests/dataframe/data/iris.csv", target1, target2)


def test_fail():
    fail_scenario("tests/dataframe/data/iris.csv")
