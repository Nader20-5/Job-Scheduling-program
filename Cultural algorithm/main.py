import schedule
import operators
import random
import copy
import matplotlib.pyplot as plt

# -------------------------
# Helpers: Simulation + Outputs
# -------------------------

def simulate_schedule(schedule_chromosome, jobs_input, num_machines):
    """
    Simulate the given chromosome (priority list) and return:
      - records: list of dicts {job, op_idx, machine, duration, start, end}
      - makespan
    This does not print step-by-step; it collects results for table + gantt.
    """
    # sanity checks
    total_ops = sum(len(job) for job in jobs_input)
    if len(schedule_chromosome) != total_ops:
        raise ValueError(
            f"Chromosome length {len(schedule_chromosome)} doesn't match total operations {total_ops}."
        )
    # initialize timers/counters
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

        # determine start & end
        start_time = max(machine_timers[machine_id], job_timers[job_id])
        end_time = start_time + duration

        # record
        records.append({
            "job": job_id,
            "op_idx": op_idx,
            "machine": machine_id,
            "duration": duration,
            "start": start_time,
            "end": end_time
        })

        # update timers
        machine_timers[machine_id] = end_time
        job_timers[job_id] = end_time
        op_counters[job_id] += 1

    makespan = max(machine_timers) if machine_timers else 0
    return records, makespan


def print_table(records):
    """Print a neat table of operation records (sorted by start time)."""
    records_sorted = sorted(records, key=lambda r: (r["start"], r["machine"]))
    headers = ["#","Job","Op","Machine","Start","End","Duration"]
    line = "-" * 62
    print("\n" + line)
    print(f"{headers[0]:>3}  {headers[1]:>3}  {headers[2]:>3}  {headers[3]:>7}  {headers[4]:>6}  {headers[5]:>6}  {headers[6]:>8}")
    print(line)
    for i, r in enumerate(records_sorted, start=1):
        print(f"{i:3d}  {r['job']:3d}  {r['op_idx']:3d}  {r['machine']:7d}  {r['start']:6d}  {r['end']:6d}  {r['duration']:8d}")
    print(line + "\n")


def plot_gantt(records, num_machines, title="Gantt Chart"):
    """
    Plot a Gantt chart using matplotlib.
    machines on y-axis, time on x-axis.
    """
    if not records:
        print("No records to plot.")
        return

    # Map job -> color using tab10 colormap
    unique_jobs = sorted({r["job"] for r in records})
    cmap = plt.get_cmap("tab10")
    job_color = {job: cmap(i % 10) for i, job in enumerate(unique_jobs)}

    fig, ax = plt.subplots(figsize=(10, max(4, num_machines * 0.8)))
    yticks = []
    ytick_labels = []

    # Plot each operation as a horizontal bar at y=machine_id
    height = 0.6
    for r in records:
        m = r["machine"]
        start = r["start"]
        dur = r["duration"]
        job = r["job"]
        op_idx = r["op_idx"]
        color = job_color[job]

        ax.barh(m, dur, left=start, height=height, align="center", edgecolor='k', color=color)
        # label inside bar if there's space, otherwise above bar
        label = f"J{job}-O{op_idx}"
        text_x = start + dur / 2
        ax.text(text_x, m, label, va="center", ha="center", color="white", fontsize=9, fontweight="bold")

        if m not in yticks:
            yticks.append(m)
            ytick_labels.append(f"Machine {m}")

    ax.set_yticks(sorted(yticks))
    ax.set_yticklabels([f"Machine {m}" for m in sorted(yticks)])
    ax.invert_yaxis()  # optional: put machine 0 at top
    ax.set_xlabel("Time")
    ax.set_title(title)

    # legend for jobs
    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=job_color[j], edgecolor='k', label=f"Job {j}") for j in unique_jobs]
    ax.legend(handles=legend_handles, loc='upper right', bbox_to_anchor=(1.15, 1.0))

    plt.tight_layout()
    plt.show()


# -------------------------
# Main: Inputs and Tests (keeps your earlier flow)
# -------------------------

def get_user_input():
    print("\n=== JOB SHOP INPUT SETUP ===")
    num_machines = int(input("Enter number of machines: "))
    num_jobs = int(input("Enter number of jobs: "))

    jobs_input = []
    for j in range(num_jobs):
        print(f"\n-- Job {j} --")
        num_ops = int(input(f"Enter number of operations for Job {j}: "))
        job_ops = []
        for op in range(num_ops):
            machine = int(input(f"  Operation {op} → Machine ID: "))
            duration = int(input(f"  Operation {op} → Duration (integer): "))
            job_ops.append((machine, duration))
        jobs_input.append(job_ops)
    return num_machines, jobs_input


def main():
    print("\n=== MENU ===")
    print("1. Enter new Job Shop input")
    print("2. Use the default example (2 jobs, 2 machines)")
    choice = input("Choose option (1 or 2): ").strip()

    if choice == "1":
        NUM_MACHINES, JOBS_INPUT = get_user_input()
    else:
        NUM_MACHINES = 2
        JOBS_INPUT = [
            [(0, 3), (1, 2)],
            [(1, 4), (0, 1)]
        ]
        print("\nUsing default example...")

    # Create a random chromosome using your schedule module (keeps compatibility)
    random_chrom = schedule.create_random_schedule(JOBS_INPUT)
    print(f"\nRandom chromosome generated: {random_chrom}")

    # Ask user to choose a chromosome to trace or use random
    trace_choice = input("Enter schedule manually? (y/n): ").strip().lower()
    if trace_choice == "y":
        trace_list = input("Enter chromosome (space-separated job IDs, e.g. '0 1 0 1'): ").split()
        trace_chrom = [int(x) for x in trace_list]
    else:
        trace_chrom = random_chrom
        print("Using random chromosome.")

    # Simulate (collect records)
    try:
        records, makespan = simulate_schedule(trace_chrom, JOBS_INPUT, NUM_MACHINES)
    except ValueError as e:
        print("Error during simulation:", e)
        return

    print(f"\nSimulation complete. Makespan: {makespan}")

    # Print table
    print_table(records)

    # Plot Gantt chart
    plot_gantt(records, NUM_MACHINES, title=f"Gantt Chart - Makespan {makespan}")

    # Keep old tests (selection, crossover, mutation) for convenience
    print("\n--- Quick tests of operators (unchanged) ---")
    try:
        fitness_rand = schedule.calculate_fitness(trace_chrom, JOBS_INPUT, NUM_MACHINES)
        print(f"Fitness of traced chromosome: {fitness_rand}")
    except Exception as e:
        print("Skipping fitness test (error):", e)

    dummy_pop = [[0,1,0,1], [1,0,1,0], [0,0,1,1]]
    dummy_scores = [10, 7, 12]
    print("Selection test ->", operators.selection(dummy_pop, dummy_scores))
    print("Crossover test ->", operators.crossover([0,0,1,1], [1,1,0,0]))
    print("Mutation test ->", operators.mutation([0,1,0,1], {}, mutation_rate=1.0))


if __name__ == "__main__":
    main()
