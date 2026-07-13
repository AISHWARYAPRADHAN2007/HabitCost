def get_achievements(
    total_habits,
    total_logs,
    total_spending,
    budget
):

    achievements = []


    # First habit
    achievements.append({
        "title": "🔥 Habit Starter",
        "description": "Created your first habit",
        "unlocked": total_habits >= 1
    })


    # Multiple habits
    achievements.append({
        "title": "📊 Finance Explorer",
        "description": "Added 10 habits",
        "unlocked": total_habits >= 10
    })


    # Tracking consistency
    achievements.append({
        "title": "💪 Consistency King",
        "description": "Tracked habits 7 times",
        "unlocked": total_logs >= 7
    })


    # Budget control
    achievements.append({
        "title": "🎯 Budget Master",
        "description": "Stayed within monthly budget",
        "unlocked": (
            budget > 0 
            and total_spending <= budget
        )
    })


    # Big tracker
    achievements.append({
        "title": "🚀 Habit Pro",
        "description": "Created 25 habits",
        "unlocked": total_habits >= 25
    })


    return achievements