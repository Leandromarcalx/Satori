SELECT 
    name,
    price
    from items
WHERE price = SELECT(max(price) from items)


SELECT
    menu_id,
    COUNT(*) as qty_of_menus
    from items
WHERE price <= 20
GROUP BY menu_id
HAVING COUNT(*) > 30

ORDER BY qty_of_menus DESC

SELECT
    COUNT(DISTINCT(menu_id)) as number_of_menus
FROM
    items
WHERE price = (SELECT MAX(price) from items) OR (SELECT MAX(calories) from items)