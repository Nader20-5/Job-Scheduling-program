# job_scheduler.py
import copy
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class Op:
    id: int
    dur: int
    mach: int

@dataclass
class Job:
    id: int
    ops: List[Op]
    deps: List[int]
    pri: int = 0

    def next_op(self, prog):
        return self.ops[prog] if prog < len(self.ops) else None

    def complete(self, prog):
        return prog >= len(self.ops)

@dataclass
class Assign:
    j: int
    o: int
    m: int
    s: int
    e: int

class Scheduler:
    def __init__(self, machines:int, jobs:List[Job]):
        self.machines = machines
        self.jobs = jobs
        self.best: Optional[List[Assign]] = None
        self.best_ms = 10**9
        self.all_sols = []

        for j in self.jobs:
            j.pri = -len(j.deps)

    def simple_schedule(self):
        """
        Simple sequential scheduler (for GUI demo)
        """
        timeline = [0]*self.machines
        schedule = []
        for job in self.jobs:
            for op in job.ops:
                m_idx = op.mach-1
                start = timeline[m_idx]
                end = start + op.dur
                timeline[m_idx] = end
                schedule.append(Assign(job.id, op.id, op.mach, start, end))
        makespan = max(timeline)
        return schedule, makespan
