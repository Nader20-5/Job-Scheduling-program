import random
import copy
from collections import Counter

def selection(population, fitness_scores):
    
    idx1 = random.randint(0, len(population) - 1)
    idx2 = random.randint(0, len(population) - 1)
    
    if fitness_scores[idx1] < fitness_scores[idx2]:
        # Return the chromosome (the list) of the winner
        return population[idx1]
    else:
        return population[idx2]


def crossover(parent1_chromosome, parent2_chromosome):
    
    p1 = copy.deepcopy(parent1_chromosome)
    p2 = copy.deepcopy(parent2_chromosome)
    size = len(p1)

    # 1. Pick two random cut-off points
    start, end = sorted(random.sample(range(size), 2))

    # 2. Create the child, starting as a list of 'None'
    child = [None] * size

    # 3. Copy the "chunk" from parent 1 directly to the child
    chunk = p1[start:end]
    child[start:end] = chunk
    
    # 4. Count the items in the chunk
    chunk_item_counts = Counter(chunk)
    
    # 5. Get the list of items to add from Parent 2
    p2_items_to_add = []
    for item in p2:
        if item in chunk_item_counts and chunk_item_counts[item] > 0:
            chunk_item_counts[item] -= 1
        else:
            p2_items_to_add.append(item)

    # 6. Fill in the 'None' gaps in the child, using the items from parent 2
    child_pointer = 0
    p2_pointer = 0
    
    while p2_pointer < len(p2_items_to_add):
        if child_pointer == start:
            child_pointer = end
        
        if child[child_pointer] is None:
            child[child_pointer] = p2_items_to_add[p2_pointer]
            p2_pointer += 1
            
        child_pointer += 1
        
    return child


def mutation(chromosome, belief_space, mutation_rate=0.1):
    
    new_chromosome = copy.deepcopy(chromosome)
    
    # --- 1. CULTURAL INFLUENCE (30% Chance) ---
    # This replaces your friend's 'influence_evolution' function.
    if random.random() < 0.3: 
        
        # A. SITUATIONAL KNOWLEDGE (Copying the Leader)
        # Logic: "If Job A is before Job B in the Best Schedule, I should do that too."
        best_ever = belief_space['best_schedule_so_far']
        
        if best_ever: # Only if we have a history
            # Pick two random spots in our child
            idx1, idx2 = sorted(random.sample(range(len(new_chromosome)), 2))
            job_a = new_chromosome[idx1]
            job_b = new_chromosome[idx2]
            
            # Check: Where are they in the Best Schedule?
            try:
                pos_a_in_best = best_ever.index(job_a)
                pos_b_in_best = best_ever.index(job_b)
                
                # If the Best Schedule has B before A...
                if pos_b_in_best < pos_a_in_best:
                    # ...but WE have A before B (since idx1 < idx2)...
                    # SWAP THEM to match the leader!
                    new_chromosome[idx1], new_chromosome[idx2] = job_b, job_a
                    return new_chromosome 
            except ValueError:
                pass 

        # B. DOMAIN KNOWLEDGE (Critical Jobs)
        # Logic: "Long/Critical jobs should be done FIRST."
        # (We assume even-numbered jobs are 'critical' for this example)
        idx = random.randint(1, len(new_chromosome) - 1)
        job_id = new_chromosome[idx]
        
        # Your friend's check: "if job_id in belief_space...critical_jobs"
        # For now, let's pretend Job 0 is always critical:
        is_critical = (job_id in belief_space.get('critical_jobs', [])) 
        
        if is_critical:
            # It's critical! Move it earlier in the priority list (swap left)
            # This translates "Don't put on busy machine" to "Schedule it earlier"
            new_chromosome[idx], new_chromosome[idx-1] = new_chromosome[idx-1], new_chromosome[idx]
            return new_chromosome


    # --- 2. STANDARD MUTATION (10% Chance) ---
    # If we didn't use culture, we check for a normal random mutation.
    elif random.random() < mutation_rate:
        if len(new_chromosome) >= 2:
            idx1, idx2 = random.sample(range(len(new_chromosome)), 2)
            # Simple random swap
            new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]

    # Ensure we ALWAYS return the chromosome, even if no mutation happened
    return new_chromosome