SELECT 
    id, base_id, scraping_log_url, cleaning_log_url
FROM source_run_report 
WHERE base_id = :base_id::UUID
  AND updated_at = (
      SELECT MAX(updated_at) 
      FROM source_run_report 
      WHERE base_id = :base_id::UUID
  )
  AND is_deleted = FALSE;