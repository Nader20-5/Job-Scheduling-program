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

    belief_space = {
        'best_fitness_so_far': float('inf'),
        'best_schedule_so_far': []
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
