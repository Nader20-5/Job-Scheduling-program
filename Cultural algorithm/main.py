'''import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ast
import threading

# These modules should be in your project (provided by you)
import schedule
import operators
import cultural_algorithm

# We also include plotting and simulation helpers (compatible with your code)
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import copy

FINAL_POPULATION = 50
FINAL_GENERATIONS = 100


def simulate_schedule(schedule_chromosome, jobs_input, num_machines):
    """
    Simulate a chromosome and return a list of records and the makespan.
    Each record: dict(job, op_idx, machine, duration, start, end)
    """
    total_ops = sum(len(job) for job in jobs_input)
    if len(schedule_chromosome) != total_ops:
        raise ValueError(f"Chromosome length {len(schedule_chromosome)} doesn't match total operations {total_ops}.")

    machine_timers = [0] * num_machines
    job_timers = [0] * len(jobs_input)
    op_counters = [0] * len(jobs_input)

    records = []

    for idx, job_id in enumerate(schedule_chromosome):
        if not (0 <= job_id < len(jobs_input)):
            raise ValueError(f"Invalid job id {job_id} at position {idx}")

        op_idx = op_counters[job_id]
        if op_idx >= len(jobs_input[job_id]):
            raise ValueError(f"Job {job_id} has no operation {op_idx} (chromosome invalid).")

        machine_id, duration = jobs_input[job_id][op_idx]

        start_time = max(machine_timers[machine_id], job_timers[job_id])
        end_time = start_time + duration

        records.append({
            "job": job_id,
            "op_idx": op_idx,
            "machine": machine_id,
            "duration": duration,
            "start": start_time,
            "end": end_time
        })

        machine_timers[machine_id] = end_time
        job_timers[job_id] = end_time
        op_counters[job_id] += 1

    makespan = max(machine_timers) if machine_timers else 0
    return records, makespan


def plot_gantt(records, num_machines, title="Gantt Chart"):
    if not records:
        messagebox.showinfo("Gantt", "No records to plot.")
        return

    unique_jobs = sorted({r["job"] for r in records})
    cmap = plt.get_cmap("tab10")
    job_color = {job: cmap(i % 10) for i, job in enumerate(unique_jobs)}

    fig, ax = plt.subplots(figsize=(12, max(4, num_machines * 0.8)))

    bar_height = 0.6
    machine_gap = 1

    # plot each operation
    for r in records:
        m = r["machine"]
        start = r["start"]
        dur = r["duration"]
        job = r["job"]
        op_idx = r["op_idx"]
        color = job_color[job]

        y = m * machine_gap
        ax.barh(y, dur, left=start, height=bar_height, align="center", edgecolor='k', color=color)

        # label inside bar when possible
        label = f"job({job},{op_idx})"
        text_x = start + dur / 2
        ax.text(text_x, y, label, va='center', ha='center', color='white', fontsize=9, fontweight='bold')

    # configure y ticks so machine 0 is top (no inversion per your screenshot)
    yticks = [m * machine_gap for m in range(num_machines)]
    ylabels = [f"Machine {m}" for m in range(num_machines)]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)

    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.set_ylim(-machine_gap, num_machines * machine_gap)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    legend_handles = [Patch(facecolor=job_color[j], edgecolor='k', label=f"Job {j}") for j in unique_jobs]
    ax.legend(handles=legend_handles, loc='upper right')

    plt.tight_layout()
    plt.show()


class JobSchedulerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Job Scheduler - Cultural Algorithm GUI")

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0, sticky='nsew')

        # Inputs: num_machines and jobs_input (as Python list literal)
        ttk.Label(main, text="Number of machines:").grid(row=0, column=0, sticky='w')
        self.num_machines_var = tk.StringVar(value='2')
        ttk.Entry(main, textvariable=self.num_machines_var, width=10).grid(row=0, column=1, sticky='w')

        ttk.Label(main, text='Jobs input (Python list):').grid(row=1, column=0, columnspan=2, sticky='w', pady=(8,0))
        self.jobs_text = scrolledtext.ScrolledText(main, width=60, height=8)
        self.jobs_text.grid(row=2, column=0, columnspan=4, sticky='w')
        # Example placeholder matching your code's expected structure
        example = "[(0,3),(1,2)], [(1,4),(0,1)]"
        self.jobs_text.insert('1.0', f"# Example: [{example}]\n")

        # Chromosome entry (optional; if empty, random will be used)
        ttk.Label(main, text='Chromosome (space-separated job IDs) — optional:').grid(row=3, column=0, columnspan=2, sticky='w', pady=(8,0))
        self.chrom_entry = ttk.Entry(main, width=50)
        self.chrom_entry.grid(row=4, column=0, columnspan=3, sticky='w')

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(10,0), sticky='w')

        ttk.Button(btn_frame, text='Generate Random Chromosome', command=self.generate_random).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text='Run Cultural Algorithm', command=self.run_ca).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text='Simulate Chromosome & Plot', command=self.simulate_and_plot).grid(row=0, column=2, padx=4)

        # Output area
        ttk.Label(main, text='Output (table / status):').grid(row=6, column=0, columnspan=2, sticky='w', pady=(10,0))
        self.output_text = scrolledtext.ScrolledText(main, width=80, height=12)
        self.output_text.grid(row=7, column=0, columnspan=4)

    def _parse_jobs_input(self):
        raw = self.jobs_text.get('1.0', 'end').strip()
        # Allow users to paste a Python-list-like expression; ignore comments
        lines = [l for l in raw.splitlines() if not l.strip().startswith('#')]
        raw = '\n'.join(lines).strip()
        if not raw:
            raise ValueError('Jobs input is empty')
        # Ensure it's a proper list-like by wrapping brackets if needed
        try:
            jobs_input = ast.literal_eval(raw)
        except Exception:
            # Try to wrap if user provided comma-separated jobs without outer list
            try:
                jobs_input = ast.literal_eval('[' + raw + ']')
            except Exception as e:
                raise ValueError('Cannot parse jobs input. Provide a Python list of job operation lists.')
        # Validate format
        if not isinstance(jobs_input, list):
            raise ValueError('Jobs input must be a list')
        for job in jobs_input:
            if not isinstance(job, list) and not isinstance(job, tuple):
                raise ValueError('Each job must be a list or tuple of (machine,duration) pairs')
            # convert inner to list of tuples
        jobs_clean = [list(job) for job in jobs_input]
        return jobs_clean

    def generate_random(self):
        try:
            jobs = self._parse_jobs_input()
            # num_machines is not needed to create random chromosome in your schedule.create_random_schedule
            chrom = schedule.create_random_schedule(jobs)
            self.chrom_entry.delete(0, 'end')
            self.chrom_entry.insert(0, ' '.join(str(x) for x in chrom))
            self._write_output(f"Random chromosome generated: {chrom}")
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def run_ca(self):
        try:
            jobs = self._parse_jobs_input()
            num_machines = int(self.num_machines_var.get())
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return

        # Run the cultural algorithm in a thread to avoid blocking the GUI
        def ca_thread():
            self._write_output('Running Cultural Algorithm...')
            try:
                best_schedule, best_fitness = cultural_algorithm.solve_with_ca(jobs, num_machines)
                self._write_output(f'CA finished. Best fitness: {best_fitness}')
                self._write_output(f'Best schedule: {best_schedule}')
                # populate chromosome field with best
                self.chrom_entry.delete(0, 'end')
                self.chrom_entry.insert(0, ' '.join(str(x) for x in best_schedule))
            except Exception as e:
                self._write_output(f'Error during CA: {e}')

        threading.Thread(target=ca_thread, daemon=True).start()

    def simulate_and_plot(self):
        try:
            jobs = self._parse_jobs_input()
            num_machines = int(self.num_machines_var.get())
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return

        chrom_text = self.chrom_entry.get().strip()
        if chrom_text:
            try:
                chrom = [int(x) for x in chrom_text.split()]
            except Exception:
                messagebox.showerror('Error', 'Chromosome must be space-separated integers')
                return
        else:
            chrom = schedule.create_random_schedule(jobs)
            self._write_output(f'No chromosome provided — using random: {chrom}')

        # Simulate
        try:
            records, makespan = simulate_schedule(chrom, jobs, num_machines)
        except Exception as e:
            messagebox.showerror('Simulation error', str(e))
            return

        # print table to output box
        self._print_table_to_output(records)
        self._write_output(f'Makespan: {makespan}')

        # Plot Gantt
        plot_gantt(records, num_machines, title=f'Gantt Chart - Makespan {makespan}')

    def _print_table_to_output(self, records):
        lines = []
        headers = ['#','Job','Op','Machine','Start','End','Duration']
        lines.append(' | '.join(headers))
        for i, r in enumerate(sorted(records, key=lambda x: (x['start'], x['machine'])), start=1):
            lines.append(f"{i} | {r['job']} | {r['op_idx']} | {r['machine']} | {r['start']} | {r['end']} | {r['duration']}")
        self._write_output('\n'.join(lines))

    def _write_output(self, text):
        self.output_text.insert('end', str(text) + '\n')
        self.output_text.see('end')


if __name__ == '__main__':
    root = tk.Tk()
    app = JobSchedulerGUI(root)
    root.mainloop() '''




