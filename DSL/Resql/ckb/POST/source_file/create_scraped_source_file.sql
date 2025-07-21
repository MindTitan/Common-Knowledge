INSERT INTO source_file (
    base_id, source_base_id, url, page_title, original_data_url, last_scraped_at, 
    originally_scraped, type
)
VALUES (
    :base_id::UUID, :source_base_id::UUID, :url, :page_title, :original_data_url, :scraped_at::TIMESTAMP WITH TIME ZONE, :scraped_at::TIMESTAMP WITH TIME ZONE, 'scraped_file'::source_file_type
)
RETURNING id, base_id, source_base_id, url, page_title, original_data_url, last_scraped_at;
