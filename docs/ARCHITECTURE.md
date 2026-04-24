# System Architecture & Design Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   PAWPAL+ AI SYSTEM OVERVIEW                    │
└─────────────────────────────────────────────────────────────────┘

                      ┌──────────────────┐
                      │  Streamlit UI    │
                      │  (5 Tabs)        │
                      └────────┬─────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────┐          ┌─────────┐          ┌──────────────┐
   │Dashboard│          │  Manage │          │ AI Schedule  │
   │         │          │  Tasks  │          │  Generator   │
   └────┬────┘          └────┬────┘          └──────┬───────┘
        │                    │                       │
        └────────────────┬───┴───────────────────────┘
                         │
                    ┌────▼────┐
                    │ Session │
                    │  State  │
                    └────┬────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Owner Data  │  │ Pet Objects  │  │ AIScheduler      │
│ - Name      │  │ - Name       │  │ Integration      │
│ - Time      │  │ - Species    │  │ - Agent          │
│ - Prefs     │  │ - Age        │  │ - Logger         │
└─────────────┘  │ - Special    │  └─────────┬────────┘
                 │   Needs      │            │
                 │ - Tasks[]    │            │
                 └──────────────┘    ┌───────┴──────────┐
                                     │                  │
                            ┌────────▼──────────┐  ┌───▼─────────┐
                            │  Pet Care RAG     │  │  AI Agent   │
                            │ ┌──────────────┐  │  │ Loop        │
                            │ │ Guidelines   │  │  │ 1. Retrieve │
                            │ │ JSON         │  │  │ 2. Reason   │
                            │ │ - Dog rules  │  │  │ 3. Generate │
                            │ │ - Cat rules  │  │  │ 4. Evaluate │
                            │ │ - Rabbit...  │  │  │ 5. Select   │
                            │ │ - Task hints │  │  └─────────────┘
                            │ │ - Time slots │  │
                            │ └──────────────┘  │
                            └───────┬───────────┘
                                    │
                        ┌───────────▼──────────────┐
                        │  Ollama LLM (Optional)   │
                        │  - Deepseek, Qwen, Gemma│
                        │  - Runs Locally          │
                        │  - Fallback: Mock Mode   │
                        └──────────────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │ Decision Logging System        │
                    │ ┌──────────────────────────┐  │
                    │ │ Decision Journal         │  │
                    │ │ - Task ID                │  │
                    │ │ - Scheduled: bool        │  │
                    │ │ - Confidence: float      │  │
                    │ │ - Reasoning: string      │  │
                    │ │ - Timestamp              │  │
                    │ └──────────────────────────┘  │
                    │ ┌──────────────────────────┐  │
                    │ │ Analytics & Reports      │  │
                    │ │ - Reliability stats      │  │
                    │ │ - Decision confidence    │  │
                    │ │ - Success rates          │  │
                    │ └──────────────────────────┘  │
                    └───────────┬──────────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Output to User         │
                    │ - Schedule + reasoning  │
                    │ - Confidence scores     │
                    │ - Alternatives         │
                    │ - Conflict warnings     │
                    └─────────────────────────┘
```

---

## 2. AI Agent Decision Loop

```
┌──────────────────────────────────────────────────────────────────┐
│              AI AGENT AGENTIC WORKFLOW                           │
└──────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────────────────────────────┐
│ STEP 1: RETRIEVE CONTEXT                │
│                                         │
│ Owner: Get available time               │
│ Pets: Get all tasks (filter completed)  │
│ RAG: Load pet guidelines                │
│ RAG: Load task category defaults        │
│ RAG: Load time slot guidance            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 2: BUILD LLM PROMPT                │
│                                         │
│ Format:                                 │
│ - Owner name + available time           │
│ - Pet profiles (species, age, needs)    │
│ - Task list (name, duration, priority)  │
│ - Relevant guidelines                   │
│ - Task asking for reasoning             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 3: QUERY LLM (OR MOCK)             │
│                                         │
│ If Ollama available:                    │
│   → Query model (Deepseek, Qwen, etc.) │
│   → Get text reasoning                  │
│                                         │
│ Else:                                   │
│   → Return mock reasoning               │
│   → (Maintains system functionality)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 4: TRADITIONAL SCHEDULE            │
│                                         │
│ Run existing Scheduler:                 │
│ 1. Get all tasks                        │
│ 2. Sort by (priority, duration)         │
│ 3. Fit tasks greedily into time         │
│ 4. Detect conflicts                     │
│ 5. Generate explanations                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 5: EVALUATE DECISIONS              │
│                                         │
│ For each task:                          │
│ - Was it scheduled? (bool)              │
│ - Calculate confidence score            │
│ - Compose reasoning                     │
│ - Find alternatives                     │
│ - Create SchedulingDecision object      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 6: GENERATE ALTERNATIVES           │
│                                         │
│ Create 3 strategies:                    │
│ 1. Flexible (defer non-critical)        │
│ 2. Time-Optimized (batch tasks)         │
│ 3. Pet-Centric (per-pet optimization)   │
│                                         │
│ Rate each with success probability      │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ STEP 7: LOG EVERYTHING                  │
│                                         │
│ For each decision:                      │
│ - Log to decision_journal                │
│ - Calculate reliability stats            │
│ - Persist to JSON                        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ RETURN RESULT TO USER                   │
│                                         │
│ {                                       │
│   scheduled_tasks: [...],               │
│   unscheduled_tasks: [...],             │
│   explanations: {...},                  │
│   ai_reasoning: "text...",              │
│   decisions: [...],                     │
│   confidence_score: 0.82,               │
│   alternatives: [...],                  │
│   conflicts: [...]                      │
│ }                                       │
└────────────────┬────────────────────────┘
                 │
                 ▼
               END