# -------------------------------------- streamlit --------------------------------------

import streamlit as st
import ast
import threading
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import copy

# your project modules (must be in same folder or importable)
import schedule
import cultural_algorithm

st.set_page_config(layout="wide", page_title="Job Scheduler - Streamlit")

st.title("Job Scheduler — Cultural Algorithm (Streamlit + Matplotlib)")

# --- Left column: Inputs
col1, col2 = st.columns([1, 1.4])

with col1:
    st.header("Inputs")

    num_machines_input = st.number_input(
        "Number of machines",
        min_value=1,
        value=2,
        step=1,
        help="Enter the number of distinct machines."
    )

    st.markdown("**Jobs input (Python list)** — format: `[[ (m,d), (m,d), ... ], [ ... ], ... ]`")
    example = "[[(0,3),(1,2)], [(1,4),(0,1)]]"
    jobs_raw = st.text_area(
        "Jobs input (paste Python list)",
        value=f"# Example: {example}\n{example}",
        height=160
    )

    st.markdown("**Chromosome (space-separated job IDs)** — optional. If empty, random will be used.")
    chrom_input = st.text_input("Chromosome (optional)", value="")

    st.markdown("**Actions**")
    generate_btn = st.button("Generate Random Chromosome")
    run_ca_btn = st.button("Run Cultural Algorithm (CA)")
    simulate_btn = st.button("Simulate Chromosome & Plot")

