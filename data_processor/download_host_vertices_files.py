import gzip, shutil, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import settings as S

output_dir = S.HOST_VERTICES_DIR
output_dir.mkdir(parents=True, exist_ok=True)
output_file = output_dir / "host_vertices.txt"
describe_file = output_dir / "describe.txt"

if S.GRAPH_KIND == "domain":
    cand = S.DATA_DIR / f"cc-main-{S.RELEASE}-domain-vertices.txt.gz"
    if cand.exists():
        gz_path = cand
    else:
        ms = list(S.DATA_DIR.glob("*domain-vertices.txt.gz"))
        if not ms:
            raise FileNotFoundError("domain vertices .txt.gz not found under data/")
        gz_path = ms[0]
    current_index = 0
    with open(output_file, "w", encoding="utf-8") as fout, gzip.open(gz_path, "rt", encoding="utf-8") as fin:
        for line in fin:
            fout.write(line)
            current_index += 1
    with open(describe_file, "w", encoding="utf-8") as f:
        f.write(f"1-{current_index} = {gz_path.name}")
    print("Success: vertices")
else:
    S.TMP_DIR.mkdir(parents=True, exist_ok=True)
    paths_txt = S.TMP_DIR / "paths.list"
    with gzip.open(S.VERTICES_PATHS_GZ, "rb") as fin, open(paths_txt, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    with open(paths_txt) as f:
        paths = [line.strip() for line in f if line.strip().endswith(".txt.gz")]
    def fetch(p):
        fname = p.split("/")[-1]
        url = f"{S.CC_BASE_URL}/{p}"
        target = output_dir / fname
        if target.exists():
            return fname
        urllib.request.urlretrieve(url, target)
        return fname
    with ThreadPoolExecutor(max_workers=S.DOWNLOAD_THREADS) as ex:
        futs = [ex.submit(fetch, p) for p in paths]
        for _ in as_completed(futs):
            pass
    current_index = 0
    part_ranges = []
    with open(output_file, "w", encoding="utf-8") as fout:
        for part in sorted(output_dir.glob("part-*.txt.gz")):
            start = current_index + 1
            with gzip.open(part, "rt", encoding="utf-8") as fin:
                for line in fin:
                    fout.write(line)
                    current_index += 1
            end = current_index
            part_ranges.append(f"{start}-{end} = {part.name}")
            part.unlink()
    with open(describe_file, "w", encoding="utf-8") as f:
        f.write("\n".join(part_ranges))
    shutil.rmtree(S.TMP_DIR, ignore_errors=True)
    print("Success: vertices")
