import json
import argparse
import time
import random
from collections import defaultdict

class MeetingSchedulerSolver:
    """
    Solves the Meeting Scheduling Problem (MSP) with the objective of
    maximizing total attendee participation.
    Uses a Greedy Randomized Adaptive Search Procedure (GRASP) like heuristic.
    """
    def __init__(self, meetings, attendee_availability, rooms, timeout=60):
        self.meetings = meetings
        self.attendee_availability = attendee_availability
        self.rooms = rooms
        self.timeout = timeout
        self.start_time = None
        self.best_schedule = []
        self.best_score = 0

    @staticmethod
    def _is_overlapping(start1, end1, start2, end2):
        """Check if two time intervals [start1, end1) and [start2, end2) overlap."""
        return max(start1, start2) < min(end1, end2)

    def _get_attendee_free_slots(self, attendees, duration):
        """
        Calculates the common free time slots for a group of attendees.
        This is a complex interval intersection problem.
        """
        if not attendees:
            return [(0, float('inf'))]
        
        # Start with the availability of the first attendee
        common_slots = self.attendee_availability.get(attendees[0], [])
        
        for attendee_id in attendees[1:]:
            next_slots = self.attendee_availability.get(attendee_id, [])
            intersected_slots = []
            i, j = 0, 0
            while i < len(common_slots) and j < len(next_slots):
                start1, end1 = common_slots[i]
                start2, end2 = next_slots[j]
                
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)
                
                if overlap_start < overlap_end:
                    intersected_slots.append((overlap_start, overlap_end))
                
                if end1 < end2:
                    i += 1
                else:
                    j += 1
            common_slots = intersected_slots

        # Filter slots that are long enough for the meeting
        return [(start, end) for start, end in common_slots if end - start >= duration]

    def _construct_schedule(self):
        """
        Constructs a single valid schedule using a greedy randomized heuristic.
        """
        current_schedule = []
        unscheduled_meetings = list(self.meetings.keys())
        
        # Keep track of booked times for resources
        room_bookings = defaultdict(list)
        attendee_bookings = defaultdict(list)
        
        while unscheduled_meetings:
            candidate_placements = []
            
            for meeting_id in unscheduled_meetings:
                meeting = self.meetings[meeting_id]
                attendees = meeting['attendees']
                duration = meeting['duration']
                num_attendees = len(attendees)

                earliest_start = float('inf')
                best_room = -1

                # Check suitable rooms
                suitable_rooms = [r_id for r_id, cap in self.rooms.items() if cap >= num_attendees]
                
                # Find all common free slots for the attendees based on their personal calendars
                common_slots = self._get_attendee_free_slots(attendees, duration)
                found_placement_for_meeting = False

                for room_id in suitable_rooms:
                    # Iterate through the time windows where all attendees are free
                    for slot_start, slot_end in common_slots:
                        
                        current_check_time = slot_start
                        
                        # Search for a conflict-free time within this personal availability slot
                        while current_check_time + duration <= slot_end:
                            
                            conflict_end_time = current_check_time

                            # Check for room conflicts with already scheduled meetings
                            for r_start, r_end in room_bookings.get(room_id, []):
                                if self._is_overlapping(current_check_time, current_check_time + duration, r_start, r_end):
                                    conflict_end_time = max(conflict_end_time, r_end)

                            # Check for attendee conflicts with already scheduled meetings
                            for attendee_id in attendees:
                                for a_start, a_end in attendee_bookings.get(attendee_id, []):
                                    if self._is_overlapping(current_check_time, current_check_time + duration, a_start, a_end):
                                        conflict_end_time = max(conflict_end_time, a_end)
                            
                            if conflict_end_time > current_check_time:
                                # Conflict found, jump time forward
                                current_check_time = conflict_end_time
                            else:
                                # No conflicts! This is a valid placement.
                                earliest_start = current_check_time
                                best_room = room_id
                                found_placement_for_meeting = True
                                break  # Exit the `while` loop

                        if found_placement_for_meeting:
                            break  # Exit the `for slot_start, slot_end` loop
                    
                    if found_placement_for_meeting:
                        break  # Exit the `for room_id` loop

                if found_placement_for_meeting:
                    score = num_attendees / duration if duration > 0 else num_attendees
                    candidate_placements.append({
                        "meeting_id": meeting_id,
                        "room_id": best_room,
                        "start_time": earliest_start,
                        "score": score
                    })
            
            if not candidate_placements:
                break # No more meetings can be scheduled

            # GRASP: Create Restricted Candidate List (RCL) and choose randomly
            candidate_placements.sort(key=lambda x: x['score'], reverse=True)
            max_score = candidate_placements[0]['score']
            rcl_threshold = max_score * 0.8 
            rcl = [p for p in candidate_placements if p['score'] >= rcl_threshold]
            
            chosen_meeting = random.choice(rcl)
            
            # Add to schedule and book resources
            m_id = chosen_meeting['meeting_id']
            r_id = chosen_meeting['room_id']
            s_time = chosen_meeting['start_time']
            e_time = s_time + self.meetings[m_id]['duration']
            
            current_schedule.append((m_id, r_id, s_time))
            room_bookings[r_id].append((s_time, e_time))
            for att in self.meetings[m_id]['attendees']:
                attendee_bookings[att].append((s_time, e_time))
                
            unscheduled_meetings.remove(m_id)

        return current_schedule

    def _ruin_and_recreate(self, schedule, destruction_rate=0.2):
        """
        Improves a given schedule using the Ruin and Recreate principle.
        1. Ruin: Randomly removes a fraction of meetings from the schedule.
        2. Recreate: Greedily re-inserts the removed meetings and any previously
                     unscheduled meetings back into the partial schedule.
        """
        if not schedule: return []

        # --- 1. Ruin Phase ---
        partial_schedule = list(schedule)
        meetings_to_reinsert = []
        
        num_to_remove = int(len(partial_schedule) * destruction_rate)
        if num_to_remove > 0:
            removed_indices = sorted(random.sample(range(len(partial_schedule)), num_to_remove), reverse=True)
            for idx in removed_indices:
                meetings_to_reinsert.append(partial_schedule.pop(idx)[0])

        # Add meetings that were never scheduled in the first place
        scheduled_ids = {m_id for m_id, _, _ in partial_schedule}
        originally_unscheduled = [m_id for m_id in self.meetings if m_id not in scheduled_ids]
        meetings_to_reinsert.extend(originally_unscheduled)

        # Sort meetings to be re-inserted, prioritizing those with more attendees (higher value)
        meetings_to_reinsert.sort(key=lambda mid: len(self.meetings[mid]['attendees']), reverse=True)

        # --- 2. Recreate Phase ---
        # Re-create bookings based on the partial schedule
        room_bookings = defaultdict(list)
        attendee_bookings = defaultdict(list)
        for m_id, r_id, s_time in partial_schedule:
            e_time = s_time + self.meetings[m_id]['duration']
            room_bookings[r_id].append((s_time, e_time))
            for att in self.meetings[m_id]['attendees']:
                attendee_bookings[att].append((s_time, e_time))

        # Attempt to re-insert meetings one by one
        for meeting_id in meetings_to_reinsert:
            # This logic is very similar to the greedy insertion used before
            meeting = self.meetings[meeting_id]
            attendees = meeting['attendees']
            duration = meeting['duration']
            num_attendees = len(attendees)

            suitable_rooms = [r_id for r_id, cap in self.rooms.items() if cap >= num_attendees]
            common_slots = self._get_attendee_free_slots(attendees, duration)
            
            best_placement = None # Find the earliest possible placement
            earliest_start = float('inf')

            for room_id in suitable_rooms:
                for slot_start, slot_end in common_slots:
                    current_check_time = slot_start
                    while current_check_time + duration <= slot_end:
                        # Simplified conflict checking logic from before
                        is_conflict = False
                        # Check room
                        for r_start, r_end in room_bookings.get(room_id, []):
                            if self._is_overlapping(current_check_time, current_check_time + duration, r_start, r_end):
                                is_conflict = True; break
                        if is_conflict: current_check_time += 1; continue
                        # Check attendees
                        for att_id in attendees:
                            for a_start, a_end in attendee_bookings.get(att_id, []):
                                if self._is_overlapping(current_check_time, current_check_time + duration, a_start, a_end):
                                    is_conflict = True; break
                            if is_conflict: break
                        
                        if not is_conflict:
                            if current_check_time < earliest_start:
                                earliest_start = current_check_time
                                best_placement = (meeting_id, room_id, current_check_time)
                            break # Found earliest in this slot, move to next slot/room
                        else:
                            current_check_time += 1 # Basic time step
            
            if best_placement:
                m_id, r_id, s_time = best_placement
                e_time = s_time + self.meetings[m_id]['duration']
                partial_schedule.append(best_placement)
                room_bookings[r_id].append((s_time, e_time))
                for att in self.meetings[m_id]['attendees']:
                    attendee_bookings[att].append((s_time, e_time))

        return partial_schedule

    def solve(self):
        self.start_time = time.time()
        iteration = 0
        while time.time() - self.start_time < self.timeout:
            iteration += 1
            # 1. Construct a solution using GRASP
            schedule = self._construct_schedule()
            
            # 2. Improve the solution using Ruin and Recreate
            schedule = self._ruin_and_recreate(schedule)
            
            # 3. Evaluate and update the best-found solution
            score = sum(len(self.meetings[m_id]['attendees']) for m_id, _, _ in schedule)

            if score > self.best_score:
                self.best_score = score
                self.best_schedule = schedule
                print(f"   - Iteration {iteration}: New best schedule found with total attendance {score}")
        
        print(f"   - Finished after {iteration} iterations.")
        return sorted(self.best_schedule, key=lambda x: x[2])


