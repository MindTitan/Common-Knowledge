/*
declaration:
  version: 0.1
  description: "Get 1 not scheduled source"
  method: get
  returns: json
  namespace: scheduler
  allowlist: {}
  response:
    fields:
      - field: base_id
        type: string
        description: "base_id of source"
      - field: cron_schedule
        type: string
        description: "cron schedule"
*/
SELECT base_id, cron_schedule
FROM source
WHERE (base_id, updated_at) IN (
    SELECT base_id, max(updated_at)
    FROM source
    GROUP BY base_id
) AND is_deleted = FALSE AND update_automatically = TRUE AND next_scrapping_at IS NULL
LIMIT 1;
