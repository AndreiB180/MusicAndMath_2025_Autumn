from generater import Population, Melody, Params, mapNoteToValue, mapValueToNote
from export import melody_to_midi
from fitness import fitness_music_theory, fitness_statistical, fitness_ml_markov, fitness_interactive
import random
import math

def main():
    params = Params(
        population_size=500,
        crossover_rate=0.6,
        mutation_rate=0.4,
        transpose_rate=0.1,
        inversion_rate=0.05,
        retrograde_rate=0.05
    )

    generations = 100
    initial_size = 100
    threshold = 1000

    # current_fitness_function = fitness_music_theory
    # current_fitness_function = fitness_statistical
    current_fitness_function = fitness_ml_markov
    # current_fitness_function = fitness_interactive

    print(f"Using Fitness Function: {current_fitness_function.__name__}")

    population = Population(size=initial_size, threshold=threshold)
    population.initialize(current_fitness_function)

    for generation in range(generations):
        best_ind = population.find_best_individual()
        avg_fitness = sum(ind.fitness for ind in population.individuals) / len(population.individuals)
        
        print(f"Generation {generation}: Best Fitness = {best_ind.fitness}, Avg Fitness = {avg_fitness:.2f}")

        population.evolve(current_fitness_function, params)
        
        if population.check_termination():
            print("Threshold reached, stopping evolution.")
            break
    
    print("\nFinal Generation:")
    population_best = population.find_best_individual()
    if population_best:
        print(f" Best Individual Fitness = {population_best.fitness}")
        print(f" Notes: {[mapValueToNote[note] for note in population_best.notes]}")
        
        output_filename = "output_melody.mid"
        try:
            melody_to_midi(population_best.notes, output_filename)
            print(f"Generated MIDI saved to {output_filename}")
        except TypeError:
             melody_to_midi(population_best.notes)
             print(f"Generated MIDI saved (default filename)")

if __name__ == "__main__":
    main()