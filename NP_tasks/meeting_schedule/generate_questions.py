#!/usr/bin/env python3
"""
基于规则的会议安排问题（Meeting Scheduling Problem）造题脚本
目标：最大化总参会人数
"""

import json
import random
import argparse
from typing import Dict, List, Tuple

def save_json_compact(data, filename):
    """
    使用自定义的紧凑格式保存JSON文件。
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('{\n')
        f.write(f'  "big_small": "{data["big_small"]}",\n')
        f.write('  "questions": {\n')
        
        question_items = []
        
        # 自定义排序：easy -> medium -> hard
        def sort_key(q_key):
            if q_key.startswith('easy_'):
                return (0, int(q_key.replace('easy_question', '')))
            elif q_key.startswith('medium_'):
                return (1, int(q_key.replace('medium_question', '')))
            elif q_key.startswith('hard_'):
                return (2, int(q_key.replace('hard_question', '')))
            elif q_key.startswith('bench_'):
                return (3, int(q_key.replace('bench_question', '')))
            else:
                # 兼容其他格式
                return (4, int(q_key.replace('question', '')))
        
        sorted_q_keys = sorted(data["questions"].keys(), key=sort_key)
        
        for i, q_key in enumerate(sorted_q_keys):
            q_data = data["questions"][q_key]
            lines = [f'    "{q_key}": {{']
            
            # Format meetings
            meetings_str = ',\n'.join([f'      "{k}": {json.dumps(v)}' for k, v in q_data["meetings"].items()])
            lines.append(f'      "meetings": {{\n{meetings_str}\n      }},')

            # Format attendee_availability
            avail_str = ',\n'.join([f'      "{k}": {json.dumps(v)}' for k, v in q_data["attendee_availability"].items()])
            lines.append(f'      "attendee_availability": {{\n{avail_str}\n      }},')

            # Format rooms
            rooms_str = ',\n'.join([f'      "{k}": {v}' for k, v in q_data["rooms"].items()])
            lines.append(f'      "rooms": {{\n{rooms_str}\n      }}')

            lines.append('    }')
            question_item = '\n'.join(lines)
            if i < len(sorted_q_keys) - 1:
                question_item += ','
            question_items.append(question_item)
            
        f.write('\n'.join(question_items))
        f.write('\n  }\n}\n')


class MeetingScheduleGenerator:
    """会议安排问题生成器"""

    def __init__(self, params: Dict):
        self.p = params

    def _get_common_availability(self, attendees: List[int], availability: Dict, duration: int) -> List[Tuple[int, int]]:
        """计算一组参会者共同有空且足够长的时段"""
        if not attendees:
            return []
        
        # Start with the first attendee's availability
        common_slots = availability[str(attendees[0])]
        
        for i in range(1, len(attendees)):
            next_slots = availability[str(attendees[i])]
            new_common = []
            p1, p2 = 0, 0
            while p1 < len(common_slots) and p2 < len(next_slots):
                start1, end1 = common_slots[p1]
                start2, end2 = next_slots[p2]
                
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)
                
                if overlap_start < overlap_end:
                    new_common.append((overlap_start, overlap_end))
                
                if end1 < end2:
                    p1 += 1
                else:
                    p2 += 1
            common_slots = new_common
        
        # Filter for slots that are long enough for the meeting
        return [(s, e) for s, e in common_slots if e - s >= duration]

    def _find_a_greedy_solution(self, problem: Dict) -> List[Tuple[int, int, int]]:
        """使用贪心算法找到一个有效的（不一定最优的）会议安排"""
        meetings = problem["meetings"]
        availability = problem["attendee_availability"]
        rooms = problem["rooms"]
        
        scheduled_meetings = []
        room_schedules = {str(r_id): [] for r_id in rooms}
        attendee_schedules = {str(a_id): [] for a_id in availability}
        
        # 尝试安排每一个会议
        for m_id_str, m_info in meetings.items():
            m_id = int(m_id_str)
            attendees = m_info["attendees"]
            duration = m_info["duration"]
            
            # 找到合适的房间
            suitable_rooms = [r_id for r_id, cap in rooms.items() if cap >= len(attendees)]
            if not suitable_rooms:
                continue

            # 找到所有参会者都有空的时间
            common_slots = self._get_common_availability(attendees, availability, duration)
            if not common_slots:
                continue

            # 尝试在每个可用房间和可用时间段中找到一个位置
            best_slot_found = None
            for r_id_str in suitable_rooms:
                r_id = int(r_id_str)
                for start_slot, end_slot in common_slots:
                    current_time = start_slot
                    while current_time + duration <= end_slot:
                        # 检查房间冲突
                        room_conflict = any(s < current_time + duration and e > current_time for s, e in room_schedules[r_id_str])
                        
                        # 检查参会者冲突
                        attendee_conflict = False
                        if not room_conflict:
                            for att_id in attendees:
                                if any(s < current_time + duration and e > current_time for s, e in attendee_schedules[str(att_id)]):
                                    attendee_conflict = True
                                    break
                        
                        if not room_conflict and not attendee_conflict:
                            best_slot_found = (m_id, r_id, current_time)
                            break
                        current_time += 30 # 尝试下一个30分钟的槽
                    if best_slot_found:
                        break
                if best_slot_found:
                    break
            
            if best_slot_found:
                _, r_id, start = best_slot_found
                scheduled_meetings.append(best_slot_found)
                end = start + duration
                room_schedules[str(r_id)].append((start, end))
                for att_id in attendees:
                    attendee_schedules[str(att_id)].append((start, end))

        return sorted(scheduled_meetings, key=lambda x: x[2])

    def generate_single_question(self) -> Tuple[Dict, List[Tuple[int, int, int]]]:
        """生成单个MSP问题，并确保它有解"""
        num_meetings = random.randint(*self.p["num_meetings"])
        num_attendees = random.randint(*self.p["num_attendees"])
        num_rooms = random.randint(*self.p["num_rooms"])

        # 生成会议
        meetings = {str(i): {
            "attendees": sorted(random.sample(range(num_attendees), k=random.randint(2, self.p["max_attendees_per_meeting"]))),
            "duration": random.choice(self.p["durations"])
        } for i in range(num_meetings)}

        # 生成参会者可用时间
        availability = {}
        for i in range(num_attendees):
            if random.random() > self.p["fragmented_availability_chance"]:
                start = random.randint(self.p["time_window"][0], self.p["time_window"][0] + 120)
                end = random.randint(self.p["time_window"][1] - 120, self.p["time_window"][1])
                availability[str(i)] = [(start, end)]
            else: # 模拟午休
                avail1 = (self.p["time_window"][0], self.p["lunch_time"][0])
                avail2 = (self.p["lunch_time"][1], self.p["time_window"][1])
                availability[str(i)] = [avail1, avail2]

        # 生成房间
        rooms = {str(i): random.randint(*self.p["capacity_range"]) for i in range(num_rooms)}
        
        problem = {"meetings": meetings, "attendee_availability": availability, "rooms": rooms}
        
        # 保证有解
        solution = self._find_a_greedy_solution(problem)
        
        return problem, solution

    def get_difficulty_params(self, difficulty: str) -> Dict:
        """获取指定难度的参数"""
        base_params = {
            "time_window": (540, 1020), # 9:00 - 17:00
            "lunch_time": (720, 780), # 12:00 - 13:00
            "durations": [30, 60, 90],
            "capacity_range": (3, 10),
        }
        if difficulty == "easy":
            return {**base_params, "num_meetings": (4, 5), "num_attendees": (3, 5), "num_rooms": (3, 4),
                    "max_attendees_per_meeting": 3, "fragmented_availability_chance": 1}  
        elif difficulty == "medium":
            return {**base_params, "num_meetings": (5, 6), "num_attendees": (4, 6), "num_rooms": (4, 5),
                    "max_attendees_per_meeting": 4, "fragmented_availability_chance": 1}
        elif difficulty == "hard":
            return {**base_params, "num_meetings": (6, 7), "num_attendees": (5, 7), "num_rooms": (5, 6),
                    "max_attendees_per_meeting": 4, "fragmented_availability_chance": 1}
        elif difficulty == "bench":
            return {**base_params, "num_meetings": (8, 10), "num_attendees": (7, 9), "num_rooms": (6, 7),
                    "max_attendees_per_meeting": 5, "fragmented_availability_chance": 1}
        else:
            raise ValueError(f"未知难度: {difficulty}")

    def generate_questions_by_difficulty(self, num_questions: int, difficulty: str, prefix: str = "") -> Tuple[Dict, Dict]:
        """生成指定数量和难度的问题集"""
        self.p = self.get_difficulty_params(difficulty)
            
        questions, answers = {}, {}
        for i in range(1, num_questions + 1):
            # print(f"生成第 {i}/{num_questions} 题 (难度: {difficulty})...")
            problem, answer = self.generate_single_question()
            question_key = f"{prefix}question{i}" if prefix else f"question{i}"
            questions[question_key] = problem
            answers[question_key] = answer
            
        return questions, answers

    def generate_mixed_questions(self, easy_num: int, medium_num: int, hard_num: int, bench_num: int = 0) -> Dict:
        """生成混合难度的问题集，顺序为easy->medium->hard->bench"""
        all_questions, all_answers = {}, {}
        total_meetings = 0
        total_questions = 0
        
        # 生成easy题目
        if easy_num > 0:
            print(f"\n=== 生成 {easy_num} 道简单题目 ===")
            easy_q, easy_a = self.generate_questions_by_difficulty(easy_num, "easy", "easy_")
            # 按顺序添加easy题目
            for i in range(1, easy_num + 1):
                key = f"easy_question{i}"
                all_questions[key] = easy_q[key]
                all_answers[key] = easy_a[key]
            total_meetings += sum(len(q["meetings"]) for q in easy_q.values())
            total_questions += easy_num
        
        # 生成medium题目
        if medium_num > 0:
            print(f"\n=== 生成 {medium_num} 道中等题目 ===")
            medium_q, medium_a = self.generate_questions_by_difficulty(medium_num, "medium", "medium_")
            # 按顺序添加medium题目
            for i in range(1, medium_num + 1):
                key = f"medium_question{i}"
                all_questions[key] = medium_q[key]
                all_answers[key] = medium_a[key]
            total_meetings += sum(len(q["meetings"]) for q in medium_q.values())
            total_questions += medium_num
        
        # 生成hard题目
        if hard_num > 0:
            print(f"\n=== 生成 {hard_num} 道困难题目 ===")
            hard_q, hard_a = self.generate_questions_by_difficulty(hard_num, "hard", "hard_")
            # 按顺序添加hard题目
            for i in range(1, hard_num + 1):
                key = f"hard_question{i}"
                all_questions[key] = hard_q[key]
                all_answers[key] = hard_a[key]
            total_meetings += sum(len(q["meetings"]) for q in hard_q.values())
            total_questions += hard_num
            
        # 生成bench题目
        if bench_num > 0:
            print(f"\n=== 生成 {bench_num} 道基准题目 ===")
            bench_q, bench_a = self.generate_questions_by_difficulty(bench_num, "bench", "bench_")
            # 按顺序添加bench题目
            for i in range(1, bench_num + 1):
                key = f"bench_question{i}"
                all_questions[key] = bench_q[key]
                all_answers[key] = bench_a[key]
            total_meetings += sum(len(q["meetings"]) for q in bench_q.values())
            total_questions += bench_num
            
        avg_meetings = total_meetings / total_questions if total_questions > 0 else 0
        big_small = "big"
        
        return {
            "big_small": big_small, 
            "questions": all_questions, 
            "answers": all_answers,
            "metadata": {
                "easy_count": easy_num,
                "medium_count": medium_num, 
                "hard_count": hard_num,
                "bench_count": bench_num,
                "total_questions": total_questions,
                "avg_meetings": avg_meetings
            }
        }

def main():
    parser = argparse.ArgumentParser(description='生成会议安排问题数据集')
    parser.add_argument('--easy', type=int, default=0, help='生成简单题目数量')
    parser.add_argument('--medium', type=int, default=0, help='生成中等题目数量')
    parser.add_argument('--hard', type=int, default=0, help='生成困难题目数量')
    parser.add_argument('--bench', type=int, default=0, help='生成基准题目数量')
    parser.add_argument('--output', type=str, default='generated_meeting_schedule_questions.json', help='输出文件名')
    parser.add_argument('--separate', action='store_true', help='是否为每种难度生成单独的文件')
    args = parser.parse_args()

    # 检查参数
    if args.easy + args.medium + args.hard + args.bench == 0:
        print("错误: 至少需要指定一种难度的题目数量 > 0")
        print("例如: python generate_questions.py --easy 5 --medium 3 --hard 2 --bench 1")
        return

    generator = MeetingScheduleGenerator({})
    
    if args.separate:
        # 为每种难度生成单独文件
        if args.easy > 0:
            print(f"\n=== 生成 {args.easy} 道简单题目到单独文件 ===")
            easy_data = generator.generate_mixed_questions(args.easy, 0, 0, 0)
            easy_output = args.output.replace('.json', '_easy.json')
            output_data = {"big_small": easy_data["big_small"], "questions": easy_data["questions"]}
            save_json_compact(output_data, easy_output)
            print(f"简单题目文件: {easy_output}")
            
        if args.medium > 0:
            print(f"\n=== 生成 {args.medium} 道中等题目到单独文件 ===")
            medium_data = generator.generate_mixed_questions(0, args.medium, 0, 0)
            medium_output = args.output.replace('.json', '_medium.json')
            output_data = {"big_small": medium_data["big_small"], "questions": medium_data["questions"]}
            save_json_compact(output_data, medium_output)
            print(f"中等题目文件: {medium_output}")
            
        if args.hard > 0:
            print(f"\n=== 生成 {args.hard} 道困难题目到单独文件 ===")
            hard_data = generator.generate_mixed_questions(0, 0, args.hard, 0)
            hard_output = args.output.replace('.json', '_hard.json')
            output_data = {"big_small": hard_data["big_small"], "questions": hard_data["questions"]}
            save_json_compact(output_data, hard_output)
            print(f"困难题目文件: {hard_output}")
            
        if args.bench > 0:
            print(f"\n=== 生成 {args.bench} 道基准题目到单独文件 ===")
            bench_data = generator.generate_mixed_questions(0, 0, 0, args.bench)
            bench_output = args.output.replace('.json', '_bench.json')
            output_data = {"big_small": bench_data["big_small"], "questions": bench_data["questions"]}
            save_json_compact(output_data, bench_output)
            print(f"基准题目文件: {bench_output}")
    else:
        # 生成混合文件
        dataset = generator.generate_mixed_questions(args.easy, args.medium, args.hard, args.bench)
        
        output_data = {"big_small": dataset["big_small"], "questions": dataset["questions"]}
        save_json_compact(output_data, args.output)
        
        answer_file = args.output.replace('.json', '_with_answers.json')
        with open(answer_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
            
        print(f"\n生成完成!")
        print(f"题目文件: {args.output}")
        print(f"答案文件: {answer_file}")
        print(f"简单题目: {dataset['metadata']['easy_count']} 道")
        print(f"中等题目: {dataset['metadata']['medium_count']} 道")
        print(f"困难题目: {dataset['metadata']['hard_count']} 道")
        print(f"基准题目: {dataset['metadata']['bench_count']} 道")
        print(f"总题目数: {dataset['metadata']['total_questions']} 道")
        print(f"平均会议数量: {dataset['metadata']['avg_meetings']:.1f}")

if __name__ == "__main__":
    main() 