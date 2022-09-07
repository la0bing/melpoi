# SQLAnalyzer
A python class to parse and analyze SQL scripts dependencies and outputs. This is useful when dealing with complex or confusing sql scripts or stored procedures. There are some limitation here and there feel free to suggest any changes.

## Get Started
The following libraries are needed:
  - Graphviz
  - Ipython (for viewing image in jupyter notebooks)

## Usage
```
from parser import SQLAnalyzer

sa = SQLAnalyzer("example.sql")
sa.plot_inline()
```
Output:
[![name](https://github.com/la0bing/melpy/blob/main/sql/SQLAnalyzer/example.png)](https://github.com/la0bing/melpy/blob/main/sql/SQLAnalyzer/example.png)
Each of the box in the graph represents a separated sql statement that can be treated as a single script, this is to help understand where the scripts can be refactor into smaller pieces of scripts.

```SQLAnalyzer``` class has an optional parameter ```min_dot``` which look for the minimum amount of dot within a table name to recognize them as a real table name, as it is common to use CTE to represent temporary tables.