# --- Right column: Output
with col2:
    st.header("Output")
    output_area = st.empty()
    table_area = st.empty()
    plot_area = st.empty()


# --- Helpers (same logic as your Tkinter app)
def parse_jobs_input(text):
    # remove commented lines (#)
    lines = [l for l in text.splitlines() if not l.strip().startswith("#")]
    raw = "\n".join(lines).strip()
    if not raw:
        raise ValueError("Jobs input is empty.")
    # Try to parse literal
    try:
        jobs = ast.literal_eval(raw)
    except Exception:
        # try wrapping with [ ... ] if user omitted outer brackets
        try:
            jobs = ast.literal_eval("[" + raw + "]")
        except Exception:
            raise ValueError("Cannot parse jobs input. Provide a Python list of job operation lists.")
    # Validate structure
    if not isinstance(jobs, list):
        raise ValueError("Jobs input must be a list.")
    jobs_clean = []
    for job in jobs:
        if not (isinstance(job, list) or isinstance(job, tuple)):
            raise ValueError("Each job must be a list or tuple of (machine,duration) pairs.")
        inner = []
        for op in job:
            if not (isinstance(op, tuple) or isinstance(op, list)) or len(op) != 2:
                raise ValueError("Each operation must be a tuple/list (machine, duration).")
            machine, duration = int(op[0]), int(op[1])
            inner.append((machine, duration))
        jobs_clean.append(inner)
    return jobs_clean


def simulate_schedule(schedule_chromosome, jobs_input, num_machines):
    total_ops = sum(len(job) for job in jobs_input)
    if len(schedule_chromosome) != total_ops:
        raise ValueError(f"Chromosome length {len(schedule_chromosome)} doesn't match total operations {total_ops}.")

    machine_timers = [0] * num_machines
    job_timers = [0] * len(jobs_input)
    op_counters = [0] * len(jobs_input)

    records = []

    for idx, job_id in enumerate(schedule_chromosome):
        if not (0 <= job_id < len(jobs_input)):
            raise ValueError(f"Invalid job id {job_id} at position {idx}")

        op_idx = op_counters[job_id]
        if op_idx >= len(jobs_input[job_id]):
            raise ValueError(f"Job {job_id} has no operation {op_idx} (chromosome invalid).")

        machine_id, duration = jobs_input[job_id][op_idx]

        start_time = max(machine_timers[machine_id], job_timers[job_id])
        end_time = start_time + duration

        records.append({
            "job": job_id,
            "op_idx": op_idx,
            "machine": machine_id,
            "duration": duration,
            "start": start_time,
            "end": end_time
        })

        machine_timers[machine_id] = end_time
        job_timers[job_id] = end_time
        op_counters[job_id] += 1

    makespan = max(machine_timers) if machine_timers else 0
    return records, makespan


