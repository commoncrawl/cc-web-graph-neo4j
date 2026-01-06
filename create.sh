docker run -d \
 --name $CONAME \
 -p 7474:7474 -p 7687:7687 \
 -v "$(pwd)/data/neo4j_db":/data \
 -v "$(pwd)/data/import":/import \
 -v "$(pwd)/data/export":/export \
 -v "$(pwd)/logs":/logs \
 -v "$(pwd)/plugins":/plugins \
 -e NEO4J_AUTH="neo4j/$PW" \
 neo4j:latest
