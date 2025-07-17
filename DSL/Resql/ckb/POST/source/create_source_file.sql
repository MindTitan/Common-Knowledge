INSERT INTO source (
    agency_base_id, subsector, type, status, url
)
VALUES (
    :agency_base_id::UUID, 
    :subsector, 
    'file'::source_type, 
    'running'::source_status_type,
    :url
)
RETURNING id, base_id, agency_base_id, subsector, type, status