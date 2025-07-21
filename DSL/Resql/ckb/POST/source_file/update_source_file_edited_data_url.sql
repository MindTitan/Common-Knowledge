SELECT copy_row_with_modifications(
    'source_file',
    'id', '::UUID', id::VARCHAR,
    ARRAY[
        'edited_data_url', '::TEXT', :edited_data_url,
        'updated_at', '::TIMESTAMP WITH TIME ZONE', NOW()::VARCHAR
    ]::VARCHAR[]
) as id, page_title, file_name, url, subsector, source_base_id
FROM source_file
WHERE base_id = :base_id::UUID
  AND updated_at = (
      SELECT MAX(updated_at)
      FROM source_file
      WHERE base_id = :base_id::UUID
  )
  AND is_deleted = FALSE;