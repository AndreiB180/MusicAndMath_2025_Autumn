import random
from typing import List, Tuple
# 每个Note代表一个8分音符，延长符号'-'表示前一个音符延长8分音符的时值
mapNoteToValue = {
    'O' : 0, # 休止符
    'F3': 1,
    '#F3': 2,
    'G3': 3,
    '#G3': 4,
    'A3': 5,
    '#A3': 6,
    'B3': 7,
    'C4': 8,
    '#C4': 9,
    'D4': 10,
    '#D4': 11,
    'E4': 12,
    'F4': 13,
    '#F4': 14,
    'G4': 15,
    '#G4': 16,
    'A4': 17,
    '#A4': 18,
    'B4': 19,
    'C5': 20,
    '#C5': 21,
    'D5': 22,
    '#D5': 23,
    'E5': 24,
    'F5': 25,
    '#F5': 26,
    'G5': 27,
    '-' : 28 # 延长符号
}

mapValueToNote = {v: k for k, v in mapNoteToValue.items()}


class Params:
    """
    遗传算法的参数类，包含各种操作的概率和种群大小等参数。
    """
    def __init__(self, population_size=100, crossover_rate=0.7, mutation_rate=0.1,
                 transpose_rate=0.1, inversion_rate=0.1, retrograde_rate=0.1):
        self.population_size = population_size  # 种群大小
        self.crossover_rate = crossover_rate  # 交叉概率
        self.mutation_rate = mutation_rate  # 变异概率
        self.transpose_rate = transpose_rate  # 移调概率
        self.inversion_rate = inversion_rate  # 倒影概率
        self.retrograde_rate = retrograde_rate  # 逆行概率

class Melody:
    """
    遗传算法中的个体类，表示一个旋律。
    长度为4/4拍的四小节，共32个8分音符。
    """
    def __init__(self, notes: List[int] = []):
        self.notes = notes  # 存储旋律的音符列表
        self.fitness = 0  # 适应度值，表示旋律的质量
    def calculate_fitness(self, fitness_function):
        """
        计算旋律的适应度值。
        """
        self.fitness = fitness_function(self)

