import gzip, shutil, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings as S

output_dir = S.HOST_EDGES_DIR
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "host_edges.txt"
describe_file = output_dir / "describe.txt"

if S.GRAPH_KIND == "domain":
    cand = S.DATA_DIR / f"cc-main-{S.RELEASE}-domain-edges.txt.gz"
    if cand.exists():
        gz_path = cand
    else:
        ms = list(S.DATA_DIR.glob("*domain-edges.txt.gz"))
        if not ms:
            raise FileNotFoundError("domain edges .txt.gz not found under data/")
        gz_path = ms[0]
    current_index = 0
    with open(output_file, "w", encoding="utf-8") as fout, gzip.open(gz_path, "rt", encoding="utf-8") as fin:
        for line in fin:
            fout.write(line)
            current_index += 1
    with open(describe_file, "w", encoding="utf-8") as f:
        f.write(f"1-{current_index} = {gz_path.name}")
    print("Success: edges")
else:
    S.TMP_DIR.mkdir(parents=True, exist_ok=True)
    decompressed_path = S.TMP_DIR / "paths.list"
    with gzip.open(S.EDGES_PATHS_GZ, "rb") as f_in, open(decompressed_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    with open(decompressed_path, "r") as f:
        lines = [line.strip() for line in f if line.strip().endswith(".txt.gz")]
    def fetch(p):
        filename = p.split("/")[-1]
        url = f"{S.CC_BASE_URL}/{p}"
        target = output_dir / filename
        if target.exists():
            return filename
        urllib.request.urlretrieve(url, target)
        return filename
    with ThreadPoolExecutor(max_workers=S.DOWNLOAD_THREADS) as ex:
        futs = [ex.submit(fetch, p) for p in lines]
        for _ in as_completed(futs):
            pass
    part_ranges = []
    current_index = 0
    with open(output_file, "w", encoding="utf-8") as fout:
        for gz_file in sorted(output_dir.glob("part-*.txt.gz")):
            start = current_index + 1
            with gzip.open(gz_file, "rt") as fin:
                for line in fin:
                    fout.write(line)
                    current_index += 1
            end = current_index
            part_ranges.append(f"{start}-{end} = {gz_file.name}")
            gz_file.unlink()
    with open(describe_file, "w", encoding="utf-8") as f:
        f.write("\n".join(part_ranges))
    shutil.rmtree(S.TMP_DIR, ignore_errors=True)
    print("Success: edges")
