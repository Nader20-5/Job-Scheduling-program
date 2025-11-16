import schedule
import copy

FINAL_POPULATION = 50
FINAL_GENERATIONS = 100

def solve_with_ca(jobs, machines):
    
    #making 50 random schedules
    population = [schedule.create_random_schedule(jobs , machines) for _ in range(FINAL_POPULATION)] 

    #getting fitness score for each schedule
    fitness_score = [schedule.calculate_fitness(s , jobs , machines) for s in population] 