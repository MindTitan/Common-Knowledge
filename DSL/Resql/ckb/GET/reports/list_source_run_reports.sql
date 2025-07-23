WITH latest_reports AS (
    SELECT DISTINCT ON (base_id) 
        id, base_id, agency_base_id, agency_name, url, errors, 
        scraping_started_at, scraping_finished_at, is_deleted
    FROM source_run_report 
    ORDER BY base_id, updated_at DESC
)
SELECT 
    id, base_id, agency_base_id, agency_name, url, errors, 
    scraping_started_at, scraping_finished_at,
    :page as page,
    CEIL(COUNT(*) OVER () / :page_size::DECIMAL) AS total_pages,
    (COUNT(*) OVER ()) AS total
FROM latest_reports
WHERE is_deleted = FALSE
ORDER BY 
    CASE WHEN :sorting = 'agency_name asc' THEN agency_name END ASC,
    CASE WHEN :sorting = 'agency_name desc' THEN agency_name END DESC,
    CASE WHEN :sorting = 'url asc' THEN url END ASC,
    CASE WHEN :sorting = 'url desc' THEN url END DESC,
    CASE WHEN :sorting = 'errors asc' THEN errors END ASC,
    CASE WHEN :sorting = 'errors desc' THEN errors END DESC,
    CASE WHEN :sorting = 'scraping_started_at asc' THEN scraping_started_at END ASC,
    CASE WHEN :sorting = 'scraping_started_at desc' THEN scraping_started_at END DESC,
    CASE WHEN :sorting = 'scraping_finished_at asc' THEN scraping_finished_at END ASC,
    CASE WHEN :sorting = 'scraping_finished_at desc' THEN scraping_finished_at END DESC,
    scraping_started_at DESC NULLS LAST
LIMIT :page_size::INTEGER 
OFFSET ((GREATEST(:page::INTEGER, 1) - 1) * :page_size::INTEGER);