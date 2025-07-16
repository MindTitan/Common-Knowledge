WITH latest_agencies AS (
    SELECT DISTINCT ON (base_id) 
        id, base_id, name, sector, is_deleted, updated_at
    FROM agency 
    ORDER BY base_id, updated_at DESC
)
SELECT 
    id, base_id, name, sector, updated_at,
    :page as page,
    CEIL(COUNT(*) OVER () / :page_size::DECIMAL) AS total_pages,
    (COUNT(*) OVER ()) AS total
FROM latest_agencies
WHERE is_deleted = FALSE
ORDER BY 
    CASE WHEN :sorting = 'name asc' THEN name END ASC,
    CASE WHEN :sorting = 'name desc' THEN name END DESC,
    CASE WHEN :sorting = 'sector asc' THEN sector END ASC,
    CASE WHEN :sorting = 'sector desc' THEN sector END DESC,
    CASE WHEN :sorting = 'updatedAt asc' THEN updated_at END ASC,
    CASE WHEN :sorting = 'updatedAt desc' THEN updated_at END DESC,
    updated_at DESC
LIMIT :page_size::INTEGER 
OFFSET ((GREATEST(:page::INTEGER, 1) - 1) * :page_size::INTEGER);
