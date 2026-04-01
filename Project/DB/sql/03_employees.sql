SELECT 
    e.id,
    e.full_name,
    e.inn,
    e.phone,
    a.login,
    a.email,
    a.status
FROM employee e
LEFT JOIN account a ON a.id = e.id
ORDER BY e.id;