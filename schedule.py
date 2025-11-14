import random

#Loops and assigns each job to a machine
def create_random_schedule(jobs , num_machines):
    schedule = []
    job_num = len(jobs)
    for _ in range(job_num):
        assigned_machine = random.randint(0, num_machines-1)
        schedule.append(assigned_machine)

    return schedule

#loops and calculate score to each schedule
def calculate_fitness(schedule , jobs , num_machines):

    machine_timers = [0] * num_machines
    for job_indx , assigned_machine in enumerate(schedule):
        job_duration = jobs[job_indx]['duration']
        machine_timers[assigned_machine] += job_duration

    makespan = max(machine_timers)
    return makespan
