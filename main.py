from generater import Population, Melody, Params, mapNoteToValue, mapValueToNote
from export import melody_to_midi

def fitness_function_sample(melody) -> int:
    """
    计算旋律的适应度值的示例函数。
    这里简单地计算旋律中非休止符音符的数量作为适应度值。
    """
    fitness = sum(1 for note in melody.notes if note != mapNoteToValue['O'])
    return fitness

def main():
    # 设置遗传算法参数
    generations = 50
    initial_size = 20
    threshold = 200
    params = Params(
        population_size=50,
        crossover_rate=0.7,
        mutation_rate=0.1,
        transpose_rate=0.1,
        inversion_rate=0.1,
        retrograde_rate=0.1,
    )

    # 初始化种群
    population = Population(size=initial_size, threshold=threshold)
    population.initialize(fitness_function_sample)

    # 进化过程
    generation = 0
    while generation < generations:
        print(f"Generation {generation}:")

        # 进化到下一代
        population.evolve(fitness_function_sample, params)
        if population.check_termination():
            print("Threshold reached, stopping evolution.")
            break
        generation += 1
    
    # 输出最终结果
    print("Final Generation:")
    population_best = population.find_best_individual()
    if population_best:
        print(f" Best Individual Fitness = {population_best.fitness}")
        print(f" Notes: {[mapValueToNote[note] for note in population_best.notes]}")
        # 导出为MIDI文件
        melody_to_midi(population_best.notes)


if __name__ == "__main__":
    main()