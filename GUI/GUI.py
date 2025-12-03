import tkinter as tk
from tkinter import ttk, messagebox
import threading
import matplotlib.pyplot as plt

# Import your algorithm modules
from backtrack_algorithm.backtrack import Scheduler, Job, Op
from cultural_algorithm.cultural_algorithm import solve_with_ca


class JobSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scheduling Program")
        self.root.geometry("800x700")

        self.current_frame = None
        self.show_main_menu()

    # ================= MAIN MENU =================
    def show_main_menu(self):
        if self.current_frame:
            self.current_frame.destroy()
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        tk.Label(frame, text="Select Algorithm", font=("Arial", 20, "bold")).pack(pady=20)

        tk.Button(frame, text="Backtracking Algorithm", font=("Arial", 14),
                  command=self.show_backtrack_page).pack(pady=20)
        tk.Button(frame, text="Cultural Algorithm", font=("Arial", 14),
                  command=self.show_cultural_page).pack(pady=20)

    # ================= BACKTRACK PAGE =================
    def show_backtrack_page(self):
        self.show_algorithm_page(algorithm="backtrack")

    # ================= CULTURAL PAGE =================
    def show_cultural_page(self):
        self.show_algorithm_page(algorithm="cultural")

    # ================= ALGORITHM PAGE =================
    def show_algorithm_page(self, algorithm):
        if self.current_frame:
            self.current_frame.destroy()
        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

        self.algorithm = algorithm

        tk.Label(frame, text=f"{algorithm.capitalize()} Algorithm Scheduler", font=("Arial", 18, "bold")).pack(pady=10)

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
        self.run_button = tk.Button(frame, text="Run Scheduler", font=("Arial", 12),
                                    command=self.run_algorithm_thread)
        self.run_button.pack(pady=10)

        # Back Button
        tk.Button(frame, text="Back", font=("Arial", 12),
                  command=self.show_main_menu).pack(pady=10)

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
    def run_algorithm_thread(self):
        self.run_button.config(state="disabled")
        t = threading.Thread(target=self.run_algorithm)
        t.start()

    # ================= RUN ALGORITHM =================
    def run_algorithm(self):
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

            if self.algorithm == "backtrack":
                job_objects = []
                for j_index, job_ops in enumerate(jobs_input):
                    ops_objs = [Op(i, d, m) for i, (m, d) in enumerate(job_ops)]
                    job_objects.append(Job(j_index, ops_objs))
                scheduler = Scheduler(self.num_machines, job_objects)
                solution, makespan = scheduler.solve()
                if solution is None:
                    self.root.after(0, lambda: messagebox.showinfo("Result", "No valid schedule found."))
                    return
                self.root.after(0, lambda: self.show_gantt_backtrack(solution, makespan))
            else:
                best_schedule, makespan = solve_with_ca(jobs_input, self.num_machines)
                self.root.after(0, lambda: self.show_gantt_cultural(best_schedule, makespan, jobs_input))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.run_button.config(state="normal"))

    # ================= GANTT CHART BACKTRACK =================
    def show_gantt_backtrack(self, solution, makespan):
        fig, ax = plt.subplots(figsize=(12, 5))
        for a in solution:
            ax.barh(a.m, a.e - a.s, left=a.s, height=0.4)
            ax.text(a.s, a.m, f"J{a.j}O{a.o}", va="center")
        ax.set_title(f"Backtracking Schedule (Makespan={makespan})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Machine")
        ax.invert_yaxis()
        plt.show()

    # ================= GANTT CHART CULTURAL =================
    def show_gantt_cultural(self, schedule, makespan, jobs_input):
        fig, ax = plt.subplots(figsize=(12, 5))
        machine_timers = [0] * self.num_machines
        job_timers = [0] * len(jobs_input)
        op_count = [0] * len(jobs_input)
        for job in schedule:
            op_id = op_count[job]
            machine, duration = jobs_input[job][op_id]
            start = max(machine_timers[machine], job_timers[job])
            end = start + duration
            ax.barh(machine, duration, left=start)
            ax.text(start, machine, f"J{job}O{op_id}", va="center")
            machine_timers[machine] = end
            job_timers[job] = end
            op_count[job] += 1
        ax.set_title(f"Cultural Algorithm Schedule (Makespan={makespan})")
        ax.set_xlabel("Time")
        ax.set_ylabel("Machine")
        ax.invert_yaxis()
        plt.show()


# ================== MAIN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = JobSchedulerApp(root)
    root.mainloop()
