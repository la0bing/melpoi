create or replace TEMPORARY table `create.table.name`

with cte1 as
(
    SELECT     *
    FROM
    `from.table.name1` LEFT JOIN join.table.name1
),
cte2 as
(
    SELECT     *
    FROM
    `from.table.name2`
),

SELECT     *
FROM
cte;
