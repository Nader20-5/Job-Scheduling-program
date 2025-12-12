import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt
import time

# Import your algorithm modules
from backtrack_algorithm.backtrack import Scheduler, Job, Op
from cultural_algorithm.cultural_algorithm import solve_with_ca

class JobSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scheduling Program - Comparison Mode")
        self.root.geometry("900x700")

        self.current_frame = None
        # Start directly at the input page
        self.show_input_page()

    # ================= INPUT PAGE =================
    def show_input_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        tk.Label(frame, text="Job Scheduler Comparison", font=("Arial", 18, "bold")).pack(pady=10)

        # Input frame
        input_frame = tk.Frame(frame)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Machines:", font=("Arial", 12)).grid(row=0, column=0)
        self.entry_machines = tk.Entry(input_frame, width=5)
        self.entry_machines.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Jobs:", font=("Arial", 12)).grid(row=1, column=0)
        self.entry_jobs = tk.Entry(input_frame, width=5)
        self.entry_jobs.grid(row=1, column=1, padx=5)

        tk.Button(frame, text="Create Job Inputs", font=("Arial", 12),
                  command=self.create_job_frames).pack(pady=10)

        self.job_frames_container = None
        self.job_frames = []

        # Run Button
        self.run_button = tk.Button(frame, text="Run & Compare Algorithms", font=("Arial", 12, "bold"), bg="#dddddd",
                                    command=self.run_algorithms_thread)
        self.run_button.pack(pady=10)

    # ================= CREATE JOB FRAMES =================
    def create_job_frames(self):
        try:
            self.num_machines = int(self.entry_machines.get())
            self.num_jobs = int(self.entry_jobs.get())
        except:
            messagebox.showerror("Error", "Enter valid machine and job numbers.")
            return

        if self.job_frames_container:
            self.job_frames_container.destroy()

        self.job_frames_container = tk.Frame(self.current_frame)
        self.job_frames_container.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(self.job_frames_container)
        scrollbar = tk.Scrollbar(self.job_frames_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.job_frames = []
        for j in range(self.num_jobs):
            frame = tk.LabelFrame(scroll_frame, text=f"Job {j}", padx=10, pady=10, font=("Arial", 12))
            frame.pack(pady=10, fill="x")

            ops_list = []

            tk.Button(frame, text="Add Operation", bg="#cce5ff",
                      command=lambda k=j: self.add_operation_row(k), font=("Arial", 10)).pack(pady=5)

            self.job_frames.append({"frame": frame, "ops": ops_list})

    # ================= ADD OPERATION =================
    def add_operation_row(self, job_index):
        jf = self.job_frames[job_index]
        frame = jf["frame"]

        row_frame = tk.Frame(frame)

        tk.Label(row_frame, text="Machine:", font=("Arial", 10)).pack(side="left", padx=5)
        m_entry = tk.Entry(row_frame, width=5)
        m_entry.pack(side="left")

        tk.Label(row_frame, text="Duration:", font=("Arial", 10)).pack(side="left", padx=5)
        d_entry = tk.Entry(row_frame, width=5)
        d_entry.pack(side="left")

        row_frame.pack(pady=3, anchor="w")

        jf["ops"].append((m_entry, d_entry))

    # ================= RUN ALGORITHM THREAD =================
    def run_algorithms_thread(self):
        self.run_button.config(state="disabled")
        t = threading.Thread(target=self.run_comparison)
        t.start()

    # ================= RUN COMPARISON =================
    def run_comparison(self):
        try:
            jobs_input = []
            for jf in self.job_frames:
                job_ops = []
                for m_entry, d_entry in jf["ops"]:
                    m = int(m_entry.get())
                    d = int(d_entry.get())
                    job_ops.append((m, d))
                jobs_input.append(job_ops)

            if any(len(job) == 0 for job in jobs_input):
                self.root.after(0, lambda: messagebox.showerror("Error", "All jobs must have at least one operation."))
                return

            # --- Run Backtracking ---
            start_time = time.time()
            job_objects = []
            for j_index, job_ops in enumerate(jobs_input):
                ops_objs = [Op(i, d, m) for i, (m, d) in enumerate(job_ops)]
                job_objects.append(Job(j_index, ops_objs))
            
            backtrack_scheduler = Scheduler(self.num_machines, job_objects)
            backtrack_sol, backtrack_makespan = backtrack_scheduler.solve()
            backtrack_time = time.time() - start_time
            backtrack_nodes = backtrack_scheduler.tracker.nodes
            backtrack_depth = backtrack_scheduler.tracker.max_depth

            # --- Run Cultural ---
            # Note: Cultural algo usually prints to stdout, we might want to capture it or just run it.
            # Measuring time externally as well.
            start_time = time.time()
            cultural_schedule, cultural_makespan, cultural_avg = solve_with_ca(jobs_input, self.num_machines)
            cultural_time = time.time() - start_time
            # Cultural algo in the provided file does not expose generation count easily unless we parse stdout or modify it.
            # However, the file has a constant FINAL_GENERATIONS = 100.
            # We can use that as a proxy for "Recursion Count" or just say N/A or Fixed Generations.
            # But wait, the user asked for "how many recursion used". Cultural is iterative. 
            # Backtracking is recursive. So "Nodes" is the correct metric for Backtracking.
            # For Cultural, we can show "Generations" (fixed 100) or "Evaluations" (Pop * Gen).
            cultural_nodes = "100 Gens" # Placeholder for now

            results = {
                "Backtrack": {
                    "makespan": backtrack_makespan,
                    "time": backtrack_time,
                    "recursion": backtrack_nodes,
                    "depth": backtrack_depth,
                    "schedule": backtrack_sol,
                    "avg_fitness": "-", 
                    "type": "backtrack"
                },
                "Cultural": {
                    "makespan": cultural_makespan,
                    "time": cultural_time,
                    "recursion": cultural_nodes,
                    "depth": "-",
                    "schedule": cultural_schedule,
                    "avg_fitness": f"{cultural_avg:.2f}",
                    "type": "cultural"
                }
            }

            self.root.after(0, lambda: self.show_results_window(results, jobs_input))

        except Exception as e:
            print(e)
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.run_button.config(state="normal"))

    # ================= SHOW RESULTS =================
    def show_results_window(self, results, jobs_input):
        result_window = tk.Toplevel(self.root)
        result_window.title("Comparison Results")
        result_window.geometry("1400x600")

        # Table Frame
        table_frame = tk.Frame(result_window)
        table_frame.pack(pady=20)

        # Headers
        headers = ["Algorithm", "Best Fitness (Makespan)", "Avg Fitness", "Time (s)", "Recursion Times", "Depth Level"]
        for i, h in enumerate(headers):
            tk.Label(table_frame, text=h, font=("Arial", 12, "bold"), borderwidth=1, relief="solid", width=20).grid(row=0, column=i)

        # Data Row 1 (Backtrack)
        b_res = results["Backtrack"]
        tk.Label(table_frame, text="Backtracking", font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=0)
        tk.Label(table_frame, text=str(b_res["makespan"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=1)
        tk.Label(table_frame, text=str(b_res["avg_fitness"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=2)
        tk.Label(table_frame, text=f"{b_res['time']:.4f}", font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=3)
        tk.Label(table_frame, text=str(b_res["recursion"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=4)
        tk.Label(table_frame, text=str(b_res["depth"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=1, column=5)
        
        # Data Row 2 (Cultural)
        c_res = results["Cultural"]
        tk.Label(table_frame, text="Cultural", font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=0)
        tk.Label(table_frame, text=str(c_res["makespan"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=1)
        tk.Label(table_frame, text=str(c_res["avg_fitness"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=2)
        tk.Label(table_frame, text=f"{c_res['time']:.4f}", font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=3)
        tk.Label(table_frame, text=str(c_res["recursion"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=4)
        tk.Label(table_frame, text=str(c_res["depth"]), font=("Arial", 12), borderwidth=1, relief="solid", width=20).grid(row=2, column=5)


        # Gantt Button
        tk.Button(result_window, text="Show Gantt Charts", font=("Arial", 14), bg="#dddddd",
                  command=lambda: self.show_combined_gantt(results, jobs_input)).pack(pady=20)

    # ================= COMBINED GANTT CHART =================
    def show_combined_gantt(self, results, jobs_input):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        plt.subplots_adjust(hspace=0.4)

        # Backtrack Plot
        b_res = results["Backtrack"]
        if b_res["schedule"] is None:
            ax1.text(0.5, 0.5, "No Solution Found", ha='center')
        else:
            makespan = b_res["makespan"]
            for a in b_res["schedule"]:
                ax1.barh(a.m, a.e - a.s, left=a.s, height=0.4, align='center', color='skyblue', edgecolor='black')
                ax1.text(a.s + (a.e - a.s)/2, a.m, f"J{a.j}O{a.o}", ha='center', va='center', fontsize=8)
            ax1.set_title(f"Backtracking (Makespan={makespan}, Nodes={b_res['recursion']})")
            ax1.set_xlabel("Time")
            ax1.set_ylabel("Machine")
            ax1.set_yticks(range(self.num_machines))
            ax1.invert_yaxis()

        # Cultural Plot
        c_res = results["Cultural"]
        schedule_indices = c_res["schedule"] # list of job indices
        makespan = c_res["makespan"]
        
        machine_timers = [0] * self.num_machines
        job_timers = [0] * len(jobs_input)
        op_count = [0] * len(jobs_input)

        for job in schedule_indices:
            # We need to find which op this is. The schedule implies an order of operations? 
            # Looking at cultural_algorithm.py logic:
            # It seems schedule is a list of job IDs. It iterates and schedules the *next available operation* for that job?
            # Let's re-verify how cultural_algorithm.py constructs the schedule to be sure.
            # In show_gantt_cultural (original GUI.py):
            # for job in schedule:
            #    op_id = op_count[job]
            #    machine, duration = jobs_input[job][op_id]
            #    ...
            # So yes, it just picks the next op for that job.
            
            if op_count[job] < len(jobs_input[job]):
                op_id = op_count[job]
                machine, duration = jobs_input[job][op_id]
                start = max(machine_timers[machine], job_timers[job])
                end = start + duration
                
                ax2.barh(machine, duration, left=start, height=0.4, align='center', color='lightgreen', edgecolor='black')
                ax2.text(start + duration/2, machine, f"J{job}O{op_id}", ha='center', va='center', fontsize=8)
                
                machine_timers[machine] = end
                job_timers[job] = end
                op_count[job] += 1

        ax2.set_title(f"Cultural Algorithm (Makespan={makespan})")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Machine")
        ax2.set_yticks(range(self.num_machines))
        ax2.invert_yaxis()

        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = JobSchedulerApp(root)
    root.mainloop()