def plot_gantt_matplotlib(records, num_machines, title="Gantt Chart"):
    if not records:
        st.warning("No records to plot.")
        return

    unique_jobs = sorted({r["job"] for r in records})
    cmap = plt.get_cmap("tab10")
    job_color = {job: cmap(i % 10) for i, job in enumerate(unique_jobs)}

    fig, ax = plt.subplots(figsize=(12, max(4, num_machines * 0.8)))

    bar_height = 0.6
    machine_gap = 1

    # plot each operation
    for r in records:
        m = r["machine"]
        start = r["start"]
        dur = r["duration"]
        job = r["job"]
        op_idx = r["op_idx"]
        color = job_color[job]

        y = m * machine_gap
        ax.barh(y, dur, left=start, height=bar_height, align="center", edgecolor='k', color=color)

        # label inside bar when possible
        label = f"job({job},{op_idx})"
        text_x = start + dur / 2
        ax.text(text_x, y, label, va='center', ha='center', color='white', fontsize=9, fontweight='bold')

    # configure y ticks, machine 0 at top (no inversion)
    yticks = [m * machine_gap for m in range(num_machines)]
    ylabels = [f"Machine {m}" for m in range(num_machines)]
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)

    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.set_ylim(-machine_gap, num_machines * machine_gap)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    legend_handles = [Patch(facecolor=job_color[j], edgecolor='k', label=f"Job {j}") for j in unique_jobs]
    ax.legend(handles=legend_handles, loc='upper right')

    plt.tight_layout()
    return fig


# --- UI Actions

def write_output(text):
    output_area.text(text)


# Generate random chromosome action
if generate_btn:
    try:
        jobs_parsed = parse_jobs_input(jobs_raw)
        chrom = schedule.create_random_schedule(jobs_parsed)
        st.success("Random chromosome generated.")
        st.session_state['chromosome'] = chrom
        # show it in the input box
        st.experimental_set_query_params()  # no-op to allow UI update if necessary
        chrom_input = " ".join(str(x) for x in chrom)
        st.write("Random chromosome:", chrom)
    except Exception as e:
        st.error(str(e))

# Run cultural algorithm action (runs in background thread to keep UI responsive)
if run_ca_btn:
    try:
        jobs_parsed = parse_jobs_input(jobs_raw)
        num_machines = int(num_machines_input)
    except Exception as e:
        st.error(str(e))
    else:
        st.info("Running Cultural Algorithm (this runs in the server process).")

        # run synchronously (Streamlit reruns are single-threaded in server mode).
        try:
            best_schedule, best_fitness = cultural_algorithm.solve_with_ca(jobs_parsed, num_machines)
            st.success(f"CA finished. Best fitness: {best_fitness}")
            st.write("Best schedule:", best_schedule)
            st.session_state['chromosome'] = best_schedule
        except Exception as e:
            st.error(f"Error during CA: {e}")

# Simulate & Plot
if simulate_btn:
    try:
        jobs_parsed = parse_jobs_input(jobs_raw)
        num_machines = int(num_machines_input)
    except Exception as e:
        st.error(str(e))
    else:
        # Determine chromosome to use
        chrom_text = chrom_input.strip()
        if chrom_text:
            try:
                chrom = [int(x) for x in chrom_text.split()]
            except Exception:
                st.error("Chromosome must be space-separated integers.")
                st.stop()
        else:
            # use any saved chromosome from CA/random generation, or create random
            chrom = st.session_state.get('chromosome', None)
            if chrom is None:
                chrom = schedule.create_random_schedule(jobs_parsed)
                st.write("No chromosome provided — using random:", chrom)
            else:
                st.write("Using chromosome from session:", chrom)

        # simulate
        try:
            records, makespan = simulate_schedule(chrom, jobs_parsed, num_machines)
        except Exception as e:
            st.error(f"Simulation error: {e}")
            st.stop()

        # show table
        import pandas as pd
        df = pd.DataFrame(sorted(records, key=lambda x: (x['start'], x['machine'])))
        table_area.dataframe(df.assign(**{"start": df["start"].astype(int), "end": df["end"].astype(int)}))

        st.write(f"**Makespan:** {makespan}")

        # plot gantt
        fig = plot_gantt_matplotlib(records, num_machines, title=f"Gantt Chart - Makespan {makespan}")
        if fig:
            plot_area.pyplot(fig)
