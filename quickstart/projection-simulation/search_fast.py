"""Optimized multi-process projector search."""
import time
import numpy as np
from multiprocessing import Pool, cpu_count
from sim import samples, fit, evaluate, TRIS, OCC_FAST

def evaluate_single(item):
    x, y, z, Pl, Nl, Al = item
    pos = np.array([x, y, z])
    ev = evaluate(pos, Pl, Nl, Al, TRIS[OCC_FAST])
    if ev["tr"] < 0.36:
        return None
    inc = np.degrees(np.arccos(np.clip(ev["cosi"][ev["lit"]], -1, 1))).mean() if ev["lit"].any() else 90.0
    return (float(ev["cover"]), float(-inc), float(x), float(y), float(z), float(ev["tr"]))

def run_search():
    t0 = time.time()
    P, N, A = samples(0.45)
    left = P[:, 0] <= 15.0
    Pl, Nl, Al = P[left], N[left], A[left]
    print(f"samples {len(P)} left {left.sum()} left area {round(Al.sum(), 1)}")

    floor_ok = lambda x, y: abs(x - 15) + abs(y - 14.21) <= 11.8
    inside_v = lambda x, y: (x + y > 22.4) and (x - y < 7.4)
    box = lambda x, y, z: abs(x - 15) + abs(y - 17.61) <= 5.2 and 4.8 <= z <= 8.9

    tasks = []
    for x in np.arange(4, 26.1, 1.0):
        for y in np.arange(9, 26.1, 1.0):
            if not (floor_ok(x, y) and inside_v(x, y)):
                continue
            for z in [2.5, 3.5, 4.5, 6.0, 7.5, 9.5, 11.5]:
                if box(x, y, z):
                    continue
                f, r, u, tr, hw, hh = fit(np.array([x, y, z]), Pl)
                if tr < 0.36:
                    continue
                tasks.append((x, y, z, Pl, Nl, Al))

    workers = min(16, cpu_count())
    print(f"Searching {len(tasks)} valid candidate positions using {workers} processes...")

    with Pool(processes=workers) as pool:
        raw_res = pool.map(evaluate_single, tasks, chunksize=8)

    res = [r for r in raw_res if r is not None]
    res.sort(reverse=True)

    print(f"Completed in {time.time() - t0:.2f}s! Found {len(res)} viable configurations.")
    print("cover  meanInc  x     y     z    TR")
    for c, ni, x, y, z, tr in res[:25]:
        print(f"{c:5.3f}  {-ni:5.1f}  {x:5.1f} {y:5.1f} {z:4.1f} {tr:5.2f}")
    
    np.save("search.npy", np.array(res))
    print("Saved results to search.npy")

if __name__ == "__main__":
    run_search()
