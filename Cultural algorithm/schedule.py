import random

#Loops 3shan n create random chromosome[0 ,1 , 0 , 1]
def create_random_schedule(jobs_input):
    operation_list = []

    for job_id, job_operations in enumerate(jobs_input):
        operation_list.extend([job_id] * len(job_operations))

    random.shuffle(operation_list)
    return operation_list

#loops 3shan n calculate score to each schedule
def calculate_fitness(schedule , jobs_input , num_machines):

    machine_timers = [0] * num_machines
    job_timers = [0] * len(jobs_input)
    operation_counters = [0] * len(jobs_input)
    
    
    # Loop 3ala the chromosome
    for job_id in schedule:
        
        op_index = operation_counters[job_id]
        
        # Get the (machine, duration) tuple for that operation
        op = jobs_input[job_id][op_index]
        machine_id, duration = op
        
        #constraints(see machine's ready time(may be busy) , see jobs ready time(momken operation ablaha lesa mt3mltsh))
        machine_ready_time = machine_timers[machine_id]
        job_ready_time = job_timers[job_id]
        
        #benshoof eh el hykhls met2khr 3shan nebd2(el machine hatefda el awel wala el operation hatekhls el awel)
        start_time = max(machine_ready_time, job_ready_time)
        end_time = start_time + duration
        
        #update
        machine_timers[machine_id] = end_time
        job_timers[job_id] = end_time
        operation_counters[job_id] += 1
        
        
    makespan = max(machine_timers)
    return makespan
# [[(0,2),(1,4),(2,3),(3,1)],[(1,3),(0,2),(1,1),(3,3)],[(0,3),(2,2),(1,3),(0,1)]]