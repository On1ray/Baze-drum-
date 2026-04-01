SELECT 
    p.id,
    p.type,
    CASE 
        WHEN p.type = 'юр' THEN l.name
        ELSE pr.last_name || ' ' || pr.first_name
    END as client_name,
    pc.name as price_category,
    e.full_name as manager,
    COALESCE(a.login, 'Нет логина') as login,
    COALESCE(a.email, 'Нет email') as email,
    a.status,
    datetime(a.created_at, 'localtime') as created_at
FROM purchaser p
LEFT JOIN account a ON a.id = p.id
LEFT JOIN legal_entity l ON l.id = p.id
LEFT JOIN private_person pr ON pr.id = p.id
LEFT JOIN price_category pc ON pc.id = p.price_category_id
LEFT JOIN employee e ON e.id = p.manager_id
ORDER BY p.id;