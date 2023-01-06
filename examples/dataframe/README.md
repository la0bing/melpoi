# DataFrameAnalyzer
A python class to analyzer a pd.DataFrame object and try to optimize the datatypes, and suggesting possible problems in the dataset.

## Usage
### 1. Importing from pd.DataFrame
```
import pandas as pd
from melpoi.dataframe import DataFrameAnalyzer

df = pd.read_csv("../../tests/dataframe/data/iris.csv")
dfa = DataFrameAnalyzer(df)
dfa.run()
```
