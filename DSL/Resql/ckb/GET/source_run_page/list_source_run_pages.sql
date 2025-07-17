WITH latest_run_pages AS (
    SELECT DISTINCT ON (base_id) 
        id, base_id, source_run_report_base_id, url, error_type, error_message, scraped_at, is_deleted
    FROM source_run_page 
    WHERE (:source_run_report_base_id IS NULL OR source_run_report_base_id = :source_run_report_base_id::UUID)
    ORDER BY base_id, updated_at DESC
)
SELECT 
    id, base_id, source_run_report_base_id, url, error_type, error_message, scraped_at,
    :page as page,
    CEIL(COUNT(*) OVER () / :page_size::DECIMAL) AS total_pages
FROM latest_run_pages
WHERE is_deleted = FALSE
ORDER BY 
    CASE WHEN :sorting = 'url asc' THEN url END ASC,
    CASE WHEN :sorting = 'url desc' THEN url END DESC,
    CASE WHEN :sorting = 'error_type asc' THEN error_type END ASC,
    CASE WHEN :sorting = 'error_type desc' THEN error_type END DESC,
    CASE WHEN :sorting = 'error_message asc' THEN error_message END ASC,
    CASE WHEN :sorting = 'error_message desc' THEN error_message END DESC,
    CASE WHEN :sorting = 'scraped_at asc' THEN scraped_at END ASC,
    CASE WHEN :sorting = 'scraped_at desc' THEN scraped_at END DESC,
    scraped_at DESC NULLS LAST
LIMIT :page_size::INTEGER 
OFFSET ((GREATEST(:page::INTEGER, 1) - 1) * :page_size::INTEGER);