```

---

## 3. Confidence Score Calculation

```
┌──────────────────────────────────────────────────────────────────┐
│         CONFIDENCE SCORE CALCULATION LOGIC                       │
└──────────────────────────────────────────────────────────────────┘

For each task:

  Base Confidence = 0.5  (neutral starting point)
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
   +0.3 if    -0.2 if        +0.1 if
   scheduled   unscheduled   preferred
   AND HIGH    AND            time
   PRIORITY    CRITICAL       ASSIGNED
   (priority   (medication)
   == 3)
    │               │               │
    └───────────────┼───────────────┘
                    │
                    ▼
           Final Score = base
           + positive adjustments
           - negative adjustments

           Clamped to [0.0, 1.0]

                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
   < 0.5        0.5-0.8         > 0.8
  (LOW)         (MEDIUM)        (HIGH)
   
   "Not           "Reasonable    "High
   confident"     confidence"    confidence"
```

---

## 4. Data Flow: Task → Scheduling → AI Reasoning

```
User Input
    │
    ├─→ Task {
    │     id: "t1"
    │     name: "Morning Walk"
    │     duration: 30
    │     priority: 3
    │     preferred_time: MORNING
    │   }
    │
    ▼
Scheduler (traditional)
    │
    ├─→ Prioritize: [(priority desc), (duration asc)]
    │   Result: [t1 (30min), t4 (5min), t2 (10min), ...]
    │
    ├─→ Fit to Timeline:
    │   time_available = 90 min
    │   
    │   Schedule t1: 30 min
    │   └─ time_remaining = 60 min ✓
    │   
    │   Schedule t4: 5 min  
    │   └─ time_remaining = 55 min ✓
    │   
    │   Schedule t2: 10 min
    │   └─ time_remaining = 45 min ✓
    │   
    │   Skip t3: 25 min (only 45 left but needs high priority spot)
    │   └─ Unscheduled
    │
    ├─→ Conflict Detection:
    │   Group by preferred_time:
    │   MORNING: [t1, t4] → ⚠️ CONFLICT (50 min in same slot)
    │
    ▼
AI Agent
    │
    ├─→ Retrieve Context:
    │   - Pet: Dog, age 3 (needs exercise)
    │   - Guideline: "Morning optimal for high-energy"
    │   - Conflict detected
    │
    ├─→ Query LLM:
    │   "High-priority morning tasks create conflict.
    │    Recommend deferring non-critical walk or
    │    splitting medication/feed to different times."
    │
    ├─→ Evaluate Confidence:
    │   t1 (walk): 0.75 (scheduled, high priority, but conflicts)
    │   t4 (meds): 0.95 (scheduled, critical, high priority)
    │   t2 (feed): 0.90 (scheduled, essential)
    │   t3 (train): 0.50 (unscheduled, time constraint)
    │
    ├─→ Generate Alternatives:
    │   Alt 1: "Defer training, keep critical tasks in morning"
    │   Alt 2: "Move medication to evening, free morning slot"
    │   Alt 3: "Extend available time to 120 min"
    │
    ▼
Logging System
    │
    ├─→ Record All Decisions:
    │   {
    │     task_id: "t1",
    │     scheduled: true,
    │     confidence: 0.75,
    │     reasoning: "High priority, fits time, but conflicts...",
    │     timestamp: "2026-04-19T10:15:00",
    │     model_used: "deepseek-r1:1.5b"
    │   }
    │
    ├─→ Calculate Stats:
    │   total_decisions: 4
    │   avg_confidence: 0.78
    │   high_confidence: 2/4
    │
    ▼
Display to User
    │
    ├─→ Scheduled (3 tasks, 45 min used):
    │   ✓ t1 Morning Walk (0.75 confidence)
    │   ✓ t4 Medication (0.95 confidence)
    │   ✓ t2 Feeding (0.90 confidence)
    │
    ├─→ Unscheduled (1 task):
    │   ⏳ t3 Training (0.50 confidence)
    │
    ├─→ Alternatives:
    │   → Strategy 1 (Success: 85%)
    │   → Strategy 2 (Success: 80%)
    │   → Strategy 3 (Success: 78%)
    │
    └─→ Overall Score: 0.78 / 1.0
