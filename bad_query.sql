-- This query references a table that DOES NOT exist in DataHub
-- DocGuard should flag this as an UNKNOWN TABLE error!

SELECT * FROM this_table_does_not_exist;
