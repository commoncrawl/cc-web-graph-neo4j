import gzip
import shutil
import requests
from pathlib import Path
import settings as S

def ensure_dirs():
    S.DATA_DIR.mkdir(parents=True, exist_ok=True)
    S.HOST_VERTICES_DIR.mkdir(parents=True, exist_ok=True)
    S.HOST_EDGES_DIR.mkdir(parents=True, exist_ok=True)

def reset_outputs():
    if S.NORMALIZED_VERTICES_TXT.exists():
        S.NORMALIZED_VERTICES_TXT.unlink()
    if S.NORMALIZED_EDGES_TXT.exists():
        S.NORMALIZED_EDGES_TXT.unlink()

def copy_gz_to_txt(src_gz: Path, dst_txt: Path):
    with gzip.open(src_gz, "rb") as fin, open(dst_txt, "wb") as fout:
        shutil.copyfileobj(fin, fout, length=1024 * 1024)

def stream_append_url_gz(url: str, out_path: Path):
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        g = gzip.GzipFile(fileobj=r.raw)
        with open(out_path, "ab") as fout:
            while True:
                chunk = g.read(1024 * 1024)
                if not chunk:
                    break
                fout.write(chunk)

def iter_paths_from_gz(paths_gz: Path):
    with gzip.open(paths_gz, "rt") as f:
        for line in f:
            p = line.strip()
            if p and not p.startswith("#"):
                yield p.lstrip("/")

def pull_domain():
    ensure_dirs()
    reset_outputs()
    copy_gz_to_txt(S.DOMAIN_VERTICES_TXTGZ, S.NORMALIZED_VERTICES_TXT)
    copy_gz_to_txt(S.DOMAIN_EDGES_TXTGZ, S.NORMALIZED_EDGES_TXT)

def pull_host():
    ensure_dirs()
    reset_outputs()
    for rel in iter_paths_from_gz(S.HOST_VERTICES_PATHS_GZ):
        stream_append_url_gz(f"{S.CC_BASE_URL}/{rel}", S.NORMALIZED_VERTICES_TXT)
    for rel in iter_paths_from_gz(S.HOST_EDGES_PATHS_GZ):
        stream_append_url_gz(f"{S.CC_BASE_URL}/{rel}", S.NORMALIZED_EDGES_TXT)

def main():
    if S.GRAPH_KIND == "domain":
        pull_domain()
    else:
        pull_host()
    print("OK")

if __name__ == "__main__":
    main()