def parse_question_data(data):
    meetings = {int(k): v for k, v in data['meetings'].items()}
    attendee_availability = {int(k): v for k, v in data['attendee_availability'].items()}
    rooms = {int(k): v for k, v in data['rooms'].items()}
    return meetings, attendee_availability, rooms

def main():
    parser = argparse.ArgumentParser(description="Solve Meeting Scheduling problems from a JSON file and add ground truth values.")
    parser.add_argument('--file', type=str, default='question.json', help='Path to the JSON file with MSP problems.')
    parser.add_argument('--timeout', type=float, default=0.01, help='Timeout in seconds for each problem.')
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        return
        
    questions = data.get("questions")
    if not questions:
        print(f"Error: No 'questions' key found in '{args.file}'")
        return
        
    total_questions = len(questions)
    
    for i, (question_name, question_data) in enumerate(sorted(questions.items())):
        print(f"--- [{i+1}/{total_questions}] Solving MSP for: {question_name} ---")
        
        meetings, attendee_availability, rooms = parse_question_data(question_data)
        
        solver = MeetingSchedulerSolver(meetings, attendee_availability, rooms, timeout=args.timeout)
        solution = solver.solve()
        
        score = sum(len(meetings[m_id]['attendees']) for m_id, _, _ in solution)
        # Add ground_truth field to the original question data
        question_data['ground_truth'] = score
        
        print(f"--- Finished {question_name}, Max Attendees: {score} ---")
        print("-" * 50)

    # Save the modified data back to the original file
    try:
        with open(args.file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSuccessfully processed all {total_questions} problems.")
        print(f"All solutions have been added to '{args.file}' with ground_truth fields.")
    except IOError as e:
        print(f"\nError writing solutions to file: {e}")

if __name__ == '__main__':
    main() 