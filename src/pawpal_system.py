from dataclasses import dataclass
from typing import Optional
from enum import Enum
import json


class TimeOfDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    AS_NEEDED = "as_needed"


@dataclass
class Task:
    task_id: str
    name: str
    description: str
    category: str               # walk, feed, medication, grooming, enrichment
    duration: int               # minutes
    priority: int               # 1 (low) to 3 (high)
    frequency: Frequency = Frequency.DAILY
    preferred_time: Optional[TimeOfDay] = None
    is_completed: bool = False

    def complete(self) -> None:
        """Mark this task as done."""
        self.is_completed = True

    def reset(self) -> None:
        """Reset completion status (e.g. for a new day)."""
        self.is_completed = False

    def generate_next_occurrence(self) -> Optional['Task']:
        """
        Generate a new task instance for the next occurrence (daily/weekly).
        Returns None if the task is 'as_needed' (non-recurring).
        """
        if self.frequency == Frequency.AS_NEEDED:
            return None  # No automatic recurrence

        # Create a new task instance for the next occurrence
        next_task = Task(
            task_id=f"{self.task_id}_next",
            name=self.name,
            description=self.description,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            is_completed=False,
        )
        return next_task

    def to_dict(self) -> dict:
        """Serialize task to a dictionary for display or storage."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
            "frequency": self.frequency.value,
            "preferred_time": self.preferred_time.value if self.preferred_time else None,
            "is_completed": self.is_completed,
        }


class Pet:
    def __init__(self, name: str, species: str, age: int, special_needs: list[str] = None):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs or []
        self.tasks: list[Task] = []         # tasks belong to the pet

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by its ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def complete_and_reschedule(self, task_id: str) -> Optional[Task]:
        """
        Mark a task complete and create a new instance for the next occurrence.
        Returns the newly created task, or None if the task is non-recurring.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                task.complete()
                next_task = task.generate_next_occurrence()
                if next_task:
                    self.add_task(next_task)
                    return next_task
                return None
        return None  # Task not found

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_profile(self) -> str:
        """Return a readable summary of this pet."""
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.species}, age {self.age}) — special needs: {needs}"

    def to_dict(self) -> dict:
        """Serialize pet and its tasks to a dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "special_needs": self.special_needs,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @staticmethod
    def from_dict(data: dict) -> 'Pet':
        """Deserialize a pet from a dictionary."""
        pet = Pet(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            special_needs=data.get("special_needs", []),
        )
        for task_data in data.get("tasks", []):
            task = Task(
                task_id=task_data["task_id"],
                name=task_data["name"],
                description=task_data["description"],
                category=task_data["category"],
                duration=task_data["duration"],
                priority=task_data["priority"],
                frequency=Frequency(task_data["frequency"]),
                preferred_time=TimeOfDay(task_data["preferred_time"]) if task_data["preferred_time"] else None,
                is_completed=task_data["is_completed"],
            )
            pet.add_task(task)
        return pet


class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict = None):
        self.name = name
        self.available_time = available_time    # total minutes available per day
        self.preferences = preferences or {}
        self.pets: list[Pet] = []               # owner manages multiple pets

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> list[Task]:
        """Collect and return tasks across all pets — entry point for Scheduler."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def to_dict(self) -> dict:
        """Serialize owner and all pets/tasks to a dictionary."""
        return {
            "name": self.name,
            "available_time": self.available_time,
            "preferences": self.preferences,
            "pets": [p.to_dict() for p in self.pets],
        }

    def save_to_json(self, filename: str = "data.json") -> None:
        """Save owner, pets, and tasks to a JSON file."""
        data = self.to_dict()
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_from_json(filename: str = "data.json") -> Optional['Owner']:
        """Load owner, pets, and tasks from a JSON file. Returns None if file doesn't exist."""
        try:
            with open(filename, "r") as f:
                data = json.load(f)

            owner = Owner(
                name=data["name"],
                available_time=data["available_time"],
                preferences=data.get("preferences", {}),
            )
            for pet_data in data.get("pets", []):
                pet = Pet.from_dict(pet_data)
                owner.add_pet(pet)

            return owner
        except FileNotFoundError:
            return None


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.unscheduled_tasks: list[Task] = []
        self.explanations: dict[str, str] = {}  # task_id -> reason string
        self.conflicts: list[str] = []  # warning messages for time conflicts

    def generate_plan(self) -> None:
        """Main entry point: build the daily plan from the owner's pets' tasks."""
        # reset state so re-runs don't stack
        self.scheduled_tasks = []
        self.unscheduled_tasks = []
        self.explanations = {}
        self.conflicts = []

        ordered = self.prioritize_tasks()
        time_remaining = self.owner.available_time

        for task in ordered:
            if task.duration <= time_remaining:
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration
                self.explanations[task.task_id] = (
                    f"Scheduled '{task.name}' ({task.duration} min, priority {task.priority})"
                )
            else:
                self.unscheduled_tasks.append(task)
                self.explanations[task.task_id] = (
                    f"Skipped '{task.name}' — not enough time remaining ({time_remaining} min left)"
                )

        # Detect conflicts after scheduling
        self.detect_conflicts()

    def prioritize_tasks(self) -> list[Task]:
        """
        Retrieve all tasks from the owner's pets and sort them.
        Higher priority first; within same priority, shorter tasks first.
        Completed tasks are excluded.
        """
        # Scheduler reaches tasks via: Scheduler -> Owner -> Pet -> Tasks
        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.is_completed]
        return sorted(pending, key=lambda t: (-t.priority, t.duration))

    def detect_conflicts(self) -> None:
        """
        Detect if multiple tasks are scheduled for the same preferred time.
        Lightweight strategy: collect warnings without crashing.
        """
        self.conflicts = []

        # Group tasks by their preferred_time
        time_groups: dict[Optional[TimeOfDay], list[Task]] = {}
        for task in self.scheduled_tasks:
            if task.preferred_time is not None:  # Only check tasks with explicit time preferences
                if task.preferred_time not in time_groups:
                    time_groups[task.preferred_time] = []
                time_groups[task.preferred_time].append(task)

        # Check each time slot for conflicts (more than one task)
        for time_slot, tasks in time_groups.items():
            if len(tasks) > 1:
                task_list = ", ".join(f"'{t.name}' ({t.duration} min)" for t in tasks)
                warning = f"⚠ Conflict at {time_slot.value}: {task_list} — owner needs {sum(t.duration for t in tasks)} min"
                self.conflicts.append(warning)

    def explain_plan(self) -> dict[str, str]:
        """Return the reasoning behind each scheduling decision."""
        return self.explanations

    def display_plan(self) -> None:
        """Print a formatted summary of the daily plan."""
        print(f"\n=== Daily Plan for {self.owner.name} ===")
        print(f"Available time: {self.owner.available_time} min\n")

        print("Scheduled:")
        for task in self.scheduled_tasks:
            print(f"  [{task.preferred_time.value if task.preferred_time else 'anytime'}] "
                  f"{task.name} — {task.duration} min (priority {task.priority})")

        if self.unscheduled_tasks:
            print("\nCould not fit:")
            for task in self.unscheduled_tasks:
                print(f"  {task.name} — {task.duration} min")

        # Display conflicts if any
        if self.conflicts:
            print("\nScheduling Conflicts:")
            for conflict in self.conflicts:
                print(f"  {conflict}")

        print("\nReasons:")
        for reason in self.explanations.values():
            print(f"  - {reason}")
    
    def sort_by_time(self) -> None:
        """Sort scheduled tasks by their preferred time of day."""
        # Define time order: morning < afternoon < evening < anytime
        time_order = {
        TimeOfDay.MORNING: 0,
        TimeOfDay.AFTERNOON: 1,
        TimeOfDay.EVENING: 2,
        None: 3  # anytime goes last
        }
        self.scheduled_tasks.sort(key=lambda t: time_order.get(t.preferred_time, 3))

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> list[Task]:
        """
        Filter scheduled tasks by completion status and/or pet name.
        
        Args:
            completed: If True, return only completed tasks; if False, only pending tasks; if None, all tasks.
            pet_name: If provided, return only tasks belonging to the pet with this name.
        
        Returns:
            Filtered list of tasks.
        """
        filtered = self.scheduled_tasks
        
        if completed is not None:
            filtered = [t for t in filtered if t.is_completed == completed]
        
        if pet_name is not None:
            pet_task_ids = set()
            for pet in self.owner.pets:
                if pet.name == pet_name:
                    pet_task_ids.update(t.task_id for t in pet.tasks)
            filtered = [t for t in filtered if t.task_id in pet_task_ids]
        
        return filtered