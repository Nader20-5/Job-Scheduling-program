# app.py
import streamlit as st
from job_scheduler import Op, Job, Scheduler
import pandas as pd
import matplotlib.pyplot as plt

# ----------------- Input Page -----------------
def input_page():
    st.title("Job Scheduling Inputs")

    M = st.number_input("Number of Machines (2-10)", min_value=2, max_value=10, value=3)
    J = st.number_input("Number of Jobs (1-10)", min_value=1, max_value=10, value=3)

    jobs = []
    for jid in range(1, J+1):
        st.subheader(f"Job {jid}")
        deps = []
        if jid > 1:
            raw = st.text_input(f"  Dependencies for Job {jid} (comma separated IDs < {jid})", key=f"dep{jid}")
            if raw:
                deps = [int(x.strip()) for x in raw.split(",") if x.strip()]
        nops = st.number_input(f"  Number of operations for Job {jid} (1-6)", min_value=1, max_value=6, key=f"nops{jid}")
        ops = []
        for oid in range(1, nops+1):
            dur = st.number_input(f"    Op{oid} duration (1-20)", min_value=1, max_value=20, key=f"d{jid}_{oid}")
            mach = st.number_input(f"    Op{oid} machine (1-{M})", min_value=1, max_value=M, key=f"m{jid}_{oid}")
            ops.append(Op(oid, dur, mach))
        jobs.append(Job(jid, ops, deps))
    return M, jobs

# ----------------- Plotting -----------------
def plot_schedule(schedule, M, makespan):
    st.subheader("Gantt Chart")
    colors = plt.cm.tab20.colors
    fig, ax = plt.subplots(figsize=(10, M))

    for a in schedule:
        ax.barh(a.m, a.e - a.s, left=a.s, color=colors[(a.j-1) % len(colors)], edgecolor='black')
        ax.text(a.s + (a.e - a.s)/2, a.m, f"J{a.j}O{a.o}", ha='center', va='center', color='white', fontsize=8)

    ax.set_yticks(range(1, M+1))
    ax.set_yticklabels([f"Machine {i}" for i in range(1, M+1)])
    ax.set_xlabel("Time")
    ax.set_ylabel("Machines")
    ax.set_title(f"Gantt Chart (Makespan: {makespan})")
    st.pyplot(fig)

    st.subheader("Schedule Table")
    df = pd.DataFrame([{'Job': a.j, 'Operation': a.o, 'Machine': a.m, 'Start': a.s, 'End': a.e, 'Duration': a.e-a.s} for a in schedule])
    st.dataframe(df)

# ----------------- Main -----------------
def main():
    st.sidebar.title("Pages")
    page = st.sidebar.radio("Select Page", ["Inputs & Run", "Schedule Plot"])

    if page == "Inputs & Run":
        st.session_state['M'], st.session_state['jobs'] = input_page()
        if st.button("Run Scheduler"):
            scheduler = Scheduler(st.session_state['M'], st.session_state['jobs'])
            schedule, makespan = scheduler.simple_schedule()
            st.session_state['schedule'] = schedule
            st.session_state['makespan'] = makespan
            st.success(f"Scheduler finished! Makespan: {makespan}")
            st.experimental_rerun()

    elif page == "Schedule Plot":
        if 'schedule' not in st.session_state:
            st.warning("Run the scheduler first on the Inputs page!")
        else:
            plot_schedule(st.session_state['schedule'], st.session_state['M'], st.session_state['makespan'])

if __name__=="__main__":
    main()
