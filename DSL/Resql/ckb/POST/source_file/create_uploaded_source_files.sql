INSERT INTO source_file (
    source_base_id, file_name, subsector, created_at, type
)
SELECT
    :source_id::UUID,
    file_data.file_name,
    file_data.subsector,
    file_data.uploaded_at,
    'uploaded_file'::source_file_type
FROM (
    SELECT
        (SELECT value) ->> 'name' AS file_name,
        (SELECT value) ->> 'subsector' AS subsector,
        ((SELECT value) ->> 'uploadedAt')::TIMESTAMP WITH TIME ZONE AS uploaded_at
    FROM JSON_ARRAY_ELEMENTS(ARRAY_TO_JSON(ARRAY[:files])) WITH ORDINALITY
) AS file_data
RETURNING id, base_id, source_base_id, file_name, subsector, created_at;