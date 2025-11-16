"""import random
import copy
    
def selection(self, fitnesses):
    selected_parents = []
    for _ in range(self.pop_size):
        # select a random solution
        idx1 = random.randint(0, len(self.population) - 1)
        idx2 = random.randint(0, len(self.population) - 1)
            
        # select the best 
        if fitnesses[idx1] > fitnesses[idx2]:
            winner = copy.deepcopy(self.population[idx1])
        else:
            winner = copy.deepcopy(self.population[idx2])
            
        selected_parents.append(winner)
        return selected_parents
    

def crossover(self, parent1, parent2):
        
    # cut mn makan random
    crossover_point = random.randint(1, self.num_jobs - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
        
    return child
    
    
def mutation(self, schedule, mutation_rate=0.1):
    
    mutated_schedule = copy.deepcopy(schedule)
        
    for i in range(len(mutated_schedule)):

        if random.random() < mutation_rate:
        
            mutation_type = random.choice(['resource', 'time', 'both'])
            if mutation_type == 'resource' or mutation_type == 'both':
                # changing resources
                mutated_schedule[i][0] = random.randint(1, self.num_resources)
                
            if mutation_type == 'time' or mutation_type == 'both':
                # change start time
                mutated_schedule[i][1] = random.randint(0, 50)
        
    return mutated_schedule
    
    
def influence_evolution(self, schedule, belief_space, mutation_rate=0.1, influence_strength=0.5):
       
    # copy 3ashan man3emelsh taghyir fe original
    influenced_schedule = copy.deepcopy(schedule)
        
    for job_id in range(len(influenced_schedule)):
            
        if random.random() < influence_strength:
                
            #(Normative Knowledge) 
            current_resource, current_time = influenced_schedule[job_id]
            resource_range = belief_space.normative[job_id]['resource_range']  # مثال: (1, 3)
            time_range = belief_space.normative[job_id]['time_range']          # مثال: (5, 20)
            best_resource = belief_space.normative[job_id]['best_resource']    # مثال: 2
            best_time = belief_space.normative[job_id]['best_time']            # مثال: 12
           
     #resources 3dt el range?
        if current_resource < resource_range[0] or current_resource > resource_range[1]:
            #han3ml check lw el resources wehsha 3ashan neshoof el best
                if best_resource:
                    influenced_schedule[job_id][0] = best_resource
                else:
                    influenced_schedule[job_id][0] = random.randint(
                        resource_range[0], 
                        resource_range[1]
                    )
                
                if current_time < time_range[0] or current_time > time_range[1]:
                  
                    if best_time:
                        influenced_schedule[job_id][1] = best_time
                    else:
                        influenced_schedule[job_id][1] = random.randint(
                            int(time_range[0]), 
                            int(time_range[1])
                        )
                
                # (Domain Knowledge) 
                # critical ya3ni fe many jobs depend on it
                if job_id in belief_space.domain_knowledge['critical_jobs']:
                    
                # critical jobs != bottleneck resource  ya3ni msh betrooh lel  resource el zahma                   
                    bottlenecks = belief_space.domain_knowledge['bottleneck_resources']
                    
                    if influenced_schedule[job_id][0] in bottlenecks:
                        available = [r for r in range(1, self.num_resources + 1) 
                                   if r not in bottlenecks]
                        
                    if available:
                        influenced_schedule[job_id][0] = random.choice(available)
                #(Situational Knowledge) 
                
                if belief_space.best_solution and random.random() < 0.3:
                   influenced_schedule[job_id] = copy.deepcopy(
                        belief_space.best_solution[job_id]
                    )
    
    return influenced_schedule
    """

from collections import Counter
import random
import copy

def selection(population, fitness_scores):

    idx1 = random.randint(0, len(population) - 1)
    idx2 = random.randint(0, len(population) - 1)
    
    if fitness_scores[idx1] < fitness_scores[idx2]:
        return population[idx1]
    else:
        return population[idx2]


def crossover(parent1_chromosome, parent2_chromosome):
    
    p1 = copy.deepcopy(parent1_chromosome)
    p2 = copy.deepcopy(parent2_chromosome)
    size = len(p1)

    #Pick two random cut-off points
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size

    # 3.Copy the "chunk" from parent 1 directly to the child
    chunk = p1[start:end]
    child[start:end] = chunk
    
    # 4. Count the items in the chunk
    chunk_item_counts = Counter(chunk)
    
    # 5. Get the list of items to add from Parent 2
    p2_items_to_add = []

    for item in p2:

        # Check if this item is "available" in the chunk
        if item in chunk_item_counts and chunk_item_counts[item] > 0:
            chunk_item_counts[item] -= 1

        else:
            p2_items_to_add.append(item)

    # 6. Fill in the 'None' gaps in the child, using the items from parent 2
    child_pointer = 0
    p2_pointer = 0
    
    while p2_pointer < len(p2_items_to_add):

        if child_pointer == start:
            # We've reached the middle chunk, jump to the end
            child_pointer = end
        
        # If this slot is empty, fill it
        if child[child_pointer] is None:
            child[child_pointer] = p2_items_to_add[p2_pointer]
            p2_pointer += 1
            
        child_pointer += 1
        
    return child


def mutation(chromosome, belief_space, mutation_rate=0.1):
    
    new_chromosome = copy.deepcopy(chromosome)
    
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(new_chromosome)), 2)
        new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]

    return new_chromosome