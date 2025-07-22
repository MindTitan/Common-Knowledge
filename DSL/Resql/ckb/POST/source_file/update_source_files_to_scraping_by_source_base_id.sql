/*
declaration:
  version: 0.1
  description: "Get source_files by source id and mark them as running"
  method: post
  returns: json
  namespace: scheduler
  allowlist:
    body:
      - field: source_base_id
        type: string
        description: "base id of source"
  response:
    fields:
      - field: id
        type: string
        description: "base id of source_file"
      - field: urls
        type: array
        items:
            type: string
        description: "urls to run"
      - field: hash
        type: string
        description: "current scraped data hash"
*/
SELECT
    copy_row_with_modifications(
        'source_file',
        'id', '::UUID', id::VARCHAR,
        ARRAY[
            'status', '::SOURCE_FILE_STATUS_TYPE', 'scraping'
        ]::VARCHAR[]
    ),
    base_id as id, url, original_data_hash as hash
FROM source_file
WHERE (base_id, updated_at) IN (
        SELECT base_id, max(updated_at)
        FROM source_file
        WHERE source_base_id = :source_base_id::UUID
        GROUP BY base_id
    )
    AND is_excluded = FALSE
    AND is_deleted = FALSE
    AND type = 'scraped_file';
