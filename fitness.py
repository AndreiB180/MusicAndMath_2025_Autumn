import math
from generater import Melody, mapNoteToValue, mapValueToNote


# 1. 基于乐理规则的适应度函数 (Rule-based)
def fitness_music_theory(melody: Melody) -> int:
    score = 0
    notes = melody.notes
    
    # --- 预处理：提取真实音符（去除休止符和延音符） ---
    real_notes = [n for n in notes if 1 <= n <= 27]
    if not real_notes:
        return 0

    # --- 规则 A: 调性 (Tonality) - C 大调 ---
    # C Major: C, D, E, F, G, A, B
    # 对应 mapNoteToValue 中的值 (排除升号 #)
    # F3=1, G3=3, A3=5, B3=7, C4=8, D4=10, E4=12, F4=13, ...
    c_major_values = {1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19, 20, 22, 24, 25, 27}
    
    in_key_count = sum(1 for n in real_notes if n in c_major_values)
    # 奖励在调内的音符，比例越高分越高
    score += (in_key_count / len(real_notes)) * 100

    # --- 规则 B: 音程 (Intervals) ---
    # 音乐通常以级进（小跳）为主，偶尔大跳
    smooth_intervals = 0
    huge_jumps = 0
    for i in range(len(real_notes) - 1):
        diff = abs(real_notes[i] - real_notes[i+1])
        if diff <= 4: # 大三度以内 (4个半音)
            smooth_intervals += 1
        elif diff > 12: # 八度以上的大跳
            huge_jumps += 1
    
    score += smooth_intervals * 2
    score -= huge_jumps * 5  # 惩罚过大的跳跃

    # --- 规则 C: 终止式 (Cadence) ---
    # 最后一个音符最好结束在主音 C (C4=8, C5=20) 或属音 G (G3=3, G4=15)
    last_note = real_notes[-1]
    if last_note in [8, 20]: # C
        score += 50
    elif last_note in [3, 15, 27]: # G
        score += 20
    
    # --- 规则 D: 节奏稳定性 ---
    # 避免过多的连续休止符
    rest_count = notes.count(mapNoteToValue['O'])
    if rest_count > 16: # 超过一半是休止符
        score -= 20

    return max(0, int(score))

# 2. 基于统计结果的适应度函数 (Statistical)
def fitness_statistical(melody: Melody) -> int:
    """
    尝试让旋律的音高变化符合正态分布，或者音程跳跃符合 1/f 规律。
    这里演示一个简单的：期望音高主要集中在中央 C (C4=8) 到 C5 (20) 之间。
    """
    real_notes = [n for n in melody.notes if 1 <= n <= 27]
    if not real_notes: return 0
    
    score = 100
    
    # 计算平均音高
    avg_pitch = sum(real_notes) / len(real_notes)
    # 理想平均音高在 14 左右 (F4附近)
    dist_from_center = abs(avg_pitch - 14)
    score -= dist_from_center * 5
    
    # 期望音域不要太窄也不要太宽 (标准差)
    # ... (略)
    
    return max(0, int(score))

# 3. 机器学习/马尔可夫链 (Simple ML)
def fitness_ml_markov(melody: Melody) -> int:
    real_notes = [n for n in melody.notes if 1 <= n <= 27]
    if len(real_notes) < 2: return 0
    
    log_likelihood = 0
    count = 0
    for i in range(len(real_notes) - 1):
        curr = real_notes[i]
        next_n = real_notes[i+1]
        diff = abs(next_n - curr)
        
        # 模拟概率：
        if diff == 0: prob = 0.1   # 同音重复
        elif diff <= 2: prob = 0.6 # 级进 (半音/全音)
        elif diff <= 4: prob = 0.2 # 小跳
        elif diff <= 7: prob = 0.05 # 五度以内
        else: prob = 0.01          # 大跳
        
        log_likelihood += math.log(prob)
        count += 1
    
    if count == 0: return 0

    # 修正：使用平均对数似然度，并映射到正分区间
    # log(0.01) ≈ -4.6 (最低分情况)
    # log(0.6) ≈ -0.5 (最高分情况)
    # 平均值 avg_log_prob 范围大约在 -4.6 到 -0.5 之间
    
    avg_log_prob = log_likelihood / count
    
    # 线性映射到 0-100 分
    # 假设 -5 分对应 0 分，0 分对应 100 分
    score = (avg_log_prob + 5) * 20
    
    return max(0, int(score))


# 4. 人机交互 (Interactive)

def fitness_interactive(melody: Melody) -> int:
    # 警告：这需要用户对每一个个体打分，种群大时不可用！
    print(f"Notes: {[mapValueToNote[n] for n in melody.notes]}")
    try:
        s = input("请输入评分 (0-10): ")
        return int(s) * 10
    except:
        return 0
