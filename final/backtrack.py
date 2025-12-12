# job_scheduler_0based_gaps_lrpt_nodeps.py
import time, copy
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd

@dataclass
class Op:
    id: int
    dur: int
    mach: int

@dataclass
class Job:
    id: int
    ops: List[Op]
    def next_op(self, prog): return self.ops[prog] if prog < len(self.ops) else None
    def complete(self, prog): return prog >= len(self.ops)

@dataclass
class Assign:
    j:int; o:int; m:int; s:int; e:int

class Tracker:
    def __init__(self): self.nodes=0; self.pruned=0; self.sol=0; self.start=0; self.end=0
    def start_t(self): self.start=time.time()
    def end_t(self): self.end=time.time()
    def elapsed(self): return self.end-self.start

class Scheduler:
    def __init__(self, machines:int, jobs:List[Job]):
        self.machines = machines
        self.jobs = jobs
        self.best: Optional[List[Assign]] = None
        self.best_ms = 10**9
        self.tracker = Tracker()

    def avail_ops(self, prog:Dict[int,int]):
        candidates = []
        for j in self.jobs:
            if j.complete(prog[j.id]): continue
            op = j.next_op(prog[j.id])
            if op:
                rem = sum(o.dur for o in j.ops[prog[j.id]:])
                candidates.append((j, op, rem))
        # LRPT sorting
        candidates.sort(key=lambda x: (x[2], x[0].id), reverse=True)
        return [(j,op) for j,op,_ in candidates]

    def backtrack(self, sched, prog, timeline, job_last_end):
        self.tracker.nodes += 1

        if all(j.complete(prog[j.id]) for j in self.jobs):
            ms = max(timeline)
            self.tracker.sol += 1
            if ms < self.best_ms:
                self.best_ms = ms
                self.best = copy.deepcopy(sched)
            return

        ops = self.avail_ops(prog)
        if not ops:
            self.tracker.pruned += 1
            return

        for job, op in ops:
            m = op.mach
            start = max(timeline[m], job_last_end[job.id])
            end = start + op.dur

            sched.append(Assign(job.id, op.id, m, start, end))

            old_t = timeline[m]
            old_j = job_last_end[job.id]

            timeline[m] = end
            job_last_end[job.id] = end
            prog[job.id] += 1

            if max(timeline) < self.best_ms:
                self.backtrack(sched, prog, timeline, job_last_end)
            else:
                self.tracker.pruned += 1

            sched.pop()
            timeline[m] = old_t
            job_last_end[job.id] = old_j
            prog[job.id] -= 1

    def solve(self):
        self.tracker.start_t()
        prog = {j.id:0 for j in self.jobs}
        timeline = [0]*self.machines
        job_last_end = {j.id:0 for j in self.jobs}
        self.backtrack([], prog, timeline, job_last_end)
        self.tracker.end_t()
        return self.best, self.best_ms


# ---------- Input ----------
def get_input():
    M = int(input("Machines count (min 1): "))
    J = int(input("Jobs count (min 1): "))

    jobs = []
    for jid in range(J):
        print(f"\nJob {jid}:")
        nops = int(input("  Number of operations (>=1): "))
        ops = []
        for oid in range(nops):
            d = int(input(f"    Op{oid} duration: "))
            m = int(input(f"    Op{oid} machine (0..{M-1}): "))
            ops.append(Op(oid, d, m))
        jobs.append(Job(jid, ops))
    return M, jobs

# ---------- Output ----------
def print_gantt(sol, M, ms):
    print("\nGANTT:")
    bym = {i:[] for i in range(M)}
    for a in sol: bym[a.m].append(a)

    for m in range(M):
        bym[m].sort(key=lambda x: x.s)
        line = f"M{m} |"
        cur = 0
        for a in bym[m]:
            if a.s > cur:
                line += "."*(a.s-cur)
            label = f"[J{a.j}O{a.o}]"
            line += label*(a.e-a.s)
            cur = a.e
        print(line + f" | End:{cur}")
    print("\nTime 0", " "*(ms-1), ms)

# ---------- Main ----------
def main():
    M, jobs = get_input()
    sched = Scheduler(M, jobs)
    best, ms = sched.solve()

    if best:
        print("\nBest makespan:", ms)
        print_gantt(best, M, ms)
        df = pd.DataFrame([vars(a) for a in best])
        df.to_csv("ops_output.csv", index=False)
        print("\nSaved: ops_output.csv")

    t = sched.tracker
    print(f"\nNodes: {t.nodes} | Pruned: {t.pruned} | Solutions: {t.sol} | Time: {t.elapsed():.4f}s")

if __name__ == "__main__":
    main()
