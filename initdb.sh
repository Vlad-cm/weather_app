docker cp latest.dump postgresdb-container:/
docker exec --user=root postgresdb-container pg_restore --clean -U postgres -d postgres /latest.dump
