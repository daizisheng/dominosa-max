#!/usr/bin/env python3
"""runall.py SETLIST STRUCTDIR T WORKDIR OUT.jsonl NPROC
Runs driver.py on the structure file of every set in SETLIST (lines containing "{...}"),
NPROC at a time; resumable (skips sets already present in OUT.jsonl).
The tiling tables written by tile.c are read from $DATADIR (default ../work)."""
import sys, os, json, subprocess, threading, queue, re

setlist, sdir, T, work, outfn, nproc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6])
here = os.path.dirname(os.path.abspath(__file__))
data = os.environ.get("DATADIR", os.path.join(here, "..", "work"))
sets = []
for line in open(setlist):
    m = re.search(r"\{([0-9,]*)\}", line)
    if m:
        B = [int(x) for x in m.group(1).split(",") if x]
        sets.append(B)
done = set()
if os.path.exists(outfn):
    for line in open(outfn):
        try: done.add(tuple(json.loads(line)["B"]))
        except Exception: pass
todo = [B for B in sets if tuple(sorted(B)) not in done]
print("sets %d, done %d, todo %d" % (len(sets), len(done), len(todo)), flush=True)
q = queue.Queue()
for B in todo: q.put(B)
lock = threading.Lock()
out = open(outfn, "a")


def worker():
    while True:
        try: B = q.get_nowait()
        except queue.Empty: return
        mask = sum(1 << b for b in B)
        sf = os.path.join(sdir, "%011x.txt" % mask)
        try:
            r = subprocess.run([sys.executable, os.path.join(here, "driver.py"), data, sf, T, work], capture_output=True, text=True, timeout=200000)
            line = r.stdout.strip()
            json.loads(line)
        except Exception as e:
            line = json.dumps({"B": sorted(B), "verdict": "UNRESOLVED:runner " + repr(e)[:200]})
        with lock:
            out.write(line + "\n"); out.flush()


th = [threading.Thread(target=worker) for _ in range(nproc)]
for t in th: t.start()
for t in th: t.join()
print("finished", flush=True)
