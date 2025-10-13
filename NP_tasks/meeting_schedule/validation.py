def validation(data, answer):
    """
    验证给定的答案是否是一个有效的会议安排
    参数:
    data: json中question1字段，包含会议、参与者可用性和房间信息
    answer: 字符串答案，包含"Answer："后的安排
    返回:
    (bool, int, str): 布尔值表示答案是否有效，True代表无效，False代表有效，
                       整数表示安排的总参与人数，字符串提供错误信息（如有）
    """

    meetings = data["meetings"]
    attendee_availability = data["attendee_availability"]
    rooms = data["rooms"]

    if "Answer:" in answer:
        schedule_str = answer.split("Answer:")[-1].strip()
    else:
        return True, -1, "invalid answer: no 'Answer:' in answer"

    try:
        if schedule_str == "[]":  # Handle empty schedule case
            schedule = []
        else:
            if schedule_str.startswith('[') and schedule_str.endswith(']'):
                schedule_str = schedule_str[1:-1]  # Remove brackets
            
            schedule_str= schedule_str.replace("'", "")
            items = schedule_str.split('), (')
            
            schedule = []
            for item in items:
                parts = item.replace("(","").replace(")","").split(',')
                try:
                    meeting_id = int(parts[0].strip())
                    room_id = int(parts[1].strip())
                    start_time = int(parts[2].strip())
                    schedule.append((meeting_id, room_id, start_time))
                except (ValueError, IndexError):
                    return True, -1, "Invalid format within schedule items."


    except (ValueError, IndexError):  # Handle possible parsing errors
        return True, -1, "Invalid answer format. Should be a list of tuples: [(meeting_id, room_id, start_time), ...]"

    # 1. Check for overlapping meetings in the same room
    room_schedules = {}
    for meeting_id, room_id, start_time in schedule:
        if str(room_id) not in rooms:
            return True, -1, f"Invalid room ID: {room_id}"
        if str(meeting_id) not in meetings:
            return True, -1, f"Invalid meeting id:{meeting_id}"

        duration = meetings[str(meeting_id)]["duration"]
        end_time = start_time + duration
        if room_id not in room_schedules:
            room_schedules[room_id] = []
        for other_meeting_id, _, other_start_time in room_schedules[room_id]:
            other_duration = meetings[str(other_meeting_id)]["duration"]
            other_end_time = other_start_time + other_duration
            if start_time < other_end_time and end_time > other_start_time:
                return True, -1, f"Meeting {meeting_id} overlaps with meeting {other_meeting_id} in room {room_id}"
        room_schedules[room_id].append((meeting_id, room_id, start_time))


    # 2. Check for attendee availability and room capacity
    total_attendees = 0
    for meeting_id, room_id, start_time in schedule:
        attendees = meetings[str(meeting_id)]["attendees"]
        duration = meetings[str(meeting_id)]["duration"]
        end_time = start_time + duration
        room_capacity = rooms[str(room_id)]

        if len(attendees) > room_capacity:
            return True, -1, f"Meeting {meeting_id} exceeds room {room_id} capacity"

        for attendee_id in attendees:
            available = False
            if str(attendee_id) not in attendee_availability:
                return True, -1, f"Attendee {attendee_id} not found in availability data."

            for avail_start, avail_end in attendee_availability[str(attendee_id)]:
                if start_time >= avail_start and end_time <= avail_end:
                    available = True
                    break
            if not available:
                return True, -1, f"Attendee {attendee_id} is not available for meeting {meeting_id}"

        total_attendees += len(attendees)

    return False, total_attendees, f"Total attendees scheduled: {total_attendees}"