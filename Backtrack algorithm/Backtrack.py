# job_scheduler_compact.py
import time, copy
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class Op:
    id: int
    dur: int
    mach: int
    def __repr__(self):
        return f"Op{self.id}(d={self.dur},M{self.mach})"

@dataclass
class Job:
    id: int
    ops: List[Op]
    deps: List[int]
    pri: int = 0
    def __repr__(self):
        return f"Job{self.id}(ops={len(self.ops)},deps={self.deps})"
    def next_op(self, prog):
        return self.ops[prog] if prog < len(self.ops) else None
    def complete(self, prog):
        return prog >= len(self.ops)

@dataclass
class Assign:
    j:int
    o:int
    m:int
    s:int
    e:int
    def __repr__(self):
        return f"J{self.j}O{self.o}->M{self.m}[{self.s}-{self.e}]"

class Tracker:
    def __init__(self):
        self.nodes=0
        self.pruned=0
        self.sol=0
        self.start=0
        self.end=0
    def start_t(self): self.start=time.time()
    def end_t(self): self.end=time.time()
    def elapsed(self): return max(0.0, self.end-self.start)

class Scheduler:
    def __init__(self, machines:int, jobs:List[Job]):
        self.machines=machines
        self.jobs=jobs
        self.best:Optional[List[Assign]] = None
        self.best_ms = 10**9
        self.tracker=Tracker()
        self.all_sols=[]
        for j in self.jobs:
            j.pri = -len(j.deps)

    def avail_ops(self, prog:Dict[int,int]) -> List[Tuple[Job,Op]]:
        res=[]
        for j in self.jobs:
            if j.complete(prog[j.id]): continue
            ok=True
            for d in j.deps:
                dep_job = next(filter(lambda x: x.id==d, self.jobs))
                if not dep_job.complete(prog[d]):
                    ok=False
                    self.tracker.pruned+=1
                    break
            if ok:
                op=j.next_op(prog[j.id])
                if op: res.append((j,op))
        return res

    def backtrack(self, sched:List[Assign], prog:Dict[int,int], timeline:List[int]):
        self.tracker.nodes += 1
        if all(j.complete(prog[j.id]) for j in self.jobs):
            ms = max(timeline) if timeline else 0
            self.tracker.sol += 1
            self.all_sols.append((copy.deepcopy(sched), ms))
            if ms < self.best_ms:
                self.best_ms = ms
                self.best = copy.deepcopy(sched)
            return
        ops = self.avail_ops(prog)
        if not ops:
            self.tracker.pruned += 1
            return
        ops.sort(key=lambda x: x[0].pri, reverse=True)
        for job, op in ops:
            m = op.mach
            if m<1 or m>self.machines:
                self.tracker.pruned += 1
                continue
            i = m-1
            s = timeline[i]
            e = s + op.dur
            a = Assign(job.id, op.id, m, s, e)
            sched.append(a)
            old = timeline[i]
            timeline[i] = e
            prog[job.id] += 1
            # simple pruning: partial makespan >= best
            if max(timeline) < self.best_ms:
                self.backtrack(sched, prog, timeline)
            else:
                self.tracker.pruned += 1
            # undo
            sched.pop()
            timeline[i] = old
            prog[job.id] -= 1

    def solve(self):
        total_ops = sum(len(j.ops) for j in self.jobs)
        print(f"\nJobs: {len(self.jobs)}, Machines: {self.machines}, Total ops: {total_ops}")
        self.tracker.start_t()
        prog = {j.id:0 for j in self.jobs}
        timeline = [0]*self.machines
        self.backtrack([], prog, timeline)
        self.tracker.end_t()
        return self.best, self.best_ms

# ---------- I/O / Output helpers ----------
def get_input():
    print("\nCompact Job Shop Input")
    while True:
        try: M=int(input("Machines (2-10): "));
        except: continue
        if 2<=M<=10: break
    while True:
        try: J=int(input("Jobs (1-10): "));
        except: continue
        if 1<=J<=10: break
    jobs=[]
    for jid in range(1,J+1):
        print(f"\nJob {jid}:")
        deps=[]
        if jid>1:
            raw=input(f"  Dependencies (ids < {jid}, comma or Enter): ").strip()
            if raw: deps=[int(x.strip()) for x in raw.split(',') if x.strip()]
        while True:
            try: nops=int(input("  Num operations (1-6): ")); break
            except: pass
        ops=[]
        for oid in range(1,nops+1):
            while True:
                try: d=int(input(f"    Op{oid} duration (1-20): ")); break
                except: pass
            while True:
                try: m=int(input(f"    Op{oid} machine (1-{M}): ")); break
                except: pass
            ops.append(Op(oid,d,m))
        jobs.append(Job(jid,ops,deps))
    return M,jobs

def ops_df(sol:List[Assign]):
    data=[{'Job':a.j,'Operation':a.o,'Machine':a.m,'Start':a.s,'End':a.e,'Duration':a.e-a.s} for a in sol]
    return pd.DataFrame(data).sort_values(['Job','Operation'])

def jobs_df(sol:List[Assign], jobs:List[Job]):
    rows=[]
    for job in jobs:
        asg=[a for a in sol if a.j==job.id]
        if not asg: continue
        s=min(a.s for a in asg)
        e=max(a.e for a in asg)
        rows.append({'Job ID':job.id,'Num Operations':len(asg),'Start Time':s,'End Time':e,'Total Duration':sum(a.e-a.s for a in asg),'Makespan':e-s})
    return pd.DataFrame(rows).sort_values('Job ID')

def print_gantt(sol:List[Assign], M:int, ms:int):
    print("\nGANTT:")
    bym={i:[] for i in range(1,M+1)}
    for a in sol: bym[a.m].append(a)
    for m in range(1,M+1):
        bym[m].sort(key=lambda x:x.s)
        line=f"M{m} |"
        cur=0
        for a in bym[m]:
            idle=a.s-cur
            if idle>0: line+= "."*idle
            label=f"[J{a.j}O{a.o}]"
            line+=label*(max(1,a.e-a.s))
            cur=a.e
        line+=f" | End:{cur}"
        print(line)
    print(f"Time 0 {' '*(max(0,ms-6))}{ms}")

# ---------- main ----------
def main():
    M,jobs=get_input()
    sched=Scheduler(M,jobs)
    best,ms=sched.solve()
    if best:
        print("\nOPERATIONS SCHEDULE (best):")
        df=ops_df(best)
        print(df.to_string(index=False))
        jf=jobs_df(best,jobs)
        print("\nJOBS SUMMARY:")
        print(jf.to_string(index=False))
        print(f"\nBest makespan: {ms}")
        print_gantt(best,M,ms)
        # save csv
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(f"ops_{ts}.csv",index=False)
        jf.to_csv(f"jobs_{ts}.csv",index=False)
        print(f"\nSaved CSV: ops_{ts}.csv , jobs_{ts}.csv")
    else:
        print("No solution found.")
    # complexity
    t=sched.tracker
    print(f"\nNodes explored: {t.nodes}, pruned: {t.pruned}, solutions: {t.sol}, time: {t.elapsed():.4f}s")

if __name__=="__main__":
    main()
