SELECT 
    orders.id AS order_id,
    users.id AS user_id,
    Shoes.id AS shoe_id,
    Shoes.nom AS shoe_name,
    Shoes.prix AS shoe_price,
    users.name AS user_name,
    Shoes.taille AS shoe_size
FROM orders
JOIN users
  ON orders.idUser = users.id
JOIN Shoes
  ON orders.idShoe = Shoes.id;