/*
declaration:
  version: 0.1
  description: "Get source_files by source id"
  method: get
  returns: json
  namespace: scheduler
  allowlist:
    query:
      - field: source_base_id
        type: string
        description: "base id of source"
  response:
    fields:
      - field: urls
        type: array
        items:
            type: string
        description: "urls to run"
*/
SELECT base_id as id, url
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
