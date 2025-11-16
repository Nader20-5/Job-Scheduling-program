''''import schedule
import operators
import random
import copy

# --- 1. Define a Simple Problem to Solve ---
# We have 2 machines: Machine 0 and Machine 1
NUM_MACHINES = 2

# We have 2 jobs
# Job 0: Op0(M0, 3hr), Op1(M1, 2hr)
# Job 1: Op0(M1, 4hr), Op1(M0, 1hr)
JOBS_INPUT = [
    [(0, 3), (1, 2)],  # Job 0
    [(1, 4), (0, 1)]   # Job 1
]

# --- 2. A Function to PRINT a Schedule Trace ---
# This is an "advanced" version of your calculate_fitness function.
# It does the same simulation but *prints* every step.

def print_schedule_trace(schedule_chromosome, jobs_input, num_machines):
    """
    Runs the simulation and prints a detailed step-by-step trace.
    """
    print("\n--- Tracing Schedule Simulation ---")
    print(f"  Schedule (Priority): {schedule_chromosome}")
    
    machine_timers = [0] * num_machines
    job_timers = [0] * len(jobs_input)
    operation_counters = [0] * len(jobs_input)
    
    print(f"  Initial State:")
    print(f"    Machine Timers: {machine_timers}")
    print(f"    Job Timers:     {job_timers}")
    print("-" * 20)

    for job_id in schedule_chromosome:
        print(f"  Processing next in priority list: Job {job_id}")
        
        op_index = operation_counters[job_id]
        op = jobs_input[job_id][op_index]
        machine_id, duration = op
        
        print(f"    > Task: Job {job_id}, Op {op_index} (Needs Machine {machine_id}, Duration {duration})")
        
        machine_ready_time = machine_timers[machine_id]
        job_ready_time = job_timers[job_id]
        
        print(f"    > Checking Constraints:")
        print(f"    >   Machine {machine_id} is free at: {machine_ready_time}")
        print(f"    >   Job {job_id} is free at:     {job_ready_time} (waiting for its previous op)")
        
        start_time = max(machine_ready_time, job_ready_time)
        end_time = start_time + duration
        
        print(f"    > Decision: Start Time = max({machine_ready_time}, {job_ready_time}) = {start_time}")
        print(f"    >           End Time = {start_time} + {duration} = {end_time}")
        
        # Update timers
        machine_timers[machine_id] = end_time
        job_timers[job_id] = end_time
        operation_counters[job_id] += 1
        
        print(f"    > New State:")
        print(f"    >   Machine Timers: {machine_timers}")
        print(f"    >   Job Timers:     {job_timers}")
        print("-" * 20)


    makespan = max(machine_timers)
    print(f"  --- Simulation Complete ---")
    print(f"  Final Machine Timers: {machine_timers}")
    print(f"  Final Makespan (Fitness): {makespan}")

# --- 3. Test Each Function Individually ---

print("--- 1. Testing schedule.create_random_schedule ---")
# We just need jobs_input, not num_machines
random_chrom = schedule.create_random_schedule(JOBS_INPUT)
print(f"   Input (Jobs): {JOBS_INPUT}")
print(f"   Output (Random Chromosome): {random_chrom}")
print("-" * 30)


print("--- 2. Testing schedule.calculate_fitness ---")
# Let's test two *known* schedules to see the fitness difference
sched_a = [0, 1, 0, 1]  # Job 0 -> Job 1 -> Job 0 -> Job 1
sched_b = [1, 0, 0, 1]  # Job 1 -> Job 0 -> Job 0 -> Job 1

fitness_a = schedule.calculate_fitness(sched_a, JOBS_INPUT, NUM_MACHINES)
fitness_b = schedule.calculate_fitness(sched_b, JOBS_INPUT, NUM_MACHINES)
print(f"   Schedule A {sched_a} -> Fitness: {fitness_a}")
print(f"   Schedule B {sched_b} -> Fitness: {fitness_b}")
print("-" * 30)


print("--- 3. Testing operators.selection ---")
# Create a dummy population and scores
dummy_pop = [[0,1,0,1], [1,0,1,0], [0,0,1,1]]
dummy_scores = [10, 7, 12] # Score 7 is the best (lowest)
print(f"   Population: {dummy_pop}")
print(f"   Scores:     {dummy_scores}")

winner = operators.selection(dummy_pop, dummy_scores)
print(f"   Winner (Best Score): {winner}")
print("-" * 30)


print("--- 4. Testing operators.crossover ---")
parent1 = [0, 0, 1, 1]
parent2 = [1, 1, 0, 0]
print(f"   Parent 1:    {parent1}")
print(f"   Parent 2:    {parent2}")
# Note: Crossover is random, so the child will be different each time
child = operators.crossover(parent1, parent2)
print(f"   Child (OX1): {child}  (Is it a valid 2x0, 2x1 permutation? Yes!)")
print("-" * 30)


print("--- 5. Testing operators.mutation ---")
# We use a 100% mutation rate for this test
chrom_before = [0, 1, 0, 1]
# We pass a dummy belief_space, as our simple mutation doesn't use it
dummy_belief = {} 
print(f"   Chromosome Before: {chrom_before}")
chrom_after = operators.mutation(chrom_before, dummy_belief, mutation_rate=1.0)
print(f"   Chromosome After:  {chrom_after} (Should have two items swapped)")
print("-" * 30)


# --- 6. Run the Detailed Print Trace ---
# We'll trace the two schedules from Step 2 to see *why* they have
# different fitness scores.

print_schedule_trace(sched_a, JOBS_INPUT, NUM_MACHINES)
print_schedule_trace(sched_b, JOBS_INPUT, NUM_MACHINES)'''