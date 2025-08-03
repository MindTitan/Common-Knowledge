SELECT 
    id, base_id, name, sector, external_id, updated_at
FROM agency 
WHERE base_id = :base_id::UUID
  AND updated_at = (
      SELECT MAX(updated_at) 
      FROM agency 
      WHERE base_id = :base_id::UUID
  )
  AND is_deleted = FALSE LIMIT 1;