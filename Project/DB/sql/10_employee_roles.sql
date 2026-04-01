SELECT 
    e.full_name as employee,
    GROUP_CONCAT(p.title, ', ') as positions,
    COUNT(DISTINCT ep.position_id) as positions_count
FROM employee e
LEFT JOIN employee_position ep ON ep.employee_id = e.id
LEFT JOIN position p ON p.id = ep.position_id
GROUP BY e.id, e.full_name
ORDER BY e.full_name;