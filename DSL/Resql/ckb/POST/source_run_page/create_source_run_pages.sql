INSERT INTO source_run_page (
    agency_base_id, source_base_id, source_run_report_base_id, url, scraped_at, 
    error_type, error_message
)
SELECT
    page_data.agency_base_id,
    page_data.source_base_id,
    page_data.source_run_report_base_id,
    page_data.url,
    page_data.scraped_at,
    page_data.error_type,
    page_data.error_message
FROM (
    SELECT
        ((SELECT value) ->> 'agency_base_id')::UUID AS agency_base_id,
        ((SELECT value) ->> 'source_base_id')::UUID AS source_base_id,
        ((SELECT value) ->> 'source_run_report_base_id')::UUID AS source_run_report_base_id,
        (SELECT value) ->> 'url' AS url,
        ((SELECT value) ->> 'scraped_at')::TIMESTAMP WITH TIME ZONE AS scraped_at,
        (SELECT value) ->> 'error_type' AS error_type,
        (SELECT value) ->> 'error_message' AS error_message
    FROM JSON_ARRAY_ELEMENTS(ARRAY_TO_JSON(ARRAY[:pages])) WITH ORDINALITY
) AS page_data
RETURNING id, base_id, agency_base_id, source_base_id, source_run_report_base_id, 
          url, scraped_at, error_type, error_message;