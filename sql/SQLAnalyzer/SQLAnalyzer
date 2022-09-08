import os
import re

import graphviz
from IPython.display import Image


class SQLAnalyzer:
    def __init__(self, sql_filepath, min_dot=1) -> None:
        self.sql_filepath = sql_filepath
        self.min_dot = min_dot
        self.script_name = self.sql_filepath.split("/")[-1]

    def remove_leading_comments(self, line):
        return re.sub("(--|#)+.*$", "", line)

    def remove_capsulated_comments(self, query):
        return re.sub(r"/\*.*\*/", "", query)

    def read_lines(self, sql_filepath):
        with open(sql_filepath, "r") as f:
            lines = f.readlines()
            lines = [self.remove_leading_comments(x) for x in lines]
            one_liner = " ".join([x.upper().strip() for x in lines])
            queries = [x.strip() for x in one_liner.split(";") if x.strip() != ""]
            queries = [" ".join(x.split()) for x in queries]
        return queries

    def extract_statement(self, query):
        if self.min_dot == 0:
            table_regex = r"`?([A-Z0-9\-_]*\.?[A-Z0-9\-_]*\.?[A-Z0-9\-_]+)`?"
        elif self.min_dot == 1:
            table_regex = r"`?([A-Z0-9\-_]*\.?[A-Z0-9\-_]+\.[A-Z0-9\-_]+)`?"
        elif self.min_dot == 2:
            table_regex = r"`?([A-Z0-9\-_]+\.[A-Z0-9\-_]+\.[A-Z0-9\-_]+)`?"
        else:
            raise Exception("min_dot range must be between 0 and 2")
        # Source
        ## FROM (search for word after FROM with 2 dots in its name, with or without backticks)
        from_tables = re.findall(f"FROM {table_regex}", query)

        ## JOIN
        join_tables = re.findall(f"JOIN {table_regex}", query)

        # Output
        ## CREATE CREATE [ OR REPLACE ] [ TEMP | TEMPORARY ] TABLE [ IF NOT EXISTS ]
        create_tables = re.findall(
            f"CREATE (OR REPLACE )?(TEMP |TEMPORARY )?TABLE (IF NOT EXISTS )?{table_regex}",
            query,
        )
        create_tables = [x[3] for x in create_tables]

        ## INSERT INTO
        insert_tables = re.findall(f"INSERT (INTO )?{table_regex}", query)
        insert_tables = [x[1] for x in insert_tables]

        # define output
        query_source_tables = from_tables + join_tables
        query_output_tables = create_tables + insert_tables
        return query_source_tables, query_output_tables

    def extract_sql(self, groups=False):
        group_source_tables = []
        group_output_tables = []
        queries = self.read_lines(self.sql_filepath)
        for query in queries:
            query = self.remove_capsulated_comments(query)
            query_source_tables, query_output_tables = self.extract_statement(query)
            group_source_tables.append(list(set(query_source_tables)))
            group_output_tables.append(list(set(query_output_tables)))
        source_tables = [y for x in group_source_tables for y in x]
        output_tables = [y for x in group_output_tables for y in x]
        if groups:
            return group_source_tables, group_output_tables
        else:
            source_tables.sort()
            output_tables.sort()
            return {
                "source_tables": source_tables,
                "output_tables": output_tables,
            }

    def plot_inline(self):
        group_source_tables, group_output_tables = self.extract_sql(groups=True)
        dot = graphviz.Digraph(strict=True)
        dot.attr(label=self.script_name)
        dot.attr(rankdir="LR")

        k = 0
        for i, (source_tables, output_tables) in enumerate(
            zip(group_source_tables, group_output_tables)
        ):
            if len(source_tables) + len(output_tables) > 0:
                with dot.subgraph(name=f"cluster_{k}") as sg:
                    sg.attr(label=f"subquery_{k}")
                    sg.node(f"logic_{k}", shape="box")
                    # create edges
                    for source_table in source_tables:
                        sg.edge(source_table, f"logic_{k}")
                    for output_table in output_tables:
                        sg.edge(f"logic_{k}", output_table)
                k += 1

        dot.render(self.script_name.replace(".sql", ""), format="png")
        os.remove(self.script_name.replace(".sql", ""))

        return Image(filename=self.script_name.replace(".sql", ".png"))
