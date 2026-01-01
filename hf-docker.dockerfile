FROM neo4j:2025.09.0-community

# neo4j
RUN mkdir -p /backups
RUN chmod 640 /var/lib/neo4j/conf/neo4j.conf
RUN chmod 640 /var/lib/neo4j/conf/neo4j-admin.conf
ENV NEO4J_PLUGINS='["graph-data-science"]'

# python
RUN apt-get update \
  && apt-get install -y python3 python3-pip \  
  && rm -rf /var/lib/apt/lists/*

# app
ADD application_neo4j /application_neo4j
RUN pip install -r /application_neo4j/requirements.txt

# start
COPY start.sh start.sh
ENTRYPOINT ["/bin/bash"]
CMD ["./start.sh"]