class Population:
    """
    遗传算法中的种群类，包含多个旋律个体。
    """
    def __init__(self, size : int, threshold : int):
        self.individuals = []  # 初始化种群，包含指定数量的旋律个体
        self.size = size  # 种群初始大小
        self.generation = 0  # 当前代数
        self.threshold = threshold  # 适应度阈值

    def initialize(self, fitness_function):
        """
        初始化种群，随机生成旋律个体。
        """
        import random
        for _ in range(self.size):
            melody = Melody()
            melody.notes = [random.choice(list(mapNoteToValue.values())) for _ in range(32)]
            self.individuals.append(melody)
        for individual in self.individuals:
            individual.fitness = fitness_function(individual)

    def crossover(self, parent1: Melody, parent2: Melody) -> Tuple[Melody, Melody]:
        """
        交叉操作，生成新的旋律个体。
        """
        crossover_point1 = random.randint(1, 31)
        crossover_point2 = random.randint(1, 31)
        if crossover_point1 > crossover_point2:
            crossover_point1, crossover_point2 = crossover_point2, crossover_point1
        child_1 = Melody()
        child_2 = Melody()
        child_1.notes = (parent1.notes[:crossover_point1] + \
                       parent2.notes[crossover_point1:crossover_point2] + \
                       parent1.notes[crossover_point2:])
        child_2.notes = (parent2.notes[:crossover_point1] + \
                       parent1.notes[crossover_point1:crossover_point2] + \
                          parent2.notes[crossover_point2:])
        return (child_1, child_2)
    
    def mutate(self, individual: Melody) -> Melody:
        """
        变异操作，随机改变旋律个体的音符。
        """
        mutate_point = random.randint(0, 31)
        individual.notes[mutate_point] = random.choice(list(mapNoteToValue.values()))
        return individual
    
    def transpose(self, individual: Melody) -> Melody:
        """
        移调操作，整体提升或降低旋律个体的音高。
        """
        transpose_interval = random.choice([-2, -1, 1, 2])  # 随机选择移调间隔
        for i in range(len(individual.notes)):
            if individual.notes[i] != mapNoteToValue['O'] and individual.notes[i] != mapNoteToValue['-']:
                new_value = individual.notes[i] + transpose_interval
                if 1 <= new_value <= 27:  # 确保音符在有效范围内
                    individual.notes[i] = new_value
                # 若超出范围则轮转
                elif new_value < 1:
                    individual.notes[i] = 27 - (1 - new_value)
                elif new_value > 27:
                    individual.notes[i] = 1 + (new_value - 27)
        return individual

    def inversion(self, individual: Melody) -> Melody:
        """
        倒影操作，以中间音高为轴，将旋律个体的音符进行倒影变换。
        """
        mid_value = (1 + 27) // 2  # 中间音高值
        for i in range(len(individual.notes)):
            if individual.notes[i] != mapNoteToValue['O'] and individual.notes[i] != mapNoteToValue['-']:
                individual.notes[i] = 2 * mid_value - individual.notes[i] 
        return individual
    
    def retrograde(self, individual: Melody) -> Melody:
        """
        逆行操作，反转旋律个体的音符顺序。
        """
        individual.notes = individual.notes[::-1]
        return individual
    
    def select_parents(self) -> Tuple[Melody | None, Melody | None]:
        """
        轮盘赌算法选择两个亲代个体。
        """
        total_fitness = sum(individual.fitness for individual in self.individuals)
        pick1 = random.uniform(0, total_fitness)
        pick2 = random.uniform(0, total_fitness)
        parent1 = None
        parent2 = None
        current = 0
        for individual in self.individuals:
            current += individual.fitness
            if parent1 is None and current >= pick1:
                parent1 = individual
            if parent2 is None and current >= pick2:
                parent2 = individual
            if parent1 is not None and parent2 is not None:
                break

        return (parent1, parent2)

    def evolve(self, fitness_function, params : Params):
        """
        进化到下一代，一共要产生params.population_size个新个体。
        """
        new_generation = []
        while len(new_generation) < params.population_size:
            parent1, parent2 = self.select_parents()
            if parent1 is None or parent2 is None:
                break
            # 交叉操作
            if random.random() < params.crossover_rate:
                child1, child2 = self.crossover(parent1, parent2)
            else:
                child1 = Melody(notes=parent1.notes.copy())
                child2 = Melody(notes=parent2.notes.copy())
            # 变异操作
            if random.random() < params.mutation_rate:
                child1 = self.mutate(child1)
            if random.random() < params.mutation_rate:
                child2 = self.mutate(child2)
            # 移调操作
            if random.random() < params.transpose_rate:
                child1 = self.transpose(child1)
            if random.random() < params.transpose_rate:
                child2 = self.transpose(child2)
            # 倒影操作
            if random.random() < params.inversion_rate:
                child1 = self.inversion(child1)
            if random.random() < params.inversion_rate:
                child2 = self.inversion(child2)
            # 逆行操作
            if random.random() < params.retrograde_rate:
                child1 = self.retrograde(child1)
            if random.random() < params.retrograde_rate:
                child2 = self.retrograde(child2)
            # 计算新个体的适应度值
            child1.calculate_fitness(fitness_function)
            child2.calculate_fitness(fitness_function)
            if child1.fitness >= child2.fitness:
                new_generation.append(child1)
            else:
                new_generation.append(child2)
        self.individuals += new_generation
        self.generation += 1
    
    def check_termination(self) -> bool:
        """
        检查是否达到终止条件。
        这里的终止条件是种群中是否存在适应度值超过阈值的个体。
        """
        for individual in self.individuals:
            if individual.fitness >= self.threshold:
                return True
        return False
    
    def find_best_individual(self) -> Melody | None:
        """
        找到种群中适应度值最高的个体。
        """
        if not self.individuals:
            return None
        best_individual = max(self.individuals, key=lambda ind: ind.fitness)
        return best_individual
