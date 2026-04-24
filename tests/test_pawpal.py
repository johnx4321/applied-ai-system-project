import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pawpal_system import Task, Pet, Owner, Scheduler, Frequency, TimeOfDay


def test_task_completion():
    """Calling complete() should change is_completed from False to True."""
    task = Task(
        task_id="t1",
        name="Morning Walk",
        description="Walk around the block",
        category="walk",
        duration=30,
        priority=3,
        frequency=Frequency.DAILY,
    )

    assert task.is_completed == False   # starts incomplete
    task.complete()
    assert task.is_completed == True    # now marked done


def test_task_addition():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Buddy", species="Dog", age=3)

    assert len(pet.get_tasks()) == 0    # starts with no tasks

    task = Task(
        task_id="t2",
        name="Breakfast",
        description="Morning kibble",
        category="feed",
        duration=10,
        priority=3,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1    # now has one task


# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

def test_zero_duration_task():
    """Task with zero duration should be schedulable but contribute zero time."""
    owner = Owner("Alice", available_time=60)
    pet = Pet("Fluffy", "Cat", 2)
    owner.add_pet(pet)

    task = Task(
        task_id="t_zero",
        name="Observation",
        description="Just observe the cat",
        category="enrichment",
        duration=0,
        priority=1,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert task in scheduler.scheduled_tasks
    assert len(scheduler.unscheduled_tasks) == 0


def test_priority_out_of_range():
    """System should handle priorities outside 1-3 range gracefully."""
    owner = Owner("Bob", available_time=100)
    pet = Pet("Rex", "Dog", 5)
    owner.add_pet(pet)

    # Priority 0 and 5 should still sort
    task_p0 = Task("t_p0", "Task P0", "desc", "walk", 20, priority=0)
    task_p5 = Task("t_p5", "Task P5", "desc", "feed", 20, priority=5)
    pet.add_task(task_p0)
    pet.add_task(task_p5)

    scheduler = Scheduler(owner)
    ordered = scheduler.prioritize_tasks()

    # p5 should come before p0 (higher priority first)
    assert ordered[0].priority == 5
    assert ordered[1].priority == 0


def test_duplicate_task_ids():
    """Two tasks with same ID; both should be in system but behavior is traceable."""
    owner = Owner("Charlie", available_time=100)
    pet = Pet("Spot", "Dog", 3)
    owner.add_pet(pet)

    task1 = Task("duplicate_id", "Walk", "desc", "walk", 30, priority=2)
    task2 = Task("duplicate_id", "Feed", "desc", "feed", 15, priority=2)

    pet.add_task(task1)
    pet.add_task(task2)

    # Both tasks exist in the pet's list
    assert len(pet.get_tasks()) == 2
    # Both have same ID (no duplicate check enforced)
    assert pet.get_tasks()[0].task_id == pet.get_tasks()[1].task_id


def test_negative_available_time():
    """Owner with negative available_time should result in no scheduled tasks."""
    owner = Owner("Diana", available_time=-50)
    pet = Pet("Scout", "Dog", 4)
    owner.add_pet(pet)

    task = Task("t_neg", "Walk", "desc", "walk", 30, priority=3)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.scheduled_tasks) == 0
    assert len(scheduler.unscheduled_tasks) == 1


def test_perfect_time_fit():
    """Tasks that sum exactly to available_time should all schedule with 0 remaining."""
    owner = Owner("Eve", available_time=90)
    pet = Pet("Daisy", "Cat", 2)
    owner.add_pet(pet)

    task1 = Task("t1", "Walk", "desc", "walk", 50, priority=2)
    task2 = Task("t2", "Feed", "desc", "feed", 40, priority=2)
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.scheduled_tasks) == 2
    assert len(scheduler.unscheduled_tasks) == 0


# ============================================================================
# SORTING & PRIORITIZATION TESTS
# ============================================================================

