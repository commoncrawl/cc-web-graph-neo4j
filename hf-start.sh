# load database backup
wget --no-clobber --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/datasets/lhoestq/dump-neo4j/resolve/main/system.dump -P /backups/
wget --no-clobber --header="Authorization: Bearer $HF_TOKEN" https://huggingface.co/datasets/lhoestq/dump-neo4j/resolve/main/neo4j.dump -P /backups/
neo4j-admin database load --expand-commands system --from-path=/backups --overwrite-destination=true
neo4j-admin database load --expand-commands neo4j --from-path=/backups --overwrite-destination=true

# start database
/startup/docker-entrypoint.sh neo4j &
# start app
python3 /application_neo4j/app.py &
# wait for any process to exit
wait -n
# exit with status of process that exited first
exit $?
