def generate_plan(subject, hours):
    return [
        {"day": f"Day {i}", "task": f"{subject} study for {hours//5} hrs"}
        for i in range(1, 6)
    ]