def test_higher_priority_first():
    """Tasks with higher priority should be sorted before lower priority."""
    owner = Owner("Frank", available_time=1000)
    pet = Pet("Max", "Dog", 6)
    owner.add_pet(pet)

    task_p1 = Task("t_p1", "Low", "desc", "walk", 30, priority=1)
    task_p3 = Task("t_p3", "High", "desc", "feed", 20, priority=3)
    task_p2 = Task("t_p2", "Med", "desc", "groom", 25, priority=2)

    pet.add_task(task_p1)
    pet.add_task(task_p3)
    pet.add_task(task_p2)

    scheduler = Scheduler(owner)
    ordered = scheduler.prioritize_tasks()

    # Should be sorted: p3, p2, p1
    assert ordered[0].priority == 3
    assert ordered[1].priority == 2
    assert ordered[2].priority == 1


def test_same_priority_shorter_first():
    """Tasks with same priority should sort by duration (shorter first)."""
    owner = Owner("Grace", available_time=1000)
    pet = Pet("Bella", "Dog", 3)
    owner.add_pet(pet)

    task_30 = Task("t_30", "Long Walk", "desc", "walk", 30, priority=2)
    task_10 = Task("t_10", "Quick Walk", "desc", "walk", 10, priority=2)
    task_20 = Task("t_20", "Medium Walk", "desc", "walk", 20, priority=2)

    pet.add_task(task_30)
    pet.add_task(task_10)
    pet.add_task(task_20)

    scheduler = Scheduler(owner)
    ordered = scheduler.prioritize_tasks()

    # All priority 2, so sorted by duration: 10, 20, 30
    assert ordered[0].duration == 10
    assert ordered[1].duration == 20
    assert ordered[2].duration == 30


def test_completed_tasks_excluded():
    """Completed tasks should be excluded from prioritize_tasks()."""
    owner = Owner("Henry", available_time=1000)
    pet = Pet("Mocha", "Dog", 4)
    owner.add_pet(pet)

    task1 = Task("t1", "Walk", "desc", "walk", 30, priority=3)
    task2 = Task("t2", "Feed", "desc", "feed", 15, priority=2)

    pet.add_task(task1)
    pet.add_task(task2)

    task1.complete()  # Mark first task as completed

    scheduler = Scheduler(owner)
    ordered = scheduler.prioritize_tasks()

    # Only task2 should be in ordered list
    assert len(ordered) == 1
    assert ordered[0].task_id == "t2"


def test_sort_by_time_order():
    """sort_by_time() should order: morning → afternoon → evening → anytime."""
    owner = Owner("Ivy", available_time=1000)
    pet = Pet("Luna", "Cat", 1)
    owner.add_pet(pet)

    task_evening = Task("t_eve", "Evening", "desc", "groom", 20, priority=2, preferred_time=TimeOfDay.EVENING)
    task_morning = Task("t_mor", "Morning", "desc", "walk", 30, priority=2, preferred_time=TimeOfDay.MORNING)
    task_anytime = Task("t_any", "Anytime", "desc", "feed", 15, priority=2, preferred_time=None)
    task_afternoon = Task("t_aft", "Afternoon", "desc", "play", 25, priority=2, preferred_time=TimeOfDay.AFTERNOON)

    pet.add_task(task_evening)
    pet.add_task(task_morning)
    pet.add_task(task_anytime)
    pet.add_task(task_afternoon)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    scheduler.sort_by_time()

    # After sort, should be: morning, afternoon, evening, anytime
    assert scheduler.scheduled_tasks[0].preferred_time == TimeOfDay.MORNING
    assert scheduler.scheduled_tasks[1].preferred_time == TimeOfDay.AFTERNOON
    assert scheduler.scheduled_tasks[2].preferred_time == TimeOfDay.EVENING
    assert scheduler.scheduled_tasks[3].preferred_time == None


# ============================================================================
# RECURRENCE LOGIC TESTS
# ============================================================================

def test_as_needed_no_recurrence():
    """AS_NEEDED tasks should not generate next occurrence."""
    task = Task(
        task_id="t_asneeded",
        name="Nail Trim",
        description="Only when needed",
        category="grooming",
        duration=45,
        priority=2,
        frequency=Frequency.AS_NEEDED,
    )

    next_task = task.generate_next_occurrence()
    assert next_task is None


