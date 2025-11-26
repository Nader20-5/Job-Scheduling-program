import schedule
import copy
import operators

FINAL_POPULATION = 50
FINAL_GENERATIONS = 100


def update_belief_space(belief_space, population, fitness_scores):
    
    current_best_fitness = min(fitness_scores)
    
    if current_best_fitness < belief_space['best_fitness_so_far']:
        
        belief_space['best_fitness_so_far'] = current_best_fitness
        best_index = fitness_scores.index(current_best_fitness)
        belief_space['best_schedule_so_far'] = copy.deepcopy(population[best_index])


def solve_with_ca(jobs_input, num_machines):
    
    job_durations = []
    for job_id, operations in enumerate(jobs_input):
        total_time = sum(op[1] for op in operations) # Sum durations of all ops
        job_durations.append( (job_id, total_time) )
    
    # Sort by duration (highest first)
    job_durations.sort(key=lambda x: x[1], reverse=True)
    
    # Let's say the top 20% of jobs are "Critical"
    num_critical = max(1, int(len(jobs_input) * 0.2)) 
    critical_jobs_list = [item[0] for item in job_durations[:num_critical]]

    belief_space = {
        'best_fitness_so_far': float('inf'),
        'best_schedule_so_far': [],
        'critical_jobs': critical_jobs_list
    }
    
    #making 50 random schedules[Gen 0]
    population = [schedule.create_random_schedule(jobs_input) for _ in range(FINAL_POPULATION)] 

    #getting fitness score for each schedule
    fitness_scores = [schedule.calculate_fitness(s , jobs_input , num_machines) for s in population] 

    for gen in range(FINAL_GENERATIONS):

        update_belief_space(belief_space, population, fitness_scores)
        new_population = []

        #making new Generation
        for _ in range(FINAL_POPULATION):

            #select 2 parents make a crossover and small mutation and put it in new population
            parent1 = operators.selection(population, fitness_scores)
            parent2 = operators.selection(population, fitness_scores)
            child = operators.crossover(parent1, parent2)
            child = operators.mutation(child, belief_space , mutation_rate=0.1)

            new_population.append(child)

        population = new_population
        fitness_scores = [schedule.calculate_fitness(s, jobs_input, num_machines) for s in population]

    return belief_space['best_schedule_so_far'], belief_space['best_fitness_so_far']
