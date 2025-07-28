INSERT INTO source_file (
    source_base_id, agency_base_id, url, page_title,
    last_scraped_at, originally_scraped, original_data_hash, type, status
)
VALUES (
    :source_base_id::UUID, :agency_base_id::UUID, :url, :page_title,
    :scraped_at::TIMESTAMP WITH TIME ZONE, :scraped_at::TIMESTAMP WITH TIME ZONE,
    :original_data_hash, 'scraped_file'::source_file_type, 'cleaning'::source_file_status_type
)
RETURNING base_id
