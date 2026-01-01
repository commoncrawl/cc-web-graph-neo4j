from pathlib import Path

# Version of Webgraph using
RELEASE = "2025-mar-apr-may" 

# The level of webgraph, generally, it is either domain or host
GRAPH_KIND = "domain"

DATA_DIR = Path("data")
CC_BASE_URL = "https://data.commoncrawl.org"

HOST_VERTICES_PATHS_GZ = DATA_DIR / f"cc-main-{RELEASE}-host-vertices.paths.gz"
HOST_EDGES_PATHS_GZ    = DATA_DIR / f"cc-main-{RELEASE}-host-edges.paths.gz"
DOMAIN_VERTICES_TXTGZ  = DATA_DIR / f"cc-main-{RELEASE}-domain-vertices.txt.gz"
DOMAIN_EDGES_TXTGZ     = DATA_DIR / f"cc-main-{RELEASE}-domain-edges.txt.gz"

HOST_VERTICES_DIR = DATA_DIR / ("host_vertices" if GRAPH_KIND == "host" else "domain_vertices")
HOST_EDGES_DIR    = DATA_DIR / ("host_edges"    if GRAPH_KIND == "host" else "domain_edges")

NORMALIZED_VERTICES_TXT = HOST_VERTICES_DIR / "host_vertices.txt"
NORMALIZED_EDGES_TXT    = HOST_EDGES_DIR    / "host_edges.txt"

NEO4J_CSV_DIR = DATA_DIR / "neo4j_csv"
NEO4J_DB_DIR  = DATA_DIR / "neo4j_db"


# Naming the local webgraph
DB_NAME     = "graph.db"
NEO4J_IMAGE = "neo4j:latest"

# User Name
NEO4J_USER  = "neo4j" 

# Password for neo4j dashboard/server
NEO4J_PASS  = "test1234" 

CSV_DELIM   = ","
ARRAY_DELIM = ";"
ID_TYPE     = "string"  
OVERWRITE   = True

SPARK_MASTER     = "local[*]"

# Note: You can change it according to your hardware capacity
MAX_PART_BYTES   = 134_217_728  # 128MB
V_PARTS          = 16
E_PARTS          = 32
DOWNLOAD_THREADS = 16

AUTO_IMPORT = False  
AUTO_START  = False  

# Read 'readme' instruction before changing this file name
SCRIPT_PATH = Path("generated_docker_import.sh")