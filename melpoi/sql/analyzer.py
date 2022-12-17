import os
import re
from tkinter.ttk import Style
from turtle import color

import graphviz
from IPython.display import Image


class SQLAnalyzer:
    def __init__(self, sql_filepath, min_dot=1) -> None:
        self.min_dot = min_dot
        self.sql_filepath = sql_filepath
        if sql_filepath.endswith(".sql"):
            self.sql_scripts = [sql_filepath]
        else:
            if not sql_filepath.endswith(os.path.sep):
                sql_filepath = sql_filepath + os.path.sep
            self.sql_scripts = [
                sql_filepath + x for x in os.listdir(sql_filepath) if x.endswith(".sql")
            ]

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
        # TABLENAMES(search for word after FROM with 2 dots in its name, with or without backticks)
        if self.min_dot == 0:
            table_regex = r"`?([A-Z0-9\-_]*\.?[A-Z0-9\-_]*\.?[A-Z0-9\-_]+)`?"
        elif self.min_dot == 1:
            table_regex = r"`?([A-Z0-9\-_]*\.?[A-Z0-9\-_]+\.[A-Z0-9\-_]+)`?"
        elif self.min_dot == 2:
            table_regex = r"`?([A-Z0-9\-_]+\.[A-Z0-9\-_]+\.[A-Z0-9\-_]+)`?"
        else:
            raise Exception("min_dot range must be between 0 and 2")
        # Source
        ## FROM = ALL FROM - DELETE FROM
        from_tables = re.findall(f"FROM {table_regex}", query)
        delete_from_tables = re.findall(f"(?:DELETE )FROM {table_regex}", query)
        from_no_delete_tables = [x for x in from_tables if x not in delete_from_tables]

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

        # Others
        ## DELETE
        delete_tables = re.findall(f"DELETE (?:FROM )?{table_regex}", query)

        # define output
        query_source_tables = from_no_delete_tables + join_tables
        query_output_tables = create_tables + insert_tables
        quert_delete_tables = delete_tables
        return query_source_tables, query_output_tables, quert_delete_tables

    def extract_sql(self, sql_filepath, groups=False):
        group_source_tables = []
        group_output_tables = []
        group_delete_tables = []
        queries = self.read_lines(sql_filepath)
        for query in queries:
            query = self.remove_capsulated_comments(query)
            (
                query_source_tables,
                query_output_tables,
                quert_delete_tables,
            ) = self.extract_statement(query)
            group_source_tables.append(list(set(query_source_tables)))
            group_output_tables.append(list(set(query_output_tables)))
            group_delete_tables.append(list(set(quert_delete_tables)))
        source_tables = list(set([y for x in group_source_tables for y in x]))
        output_tables = list(set([y for x in group_output_tables for y in x]))
        delete_tables = list(set([y for x in group_delete_tables for y in x]))
        if groups:
            return group_source_tables, group_output_tables, group_delete_tables
        else:
            source_tables.sort()
            output_tables.sort()
            delete_tables.sort()
            return {
                "source_tables": source_tables,
                "output_tables": output_tables,
                "delete_tables": delete_tables,
            }

    def get_dependencies(self):
        output = {}
        for i, sql_script in enumerate(self.sql_scripts):
            # script_tail_name = os.path.split(sql_script)[-1].replace(".sql", "")
            output[sql_script] = self.extract_sql(sql_script)
        return output

    def plot_inline(self):
        dot = graphviz.Digraph(strict=True)
        dot.attr(rankdir="LR")
        for i, sql_script in enumerate(self.sql_scripts):
            script_tail_name = os.path.split(sql_script)[-1].replace(".sql", "")
            (
                group_source_tables,
                group_output_tables,
                group_delete_tables,
            ) = self.extract_sql(sql_script, groups=True)
            with dot.subgraph(name=f"cluster_{i}") as sg:
                sg.attr(label=f"<<u>{script_tail_name}.sql</u>>", color="darkblue")
                k = 1
                for j, (source_tables, output_tables, delete_tables) in enumerate(
                    zip(group_source_tables, group_output_tables, group_delete_tables)
                ):
                    if len(source_tables) + len(output_tables) > 0:
                        with sg.subgraph(name=f"cluster_{k}") as ssg:
                            ssg.attr(
                                label=f"subquery_{k}", color="black", style="dashed"
                            )
                            ssg.node(f"{script_tail_name}_step_{k}", shape="box")
                            # create edges
                            for source_table in source_tables:
                                ssg.edge(source_table, f"{script_tail_name}_step_{k}")
                            for output_table in output_tables:
                                ssg.edge(f"{script_tail_name}_step_{k}", output_table)
                            for delete_table in delete_tables:
                                ssg.node(delete_table, color="darkred")
                                ssg.edge(f"{script_tail_name}_step_{k}", delete_table)
                        k += 1

        dot.render("output", format="png")
        os.remove("output")

        return Image(filename="output.png")
