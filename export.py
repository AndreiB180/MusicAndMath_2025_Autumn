# 将音乐串转为可播放的MIDI文件
from typing import List
from midiutil import MIDIFile
import os

# -------------------------- 核心映射配置 --------------------------
# 数字 → (音名, MIDI音高) 映射（严格对应需求）
NUMBER_TO_NOTE = {
    0: ('O', None),    # 休止符（MIDI音高为None）
    1: ('F3', 53),     # F3 对应 MIDI 53
    2: ('#F3', 54),    # #F3 对应 MIDI 54
    3: ('G3', 55),     # G3 对应 MIDI 55
    4: ('#G3', 56),    # #G3 对应 MIDI 56
    5: ('A3', 57),     # A3 对应 MIDI 57
    6: ('#A3', 58),    # #A3 对应 MIDI 58
    7: ('B3', 59),     # B3 对应 MIDI 59
    8: ('C4', 60),     # C4 对应 MIDI 60（中央C）
    9: ('#C4', 61),    # #C4 对应 MIDI 61
    10: ('D4', 62),    # D4 对应 MIDI 62
    11: ('#D4', 63),   # #D4 对应 MIDI 63
    12: ('E4', 64),    # E4 对应 MIDI 64
    13: ('F4', 65),    # F4 对应 MIDI 65
    14: ('#F4', 66),   # #F4 对应 MIDI 66
    15: ('G4', 67),    # G4 对应 MIDI 67
    16: ('#G4', 68),   # #G4 对应 MIDI 68
    17: ('A4', 69),    # A4 对应 MIDI 69（标准音）
    18: ('#A4', 70),   # #A4 对应 MIDI 70
    19: ('B4', 71),    # B4 对应 MIDI 71
    20: ('C5', 72),    # C5 对应 MIDI 72
    21: ('#C5', 73),   # #C5 对应 MIDI 73
    22: ('D5', 74),    # D5 对应 MIDI 74
    23: ('#D5', 75),   # #D5 对应 MIDI 75
    24: ('E5', 76),    # E5 对应 MIDI 76
    25: ('F5', 77),    # F5 对应 MIDI 77
    26: ('#F5', 78),   # #F5 对应 MIDI 78
    27: ('G5', 79),    # G5 对应 MIDI 79
    28: ('-', None)    # 延长符（无独立音高，依赖前一音符）
}

# 基础时值配置（4/4拍，八分音符为基础单位）
BASE_DURATION = 0.5  # 八分音符 = 0.5 拍
VOLUME = 100         # 音量（0-127）
TEMPO = 120          # 速度（BPM）
CHANNEL = 0          # MIDI通道（默认0）
PROGRAM = 41         # 乐器音色（41=小提琴，可修改：1=钢琴，25=吉他等）

# -------------------------- 核心转换函数 --------------------------
def melody_to_midi(melody_numbers: list, output_file: str = "melody.mid"):
    """
    将数字旋律序列转换为MIDI文件
    :param melody_numbers: 数字编码的旋律列表（如 [8, 10, 12, 13, 0, 28, ...]）
    :param output_file: 输出MIDI文件名
    """
    # 初始化MIDI文件（1轨，单通道）
    output_file = os.path.join(os.getcwd(), "output", output_file)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    midi = MIDIFile(1, adjust_origin=True)
    midi.addTempo(track=0, time=0, tempo=TEMPO)
    midi.addProgramChange(tracknum=0, channel=CHANNEL, time=0, program=PROGRAM)

    current_time = 0.0  # 当前播放时间（单位：拍）
    prev_note = None    # 记录前一个有效音符（用于处理延长符）
    prev_duration = 0.0 # 记录前一个音符的累计时值

    for idx, num in enumerate(melody_numbers):
        # 校验数字合法性
        if num not in NUMBER_TO_NOTE:
            raise ValueError(f"无效数字编码：{num}（仅支持0-28）")
        
        note_name, midi_pitch = NUMBER_TO_NOTE[num]

        # 情况1：延长符 '-'（数字28）
        if num == 28:
            if prev_note is None:
                # 延长符不能位于序列开头，跳过或报错
                print(f"警告：序列第{idx+1}位为延长符，无前置音符，已跳过")
                continue
            # 延长符：追加一个基础时值（八分音符）
            prev_duration += BASE_DURATION
            # 不立即添加音符，等待后续非延长符时统一写入
            continue

        # 情况2：非延长符（普通音符/休止符）
        if prev_note is not None:
            # 先写入前一个音符（含累计延长时值）
            prev_note_pitch, prev_note_is_rest = prev_note
            if not prev_note_is_rest:
                # 前一个是普通音符：添加音符
                midi.addNote(
                    track=0,
                    channel=CHANNEL,
                    pitch=prev_note_pitch,
                    time=current_time,
                    duration=prev_duration,
                    volume=VOLUME
                )
            # 更新当前时间（移动到前一个音符结束位置）
            # 对于休止符，只需要推进时间，不添加音符
            current_time += prev_duration

        # 更新当前音符状态
        if num == 0:
            # 休止符：标记为休止，时值初始化为基础时值
            prev_note = (None, True)
            prev_duration = BASE_DURATION
        else:
            # 普通音符：记录MIDI音高，时值初始化为基础时值
            prev_note = (midi_pitch, False)
            prev_duration = BASE_DURATION

    # 处理序列末尾的最后一个音符（含延长符）
    if prev_note is not None:
        prev_note_pitch, prev_note_is_rest = prev_note
        if not prev_note_is_rest:
            midi.addNote(
                track=0,
                channel=CHANNEL,
                pitch=prev_note_pitch,
                time=current_time,
                duration=prev_duration,
                volume=VOLUME
            )
    with open(output_file, "wb") as f:
        midi.writeFile(f)
    print(f"MIDI文件已保存至：{output_file}")

# -------------------------- 测试用例 --------------------------
if __name__ == "__main__":
    # 测试旋律：C4 → D4 → E4（延长1拍）→ 休止符 → G4 → A4（延长2拍）→ B4
    test_melody = [8, 10, 12, 28, 0, 15, 17, 28, 28, 19]
    print(f"测试旋律（数字编码）：{test_melody}")
    print(f"对应音符：{[NUMBER_TO_NOTE[num][0] for num in test_melody]}")
    
    # 转换为MIDI
    melody_to_midi(test_melody, output_file="test_melody.mid")
