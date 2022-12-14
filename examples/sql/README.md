# SqlAnalyzer
A python class to parse and analyze SQL scripts dependencies and outputs. This is useful when dealing with complex or confusing sql scripts or stored procedures. There are some limitation here and there feel free to suggest any changes.

## Get Started
The following libraries are needed:
  - Graphviz
  - Ipython (for viewing image in jupyter notebooks)

## Usage
### 1. Visualize
```
from melpoi.sql import SqlAnalyzer

sa = SqlAnalyzer("../../tests/sql/sql_scripts")
sa.plot_inline()
```
Output:
[![name](https://github.com/la0bing/melpoi/blob/master/examples/sql/SqlAnalyzer_output.png)](https://github.com/la0bing/melpoi/blob/master/examples/sql/SqlAnalyzer_sample.ipynb)
Each of the blue box in the graph represents a script found within the given path and the inner dashed boxes indicates a separate subquery within the scripts, it has a step_i indicator to follow through which part of the query will run first in the script. This way you can dump all sql scripts into a directory and let SqlAnalyzer do the dependencies checking for you. <br />
***\*The red circle indicates a ```DELETE FROM``` statement.***
<br />
### 2. Get table dependencies
```
from melpoi.sql import SqlAnalyzer

sa = SqlAnalyzer("../../tests/sql/sql_scripts")
dependencies_dict = sa.get_dependencies()
```
<br />
Others:

```SqlAnalyzer``` class has an optional parameter ```min_dot``` which look for the minimum amount of dot within a table name to recognize them as a real table name, as it is common to use CTE to represent temporary tables.
