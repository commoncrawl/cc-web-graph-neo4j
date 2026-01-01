import pathlib, subprocess
from typing import List
from pyspark.sql import SparkSession, functions as F
import settings as S

OUT = S.NEO4J_CSV_DIR
V_OUT = OUT / "vertices"
E_OUT = OUT / "edges"
SCRIPT = S.SCRIPT_PATH

def ensure_dirs():
    V_OUT.mkdir(parents=True, exist_ok=True)
    E_OUT.mkdir(parents=True, exist_ok=True)
    S.NEO4J_DB_DIR.mkdir(parents=True, exist_ok=True)

def get_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName("convert")
        .master(S.SPARK_MASTER)
        .config("spark.sql.files.maxPartitionBytes", S.MAX_PART_BYTES)
        .config("spark.ui.showConsoleProgress", "true")
        .config("spark.ui.enabled", "true")
        .getOrCreate()
    )

def _write(df, out_dir: pathlib.Path, target_parts: int | None):
    cur = df.rdd.getNumPartitions()
    if target_parts is None:
        df2 = df
    elif target_parts <= cur:
        df2 = df.coalesce(target_parts)
    else:
        df2 = df.repartition(target_parts)
    (df2.write
        .mode("overwrite")
        .option("header", True)
        .csv(str(out_dir)))
    return list(out_dir.glob("part-*.csv"))

def convert_vertices(s: SparkSession) -> List[pathlib.Path]:
    sp = F.split(F.col("value"), r"\s+")
    if S.GRAPH_KIND == "domain":
        df = (
            s.read.text(str(S.HOST_VERTICES_DIR / "host_vertices.txt"))
            .filter(F.size(sp) >= 3)
            .select(
                sp.getItem(0).alias("id:ID"),
                F.split(sp.getItem(1), r"\.").alias("host_parts:string[]"),
                sp.getItem(2).cast("long").alias("num_hosts:long"),
            )
        )
    else:
        df = (
            s.read.text(str(S.HOST_VERTICES_DIR / "host_vertices.txt"))
            .filter(F.size(sp) >= 2)
            .select(
                sp.getItem(0).alias("id:ID"),
                F.split(sp.getItem(1), r"\.").alias("host_parts:string[]"),
            )
        )
    df = df.withColumn("host_parts:string[]", F.array_join(F.col("host_parts:string[]"), S.ARRAY_DELIM))
    df = df.withColumn(":LABEL", F.lit("Node"))
    return _write(df, V_OUT, S.V_PARTS)

def convert_edges(s: SparkSession) -> List[pathlib.Path]:
    sp = F.split(F.col("value"), r"\s+")
    df = (
        s.read.text(str(S.HOST_EDGES_DIR / "host_edges.txt"))
        .filter(F.size(sp) >= 2)
        .select(
            sp.getItem(0).alias(":START_ID"),
            sp.getItem(1).alias(":END_ID"),
        )
        .withColumn(":TYPE", F.lit("LINKS_TO"))
    )
    return _write(df, E_OUT, S.E_PARTS)

def make_script(nodes: List[pathlib.Path], rels: List[pathlib.Path]):
    n_args = " ".join(f"--nodes=/import/{p.relative_to(OUT)}" for p in nodes)
    r_args = " ".join(f"--relationships=/import/{p.relative_to(OUT)}" for p in rels)
    overwrite = "--overwrite-destination=true" if S.OVERWRITE else ""
    SCRIPT.write_text(f"""#!/bin/bash
set -e
docker run --rm -v "$(pwd)/{OUT}":/import -v "$(pwd)/{S.NEO4J_DB_DIR}":/data {S.NEO4J_IMAGE} \\
  neo4j-admin database import full {S.DB_NAME} \\
  --delimiter="{S.CSV_DELIM}" --array-delimiter="{S.ARRAY_DELIM}" --id-type={S.ID_TYPE} {overwrite} \\
  {n_args} \\
  {r_args}
echo "Run the following line to start a dashboard: "
echo "docker run -d --name my-neo4j -p 7474:7474 -p 7687:7687 \<br/> -v $(pwd)/{S.NEO4J_DB_DIR}:/data \<br/> -v $(pwd)/{OUT}:/import \<br/> -v $(pwd)/logs:/logs \<br/> -v $(pwd)/plugins:/plugins \<br/> -e NEO4J_AUTH={S.NEO4J_USER}/{S.NEO4J_PASS} \<br/> -e NEO4J_dbms_default__database={S.DB_NAME} \<br/> {S.NEO4J_IMAGE}"
""")
    SCRIPT.chmod(0o755)

def main():
    ensure_dirs()
    sp = get_spark()
    try:
        nodes = convert_vertices(sp)
        rels  = convert_edges(sp)
    finally:
        sp.stop()
    make_script(nodes, rels)
    if S.AUTO_IMPORT:
        subprocess.run([str(SCRIPT.resolve())], check=True)
    print("Done")

if __name__ == "__main__":
    main()
