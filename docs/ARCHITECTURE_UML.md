graph TD
    %% Core Domain Classes
    class Task {
        -task_id: str
        -name: str
        -description: str
        -category: str
        -duration: int
        -priority: int (1-3)
        -frequency: Frequency
        -preferred_time: Optional[TimeOfDay]
        -is_completed: bool
        +complete()
        +reset()
        +generate_next_occurrence(): Optional[Task]
        +to_dict(): dict
    }

    class Pet {
        -name: str
        -species: str
        -age: int
        -special_needs: list[str]
        -tasks: list[Task]
        +add_task(task: Task)
        +remove_task(task_id: str)
        +complete_and_reschedule(task_id: str): Optional[Task]
        +get_tasks(): list[Task]
        +get_profile(): str
        +to_dict(): dict
        +from_dict(data: dict)
    }

    class Owner {
        -name: str
        -available_time: int
        -preferences: dict
        -pets: list[Pet]
        +add_pet(pet: Pet)
        +remove_pet(pet_name: str)
        +get_all_tasks(): list[Task]
        +to_dict(): dict
        +save_to_json(filename: str)
        +load_from_json(filename: str)
    }

    class Scheduler {
        -owner: Owner
        -scheduled_tasks: list[Task]
        -unscheduled_tasks: list[Task]
        -explanations: dict[str, str]
        -conflicts: list[str]
        +generate_plan()
        +prioritize_tasks(): list[Task]
        +detect_conflicts()
        +explain_plan(): dict[str, str]
        +display_plan()
    }

    %% Enums
    class TimeOfDay {
        MORNING
        AFTERNOON
        EVENING
    }

    class Frequency {
        DAILY
        WEEKLY
        AS_NEEDED
    }

    %% AI Components
    class PetCareRAG {
        -guidelines: dict
        -task_history: list[dict]
        -guidelines_path: str
        +_load_guidelines(path: str): dict
        +retrieve_pet_guidelines(pet: Pet): str
        +retrieve_task_guidance(task: Task): str
        +retrieve_time_slot_guidance(): str
        +record_task_outcome(task, completed, notes)
    }

    class SchedulingDecision {
        -task_id: str
        -task_name: str
        -scheduled: bool
        -reasoning: str
        -confidence_score: float
        -alternative_times: list[str]
        -timestamp: str
        -model_used: str
    }

    class AISchedulingAgent {
        -model: str
        -use_ollama: bool
        -rag: PetCareRAG
        -decisions: list[SchedulingDecision]
        +generate_schedule_with_reasoning(owner: Owner): dict
        -_build_scheduling_prompt(...): str
        -_query_ollama(prompt: str): str
        -_mock_reasoning(): str
        -_evaluate_schedule(...): list[SchedulingDecision]
        -_calculate_confidence(...): float
        -_find_alternatives(task: Task): list[str]
        -_generate_alternatives(...): list[dict]
        +record_feedback(task_id, feedback, success)
    }

    class AISchedulerIntegration {
        -agent: AISchedulingAgent
        +schedule_with_ai(owner: Owner): dict
        +get_decision_history(): list[SchedulingDecision]
        +export_decisions(filepath: str)
    }

    class AIDecisionLogger {
        -log_dir: Path
        -logger: Logger
        -decision_journal: list[dict]
        +log_scheduling_decision(...)
        +log_conflict_detection(conflicts: list)
        +log_plan_generation(...)
        +log_plan_summary(...)
        +log_error(error_type, message, recovery_action)
        +log_user_feedback(task_id, feedback, success)
        +export_journal(filepath: str): str
        +get_reliability_stats(): dict
        +generate_reliability_report(): str
    }

    %% Relationships
    Owner "1" -- "*" Pet : manages
    Pet "1" -- "*" Task : contains
    Task --> TimeOfDay : prefers
    Task --> Frequency : repeats

    Scheduler --> Owner : schedules for
    Scheduler --> Task : orders

    PetCareRAG --> Task : evaluates
    PetCareRAG --> Pet : analyzes

    AISchedulingAgent --> PetCareRAG : uses
    AISchedulingAgent --> Scheduler : wraps
    AISchedulingAgent --> SchedulingDecision : creates
    AISchedulingAgent --> AIDecisionLogger : logs to

    AISchedulerIntegration --> AISchedulingAgent : contains
    AISchedulerIntegration --> Owner : processes

    AIDecisionLogger --> SchedulingDecision : records
