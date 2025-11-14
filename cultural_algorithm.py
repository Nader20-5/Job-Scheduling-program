import schedule

FINAL_POPULATION = 50
FINAL_GENERATIONS = 100

def solve_with_ca(jobs, machines):
    population = [schedule.create_random_schedule(jobs , machines) for _ in range(FINAL_POPULATION)]
    fitness = [schedule.calculate_fitness(s , jobs , machines) for s in population]