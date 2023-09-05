from melpoi.sql import SqlAnalyzer


def run_on_file(sql_filepath, expected_dict, min_dot=1):
    sql_a = SqlAnalyzer(sql_filepath, min_dot)
    out_dict = sql_a.get_dependencies()
    assert out_dict == expected_dict


# test1
def test_SqlAnalyzer1():
    expected_dict = {
        "tests/sql/sql_scripts/test1.sql": {
            "source_tables": [
                "FROM.TABLE.NAME1",
                "FROM.TABLE.NAME2",
                "JOIN.TABLE.NAME1",
            ],
            "output_tables": ["CREATE.TABLE.NAME"],
            "delete_tables": [],
        }
    }
    run_on_file("tests/sql/sql_scripts/test1.sql", expected_dict, 1)


# test2
def test_SqlAnalyzer2():
    expected_dict = {
        "tests/sql/sql_scripts/test2.sql": {
            "source_tables": ["CREATE.TABLE.NAME"],
            "output_tables": ["INSERT.TABLE.NAME"],
            "delete_tables": ["INSERT.TABLE.NAME"],
        }
    }
    run_on_file("tests/sql/sql_scripts/test2.sql", expected_dict)

# test_SqlAnalyzer_no_graphviz
def test_SqlAnalyzer_no_graphviz():
    sql_a = SqlAnalyzer("tests/sql/sql_scripts/test1.sql", 1)
    out_dict = sql_a.get_dependencies()
    assert out_dict == {
        "tests/sql/sql_scripts/test1.sql": {
            "source_tables": [
                "FROM.TABLE.NAME1",
                "FROM.TABLE.NAME2",
                "JOIN.TABLE.NAME1",
            ],
            "output_tables": ["CREATE.TABLE.NAME"],
            "delete_tables": [],
        }
    }
    assert sql_a.plot_inline() == "Graphviz is not installed. Visualization is not available."
