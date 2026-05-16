--любой заказ и товар, который есть в price_list_product
SELECT o.id AS order_id, plp.product_id 
FROM "order" o
JOIN price_list_product plp ON plp.price_list_id = o.price_list_id
LIMIT 50;