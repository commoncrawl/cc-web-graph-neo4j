#!/bin/bash
set -e

docker run --rm \
  -v "$(pwd)/data/neo4j_csv":/import \
  -v "$(pwd)/data/neo4j_db":/data \
  neo4j:latest \
  neo4j-admin database import full \
  --delimiter="," \
  --array-delimiter=";" \
  --id-type=string \
  --overwrite-destination=false \
  --nodes=/import/vertices/vertices_test.csv \
  --relationships=/import/edges/edges_test.csv

echo
echo "Import Done. Prepare to start Neo4j."
