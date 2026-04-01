SELECT 
    o.id,
    o.issue_date,
    CASE 
        WHEN p.type = 'юр' THEN l.name
        ELSE pr.last_name || ' ' || pr.first_name
    END as client,
    e.full_name as manager,
    o.payment_date,
    o.release_date
FROM "order" o
LEFT JOIN purchaser p ON p.id = o.buyer_id
LEFT JOIN legal_entity l ON l.id = p.id
LEFT JOIN private_person pr ON pr.id = p.id
LEFT JOIN employee e ON e.id = o.employee_id
ORDER BY o.id;