def test_daily_task_recurrence():
    """DAILY task should generate next occurrence with '_next' suffix."""
    task = Task(
        task_id="walk_1",
        name="Morning Walk",
        description="Daily walk",
        category="walk",
        duration=30,
        priority=3,
        frequency=Frequency.DAILY,
    )

    next_task = task.generate_next_occurrence()

    assert next_task is not None
    assert next_task.task_id == "walk_1_next"
    assert next_task.name == "Morning Walk"
    assert next_task.is_completed == False
    assert next_task.frequency == Frequency.DAILY


def test_weekly_task_recurrence():
    """WEEKLY task should generate next occurrence with '_next' suffix."""
    task = Task(
        task_id="groom_1",
        name="Grooming",
        description="Weekly groom",
        category="grooming",
        duration=60,
        priority=2,
        frequency=Frequency.WEEKLY,
    )

    next_task = task.generate_next_occurrence()

    assert next_task is not None
    assert next_task.task_id == "groom_1_next"
    assert next_task.frequency == Frequency.WEEKLY
    assert next_task.is_completed == False


def test_complete_and_reschedule():
    """Completing a task should mark it done and create next instance."""
    pet = Pet("Buddy", "Dog", 3)

    task = Task(
        task_id="feed_1",
        name="Breakfast",
        description="Feed in morning",
        category="feed",
        duration=10,
        priority=3,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    # Complete task
    new_task = pet.complete_and_reschedule("feed_1")

    # Original task marked complete
    assert task.is_completed == True

    # New task created with '_next' suffix
    assert new_task is not None
    assert new_task.task_id == "feed_1_next"
    assert new_task.is_completed == False

    # Both tasks now in pet's list
    assert len(pet.get_tasks()) == 2


def test_reschedule_preserves_attributes():
    """New task from reschedule should preserve all attributes."""
    pet = Pet("Daisy", "Cat", 2)

    task = Task(
        task_id="play_1",
        name="Play Session",
        description="Interactive play",
        category="enrichment",
        duration=20,
        priority=2,
        frequency=Frequency.DAILY,
        preferred_time=TimeOfDay.AFTERNOON,
    )
    pet.add_task(task)

    new_task = pet.complete_and_reschedule("play_1")

    # Verify all attributes copied
    assert new_task.name == task.name
    assert new_task.description == task.description
    assert new_task.category == task.category
    assert new_task.duration == task.duration
    assert new_task.priority == task.priority
    assert new_task.frequency == task.frequency
    assert new_task.preferred_time == task.preferred_time


def test_multiple_completions():
    """Completing a task twice should create two new instances."""
    pet = Pet("Rex", "Dog", 5)

    task = Task(
        task_id="med_1",
        name="Medication",
        description="Daily med",
        category="medication",
        duration=5,
        priority=3,
        frequency=Frequency.DAILY,
    )
    pet.add_task(task)

    # First completion
    next_1 = pet.complete_and_reschedule("med_1")
    assert next_1.task_id == "med_1_next"

    # Second completion on the new task
    next_2 = pet.complete_and_reschedule("med_1_next")
    assert next_2.task_id == "med_1_next_next"

    # All three tasks in list
    assert len(pet.get_tasks()) == 3


def test_complete_as_needed_returns_none():
    """Completing AS_NEEDED task should return None (no next)."""
    pet = Pet("Scout", "Dog", 4)

    task = Task(
        task_id="trim_1",
        name="Nail Trim",
        description="As needed",
        category="grooming",
        duration=30,
        priority=1,
        frequency=Frequency.AS_NEEDED,
    )
    pet.add_task(task)

    result = pet.complete_and_reschedule("trim_1")

    assert result is None
    assert task.is_completed == True
    assert len(pet.get_tasks()) == 1  # No new task created


def test_reschedule_nonexistent_task():
    """Rescheduling non-existent task should return None."""
    pet = Pet("Fluffy", "Cat", 3)

    result = pet.complete_and_reschedule("nonexistent_id")

    assert result is None


# ============================================================================
# CONFLICT DETECTION TESTS
# ============================================================================

def test_no_conflicts_different_times():
    """Tasks with different preferred times should have no conflicts."""
    owner = Owner("Jack", available_time=200)
    pet = Pet("Buddy", "Dog", 3)
    owner.add_pet(pet)

    task1 = Task("t1", "Walk", "desc", "walk", 30, priority=3, preferred_time=TimeOfDay.MORNING)
    task2 = Task("t2", "Feed", "desc", "feed", 20, priority=3, preferred_time=TimeOfDay.AFTERNOON)
    task3 = Task("t3", "Play", "desc", "play", 25, priority=2, preferred_time=TimeOfDay.EVENING)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 0


def test_no_conflicts_anytime_flexible():
    """Multiple 'anytime' tasks should not conflict."""
    owner = Owner("Karen", available_time=200)
    pet = Pet("Max", "Dog", 4)
    owner.add_pet(pet)

    task1 = Task("t1", "Walk", "desc", "walk", 30, priority=2, preferred_time=None)
    task2 = Task("t2", "Feed", "desc", "feed", 20, priority=2, preferred_time=None)
    task3 = Task("t3", "Play", "desc", "play", 25, priority=2, preferred_time=None)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # No conflicts for anytime tasks
    assert len(scheduler.conflicts) == 0


def test_conflict_duplicate_morning():
    """Two morning tasks should trigger conflict."""
    owner = Owner("Leo", available_time=1000)
    pet = Pet("Daisy", "Cat", 2)
    owner.add_pet(pet)

    task1 = Task("t1", "Feed1", "desc", "feed", 10, priority=3, preferred_time=TimeOfDay.MORNING)
    task2 = Task("t2", "Groom", "desc", "groom", 20, priority=2, preferred_time=TimeOfDay.MORNING)

    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # Should detect conflict
    assert len(scheduler.conflicts) == 1
    assert "MORNING" in scheduler.conflicts[0] or "morning" in scheduler.conflicts[0]


def test_conflict_multiple_afternoon():
    """Three afternoon tasks should generate single conflict with correct duration sum."""
    owner = Owner("Megan", available_time=2000)
    pet = Pet("Spot", "Dog", 5)
    owner.add_pet(pet)

    task1 = Task("t1", "Walk", "desc", "walk", 30, priority=2, preferred_time=TimeOfDay.AFTERNOON)
    task2 = Task("t2", "Play", "desc", "play", 25, priority=2, preferred_time=TimeOfDay.AFTERNOON)
    task3 = Task("t3", "Train", "desc", "train", 40, priority=2, preferred_time=TimeOfDay.AFTERNOON)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # Should detect one conflict at afternoon
    assert len(scheduler.conflicts) == 1
    conflict_msg = scheduler.conflicts[0]
    # Should contain all three task names
    assert "Walk" in conflict_msg
    assert "Play" in conflict_msg
    assert "Train" in conflict_msg
    # Duration sum should be 30+25+40=95
    assert "95" in conflict_msg


def test_conflict_mixed_times():
    """Only overlapping times should have conflicts."""
    owner = Owner("Noah", available_time=2000)
    pet = Pet("Rex", "Dog", 6)
    owner.add_pet(pet)

    task1 = Task("t1", "Morning1", "desc", "walk", 20, priority=2, preferred_time=TimeOfDay.MORNING)
    task2 = Task("t2", "Morning2", "desc", "feed", 15, priority=2, preferred_time=TimeOfDay.MORNING)
    task3 = Task("t3", "Afternoon", "desc", "play", 25, priority=2, preferred_time=TimeOfDay.AFTERNOON)
    task4 = Task("t4", "Evening", "desc", "groom", 30, priority=2, preferred_time=TimeOfDay.EVENING)

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    pet.add_task(task4)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    # Only morning should have conflict
    assert len(scheduler.conflicts) == 1
    assert "Morning" in scheduler.conflicts[0] or "morning" in scheduler.conflicts[0]


def test_single_task_no_conflict():
    """Single task in a time slot should not be flagged as conflict."""
    owner = Owner("Olivia", available_time=1000)
    pet = Pet("Bella", "Cat", 3)
    owner.add_pet(pet)

    task = Task("t1", "Walk", "desc", "walk", 30, priority=2, preferred_time=TimeOfDay.MORNING)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 0
