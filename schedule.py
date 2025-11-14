import random

def create_random_schedule(jobs , num_machines):
    schedule = []
    job_num = len(jobs)
    for _ in range(job_num):
        assigned_machine = random.randint(1, num_machines)
        schedule.append(assigned_machine)



def calculate_fitness():