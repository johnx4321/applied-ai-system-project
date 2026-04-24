from src.pawpal_system import Task, Pet, Owner, Scheduler, TimeOfDay, Frequency

# --- Setup Owner ---
owner = Owner(name="Alex", available_time=90)  # 90 minutes available today

# --- Setup Pets ---
buddy = Pet(name="Buddy", species="Dog", age=3)
whiskers = Pet(name="Whiskers", species="Cat", age=5, special_needs=["medication"])

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Add Tasks OUT OF ORDER to test sorting ---
# Intentionally add tasks in random order to demonstrate sorting works

# Low priority task
buddy.add_task(Task(
    task_id="t5",
    name="Brushing",
    description="Coat brushing session",
    category="grooming",
    duration=15,
    priority=1,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.EVENING,
))

# High priority, long duration
buddy.add_task(Task(
    task_id="t1",
    name="Morning Walk",
    description="30-minute walk around the neighborhood",
    category="walk",
    duration=30,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.MORNING,
))

# Medium priority enrichment
buddy.add_task(Task(
    task_id="t3",
    name="Fetch & Play",
    description="Backyard fetch session for enrichment",
    category="enrichment",
    duration=20,
    priority=2,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.AFTERNOON,
))

# Critical medication (high priority, short duration)
whiskers.add_task(Task(
    task_id="t4",
    name="Medication",
    description="Administer daily heart medication with food",
    category="medication",
    duration=5,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.MORNING,
))

# High priority feeding
buddy.add_task(Task(
    task_id="t2",
    name="Breakfast",
    description="Feed Buddy his morning kibble",
    category="feed",
    duration=10,
    priority=3,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.MORNING,
))

# INTENTIONAL CONFLICTS: Two tasks both want afternoon slot
# This will trigger conflict detection
whiskers.add_task(Task(
    task_id="t6",
    name="Afternoon Nap",
    description="Ensure cat has rest time after play",
    category="enrichment",
    duration=15,
    priority=2,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.AFTERNOON,  # CONFLICT with Fetch & Play (t3)
))

buddy.add_task(Task(
    task_id="t7",
    name="Training Session",
    description="Work on obedience training",
    category="enrichment",
    duration=20,
    priority=1,
    frequency=Frequency.DAILY,
    preferred_time=TimeOfDay.AFTERNOON,  # CONFLICT with both Fetch & Play (t3) and Afternoon Nap (t6)
))

# --- Print Pet Profiles ---
print("=== Pets ===")
for pet in owner.pets:
    print(f"  {pet.get_profile()}")

# --- Print Raw Task Order (as added) ---
print("\n=== Raw Task Order (as added) ===")
all_tasks = owner.get_all_tasks()
for task in all_tasks:
    print(f"  {task.task_id}: {task.name:20} | Category: {task.category:12} | "
          f"Duration: {task.duration:3}min | Priority: {task.priority}")

# --- Print Prioritized/Sorted Order ---
print("\n=== After Sorting (priority → duration) ===")
scheduler = Scheduler(owner)
ordered_tasks = scheduler.prioritize_tasks()
for task in ordered_tasks:
    print(f"  {task.task_id}: {task.name:20} | Category: {task.category:12} | "
          f"Duration: {task.duration:3}min | Priority: {task.priority}")

# --- Run Scheduler and Display Final Plan ---
scheduler.generate_plan()
scheduler.display_plan()

# --- Demonstrate Auto-Rescheduling ---
print("\n=== Task Completion & Auto-Rescheduling ===")
print(f"Tasks before completion: {len(owner.get_all_tasks())}")

# Complete the medication (daily task) - should create next occurrence
next_med = whiskers.complete_and_reschedule("t4")
print(f"✓ Completed medication (t4) → created next: {next_med.task_id if next_med else 'None'}")

# Complete the brushing (weekly task) - should create next occurrence
next_brush = buddy.complete_and_reschedule("t5")
print(f"✓ Completed brushing (t5) → created next: {next_brush.task_id if next_brush else 'None'}")

print(f"Tasks after completion: {len(owner.get_all_tasks())}")
print("\nTask list (showing new instances with _next suffix):")
for pet in owner.pets:
    for task in pet.get_tasks():
        status = "✓ done" if task.is_completed else "⊙ pending"
        print(f"  {task.task_id:20} {task.name:20} {status}")

# --- Demonstrate Conflict Detection ---
print("\n=== Conflict Detection Test ===")
print("Resetting owner and re-adding all tasks to test conflict detection...")

# Create fresh owner and pets for clean conflict test
owner2 = Owner(name="Jordan", available_time=120)
dog = Pet(name="Max", species="Dog", age=4)
cat = Pet(name="Smokey", species="Cat", age=2)
owner2.add_pet(dog)
owner2.add_pet(cat)

# Add tasks with intentional conflicts
dog.add_task(Task(
    task_id="c1",
    name="Dog Morning Run",
    description="Long run in park",
    category="walk",
    duration=30,
    priority=3,
    preferred_time=TimeOfDay.MORNING,
))

cat.add_task(Task(
    task_id="c2",
    name="Cat Breakfast",
    description="Feed cat in morning",
    category="feed",
    duration=10,
    priority=3,
    preferred_time=TimeOfDay.MORNING,  # CONFLICT: both morning
))

dog.add_task(Task(
    task_id="c3",
    name="Afternoon Training",
    description="Obedience work",
    category="enrichment",
    duration=25,
    priority=2,
    preferred_time=TimeOfDay.AFTERNOON,  # CONFLICT: both afternoon
))

cat.add_task(Task(
    task_id="c4",
    name="Afternoon Play",
    description="Interactive toy session",
    category="enrichment",
    duration=15,
    priority=2,
    preferred_time=TimeOfDay.AFTERNOON,  # CONFLICT: both afternoon
))

# Generate plan and show conflicts
conflict_scheduler = Scheduler(owner2)
conflict_scheduler.generate_plan()
conflict_scheduler.display_plan()