```

---

## 5. Class Relationships (UML Simplified)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLASS ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐
│  Owner   │
├──────────┤
│ name     │
│ time_avl │◄──────────┐
│ prefs    │           │
│ pets[]   │───┐       │
└──────────┘   │       │
               │       │
               ▼       │
           ┌──────┐    │
           │ Pet  │    │ Has Many
           ├──────┤    │
           │ name │    │
           │ spec │    │
           │ age  │    │
           │ task│─┐   │
           └──────┘ │   │
                    │   │
                    ▼   │
                ┌────────┤
                │ Task   │
                ├────────┤
                │ id     │
                │ name   │
                │ desc   │
                │ dur    │
                │ prio   │
                │ time   │
                │ freq   │
                │ done   │
                └────────┘


┌──────────────┐
│ Scheduler    │
├──────────────┤
│ owner: Owner │ ←─┐
│ scheduled[]  │   │
│ unscheduled[]    │ Uses
│ conflicts    │   │
├──────────────┤   │
│generate_plan()   │
│prioritize_tasks()
│detect_conflicts()
└──────────────┘


┌───────────────────┐
│ AIScheduler       │
│ Integration       │
├───────────────────┤
│ agent: AIAgent    │
├───────────────────┤
│ schedule_w_AI()   │
└───────────────────┘
        ▲
        │ Contains
        │
┌───────┴─────────────────┐
│ AISchedulingAgent       │
├─────────────────────────┤
│ model: str              │
│ rag: PetCareRAG         │◄─────┐
│ decisions: list         │      │ Uses
├─────────────────────────┤      │
│ generate_schedule()     │      │
│ _evaluate_schedule()    │      │
│ _generate_alternatives()      │
└─────────────────────────┘      │
                                  │
                         ┌────────┴──┐
                         │PetCareRAG │
                         ├───────────┤
                         │guidelines │
                         │ history   │
                         ├───────────┤
                         │retrieve_  │
                         │guidelines │
                         └───────────┘


┌──────────────────┐
│ Decision         │
│ Decision         │
├──────────────────┤
│ task_id: str     │
│ task_name: str   │
│ scheduled: bool  │
│ reasoning: str   │
│ confidence: 0-1  │
│ alternatives: [] │
│ timestamp: str   │
│ model_used: str  │
└──────────────────┘


┌─────────────────────┐
│ AIDecisionLogger    │
├─────────────────────┤
│ log_dir: Path       │
│ logger: Logger      │
│ decision_journal: []│
├─────────────────────┤
│ log_scheduling_     │
│ decision()          │
│ get_reliability_    │
│ stats()             │
│ generate_report()   │
└─────────────────────┘
```

---

## 6. File Organization

```
applied-ai-system-project/
│
├── Core Logic
│   ├── pawpal_system.py      ← Task, Pet, Owner, Scheduler
│   ├── ai_agent.py           ← AISchedulingAgent, PetCareRAG
│   └── ai_logging.py         ← AIDecisionLogger, reliability tracking
│
├── Data & Configuration
│   ├── pet_care_guidelines.json  ← Knowledge base
│   ├── data.json                 ← User data (persistent)
│   └── requirements.txt          ← Dependencies
│
├── UI & Frontend
│   └── app.py                ← Streamlit app (5 tabs)
│
├── Testing & Scripts
│   ├── main.py              ← Example usage script
│   ├── tests/
│   │   ├── test_pawpal.py              ← Original tests
│   │   └── test_ai_reliability.py      ← AI-specific tests
│   └── logs/                ← Generated decision logs
│
└── Documentation
    ├── README.md            ← Full documentation
    ├── ARCHITECTURE.md      ← This file
    └── ETHICS_REFLECTION.md ← Ethics & limitations
```

---

## 7. Testing Strategy

```
┌──────────────────────────────────────────────────────────────────┐
│           TESTING PYRAMID & COVERAGE                            │
└──────────────────────────────────────────────────────────────────┘

                        ▲
                       ╱ ╲
                      ╱   ╲
                     ╱ E2E ╲          (End-to-End Integration)
                    ╱       ╲         - Full system workflow
                   ╱─────────╲        - Real scheduling scenarios
                  ╱           ╲
                 ╱ Integration ╲      (Component Integration)
                ╱               ╲     - AI Agent + Scheduler
               ╱─────────────────╲    - Logging + Decision storage
              ╱                   ╲
             ╱   Unit Tests        ╲  (Individual Components)
            ╱                       ╲ - Task completion
           ╱─────────────────────────╲ - Confidence calculation
          ╱                           ╲ - RAG retrieval
         ╱_____________________________╲
        └───────────────────────────────┘

Test Categories:
✅ RAG System (1 test group)
✅ AI Agent (2 test groups)
✅ Scheduling Decisions (2 test groups)
✅ Integration (3 test groups)
✅ Reliability/Edge Cases (2 test groups)
✅ Logging (3 test groups)
✅ Error Handling (1 test group)
⏳ Ollama Integration (requires setup)

Total: 7/8 groups passing
```

This architecture is designed to be:
- **Modular**: Each component has a clear responsibility
- **Testable**: Mock Ollama enables local testing
- **Extensible**: Easy to add new pet types, guidelines, metrics
- **Transparent**: Logging enables auditing and improvement
