SELECT 
    base_id AS client_id,
    CASE 
        WHEN zipped_data_url IS NOT NULL AND zipped_data_url != '' 
        THEN TRUE 
        ELSE FALSE 
    END AS is_data_avialable
FROM agency a1
WHERE base_id = ANY(STRING_TO_ARRAY(:agencyIds, ',')::UUID[])
  AND updated_at = (
      SELECT MAX(updated_at) 
      FROM agency a2
      WHERE a2.base_id = a1.base_id
        AND a2.is_deleted = FALSE
  )
  AND is_deleted = FALSE;