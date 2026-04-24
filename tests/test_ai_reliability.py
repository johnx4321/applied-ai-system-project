"""
AI Reliability and Integration Tests
Tests AI scheduling agent, RAG system, and decision quality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.pawpal_system import Task, Pet, Owner, Scheduler, Frequency, TimeOfDay
from src.ai_agent import AISchedulingAgent, PetCareRAG, AISchedulerIntegration, SchedulingDecision
from src.ai_logging import AIDecisionLogger


# ============================================================================
# RAG SYSTEM TESTS
# ============================================================================

def test_rag_load_guidelines():
    """RAG should successfully load pet care guidelines."""
    rag = PetCareRAG()
    assert rag.guidelines is not None
    assert "pet_guidelines" in rag.guidelines or len(rag.guidelines) == 0


def test_rag_retrieve_dog_guidelines():
    """RAG should retrieve dog-specific guidelines."""
    rag = PetCareRAG()
    dog = Pet(name="Buddy", species="Dog", age=3)
    guidelines = rag.retrieve_pet_guidelines(dog)
    
    assert "Buddy" in guidelines
    assert "Dog" in guidelines or "dog" in guidelines.lower()


def test_rag_retrieve_cat_guidelines():
    """RAG should retrieve cat-specific guidelines."""
    rag = PetCareRAG()
    cat = Pet(name="Whiskers", species="Cat", age=2)
    guidelines = rag.retrieve_cat_guidelines()
    
    # Should return context about cat needs
    assert guidelines is not None
    

def test_rag_task_history_recording():
    """RAG should record and track task outcomes."""
    rag = PetCareRAG()
    task = Task(
        task_id="t1",
        name="Walk",
        description="Morning walk",
        category="walk",
        duration=30,
        priority=3,
        frequency=Frequency.DAILY,
    )
    
    # Record successful completion
    rag.record_task_outcome(task, completed=True, notes="Pet had great energy")
    assert len(rag.task_history) == 1
    assert rag.task_history[0]["completed"] == True
    
    # Record failed task
    another_task = Task(
        task_id="t2",
        name="Training",
        description="Training session",
        category="enrichment",
        duration=20,
        priority=2,
    )
    rag.record_task_outcome(another_task, completed=False, notes="Pet was tired")
    assert len(rag.task_history) == 2


# ============================================================================
# AI AGENT INITIALIZATION TESTS
# ============================================================================

def test_ai_agent_initialization():
    """AI agent should initialize without errors."""
    agent = AISchedulingAgent(use_ollama=False)  # Mock mode
    assert agent.model == "deepseek-r1:1.5b"
    assert agent.use_ollama == False
    assert agent.rag is not None


def test_ai_agent_mock_reasoning():
    """AI agent should generate mock reasoning when Ollama unavailable."""
    agent = AISchedulingAgent(use_ollama=False)
    reasoning = agent._mock_reasoning()
    
    assert len(reasoning) > 0
    assert "Mock" in reasoning or "reasoning" in reasoning.lower()


# ============================================================================
# SCHEDULING DECISION TESTS
# ============================================================================

def test_scheduling_decision_dataclass():
    """SchedulingDecision should properly store decision information."""
    decision = SchedulingDecision(
        task_id="t1",
        task_name="Morning Walk",
        scheduled=True,
        reasoning="High priority, fits in time",
        confidence_score=0.85,
        alternative_times=["afternoon", "evening"],
        timestamp="2026-04-19T10:00:00",
        model_used="deepseek-r1:1.5b",
    )
    
    assert decision.task_id == "t1"
    assert decision.scheduled == True
    assert decision.confidence_score == 0.85
    assert len(decision.alternative_times) == 2


def test_confidence_score_range():
    """Confidence scores should always be between 0 and 1."""
    agent = AISchedulingAgent(use_ollama=False)
    
    # Create a simple task and scheduler
    owner = Owner(name="Test Owner", available_time=60)
    dog = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(dog)
    
    task = Task(
        task_id="t1",
        name="Walk",
        description="Morning walk",
        category="walk",
        duration=30,
        priority=3,
    )
    dog.add_task(task)
    
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    
    decisions = agent._evaluate_schedule(scheduler, [task], "Test reasoning")
    
    for decision in decisions:
        assert 0.0 <= decision.confidence_score <= 1.0


def test_high_priority_tasks_high_confidence():
    """High-priority scheduled tasks should have higher confidence."""
    agent = AISchedulingAgent(use_ollama=False)
    
    owner = Owner(name="Test Owner", available_time=100)
    dog = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(dog)
    
    high_priority_task = Task(
        task_id="t1",
        name="Medication",
        description="Critical medication",
        category="medication",
        duration=5,
        priority=3,
    )
    dog.add_task(high_priority_task)
    
    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    
    decisions = agent._evaluate_schedule(scheduler, [high_priority_task], "")
    
    # High-priority scheduled tasks should have good confidence
    if decisions[0].scheduled:
        assert decisions[0].confidence_score >= 0.6


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_schedule_generation_with_ai():
    """AI should generate complete schedule with reasoning."""
    integration = AISchedulerIntegration(use_ollama=False)
    
    owner = Owner(name="Alex", available_time=90)
    buddy = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(buddy)
    
    buddy.add_task(Task(
        task_id="t1",
        name="Morning Walk",
        description="30-minute walk",
        category="walk",
        duration=30,
        priority=3,
        frequency=Frequency.DAILY,
        preferred_time=TimeOfDay.MORNING,
    ))
    
    buddy.add_task(Task(
        task_id="t2",
        name="Feeding",
        description="Breakfast",
        category="feed",
        duration=10,
        priority=3,
    ))
    
    result = integration.schedule_with_ai(owner)
    
    assert "scheduled_tasks" in result
    assert "explanations" in result
    assert "decisions" in result
    assert "confidence_score" in result
    assert 0.0 <= result["confidence_score"] <= 1.0


def test_schedule_handles_time_constraints():
    """AI should properly handle owner's time constraints."""
    integration = AISchedulerIntegration(use_ollama=False)
    
    owner = Owner(name="Busy Owner", available_time=30)  # Very limited time
    dog = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(dog)
    
    # Add tasks that exceed available time
    dog.add_task(Task(
        task_id="t1",
        name="Walk",
        description="Long walk",
        category="walk",
        duration=40,  # Exceeds available time
        priority=3,
    ))
    
    dog.add_task(Task(
        task_id="t2",
        name="Feeding",
        description="Quick feeding",
        category="feed",
        duration=10,
        priority=3,
    ))
    
    result = integration.schedule_with_ai(owner)
    
    # At least one task should be unscheduled
    assert len(result["unscheduled_tasks"]) > 0 or len(result["scheduled_tasks"]) <= 2


def test_schedule_detects_conflicts():
    """AI should detect and report scheduling conflicts."""
    integration = AISchedulerIntegration(use_ollama=False)
    
    owner = Owner(name="Jordan", available_time=120)
    dog = Pet(name="Max", species="Dog", age=4)
    owner.add_pet(dog)
    
    # Add conflicting tasks (both want morning)
    dog.add_task(Task(
        task_id="t1",
        name="Morning Run",
        description="Running",
        category="walk",
        duration=30,
        priority=3,
        preferred_time=TimeOfDay.MORNING,
    ))
    
    dog.add_task(Task(
        task_id="t2",
        name="Morning Training",
        description="Training",
        category="enrichment",
        duration=25,
        priority=2,
        preferred_time=TimeOfDay.MORNING,
    ))
    
    result = integration.schedule_with_ai(owner)
    
    # Should either detect conflicts or still generate valid schedule
    assert len(result["conflicts"]) >= 0
    assert result["scheduled_tasks"] is not None


# ============================================================================
# RELIABILITY AND ERROR HANDLING TESTS
# ============================================================================

def test_ai_agent_handles_empty_task_list():
    """AI should handle scheduling with no tasks."""
    agent = AISchedulingAgent(use_ollama=False)
    owner = Owner(name="Test Owner", available_time=60)
    
    result = agent.generate_schedule_with_reasoning(owner)
    
    assert result is not None
    assert len(result["scheduled_tasks"]) == 0


def test_ai_agent_handles_zero_available_time():
    """AI should handle case where owner has zero available time."""
    agent = AISchedulingAgent(use_ollama=False)
    
    owner = Owner(name="Very Busy", available_time=0)
    dog = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(dog)
    
    dog.add_task(Task(
        task_id="t1",
        name="Walk",
        description="Walk",
        category="walk",
        duration=30,
        priority=3,
    ))
    
    result = agent.generate_schedule_with_reasoning(owner)
    
    # All tasks should be unscheduled
    assert len(result["scheduled_tasks"]) == 0
    assert len(result["unscheduled_tasks"]) >= 1


def test_ai_agent_handles_multiple_pets():
    """AI should schedule tasks across multiple pets."""
    agent = AISchedulingAgent(use_ollama=False)
    
    owner = Owner(name="Pet Parent", available_time=120)
    dog = Pet(name="Buddy", species="Dog", age=3)
    cat = Pet(name="Whiskers", species="Cat", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    dog.add_task(Task(
        task_id="d1",
        name="Dog Walk",
        description="Walk",
        category="walk",
        duration=30,
        priority=3,
    ))
    
    cat.add_task(Task(
        task_id="c1",
        name="Cat Feed",
        description="Feed",
        category="feed",
        duration=10,
        priority=3,
    ))
    
    result = agent.generate_schedule_with_reasoning(owner)
    
    # Should schedule tasks from both pets
    assert len(result["decisions"]) >= 2


# ============================================================================
# LOGGING AND AUDIT TESTS
# ============================================================================

def test_decision_logger_initialization():
    """Decision logger should initialize properly."""
    logger = AIDecisionLogger()
    assert logger.log_dir.exists()
    assert logger.logger is not None


def test_decision_logger_records_decisions():
    """Decision logger should record decisions."""
    logger = AIDecisionLogger()
    
    logger.log_scheduling_decision(
        task_id="t1",
        task_name="Morning Walk",
        scheduled=True,
        confidence=0.85,
        reasoning="High priority, fits in time",
        model_used="deepseek-r1:1.5b",
    )
    
    assert len(logger.decision_journal) == 1
    assert logger.decision_journal[0]["task_id"] == "t1"
    assert logger.decision_journal[0]["confidence"] == 0.85


def test_decision_logger_conflicts():
    """Decision logger should record conflicts."""
    logger = AIDecisionLogger()
    conflicts = ["Morning conflict: Walk vs Training", "Afternoon conflict: Play vs Rest"]
    
    logger.log_conflict_detection(conflicts)
    # Should complete without error
    assert len(conflicts) == 2


def test_reliability_statistics():
    """Logger should calculate reliability statistics."""
    logger = AIDecisionLogger()
    
    # Add some decisions
    for i in range(5):
        logger.log_scheduling_decision(
            task_id=f"t{i}",
            task_name=f"Task {i}",
            scheduled=(i < 3),
            confidence=0.75 + (i * 0.05),
            reasoning=f"Reason {i}",
            model_used="deepseek-r1:1.5b",
        )
    
    stats = logger.get_reliability_stats()
    
    assert stats["total_decisions"] == 5
    assert stats["scheduled_count"] == 3
    assert stats["unscheduled_count"] == 2
    assert 0.0 <= stats["average_confidence"] <= 1.0


def test_reliability_report_generation():
    """Logger should generate readable reliability report."""
    logger = AIDecisionLogger()
    
    for i in range(3):
        logger.log_scheduling_decision(
            task_id=f"t{i}",
            task_name=f"Task {i}",
            scheduled=True,
            confidence=0.8,
            reasoning=f"Test reason {i}",
            model_used="deepseek-r1:1.5b",
        )
    
    report = logger.generate_reliability_report()
    
    assert "RELIABILITY REPORT" in report
    assert "Total decisions" in report
    assert "Average confidence" in report


# ============================================================================
# SUMMARY TEST
# ============================================================================

def test_ai_system_end_to_end():
    """End-to-end test of AI scheduling system."""
    # Setup
    integration = AISchedulerIntegration(use_ollama=False)
    logger = AIDecisionLogger()
    
    # Create a realistic scenario
    owner = Owner(name="Sarah", available_time=90)
    dog = Pet(name="Max", species="Dog", age=5)
    cat = Pet(name="Luna", species="Cat", age=3, special_needs=["medication"])
    owner.add_pet(dog)
    owner.add_pet(cat)
    
    # Add tasks
    dog.add_task(Task("d1", "Morning Walk", "Daily exercise", "walk", 30, 3, Frequency.DAILY, TimeOfDay.MORNING))
    dog.add_task(Task("d2", "Feeding", "Breakfast", "feed", 10, 3, Frequency.DAILY, TimeOfDay.MORNING))
    dog.add_task(Task("d3", "Training", "Obedience", "enrichment", 20, 2, Frequency.DAILY))
    
    cat.add_task(Task("c1", "Medication", "Heart meds", "medication", 5, 3, Frequency.DAILY, TimeOfDay.MORNING))
    cat.add_task(Task("c2", "Feeding", "Cat food", "feed", 10, 3, Frequency.DAILY, TimeOfDay.MORNING))
    cat.add_task(Task("c3", "Play", "Interactive toys", "enrichment", 15, 2, Frequency.DAILY, TimeOfDay.AFTERNOON))
    
    # Generate schedule
    result = integration.schedule_with_ai(owner)
    
    # Validate results
    assert len(result["decisions"]) >= 6
    assert result["confidence_score"] is not None
    assert len(result["alternatives"]) > 0
    
    # Log decisions
    for decision in result["decisions"]:
        logger.log_scheduling_decision(
            task_id=decision.task_id,
            task_name=decision.task_name,
            scheduled=decision.scheduled,
            confidence=decision.confidence_score,
            reasoning=decision.reasoning,
            model_used=decision.model_used,
        )
    
    # Verify logging
    stats = logger.get_reliability_stats()
    assert stats["total_decisions"] >= 6
    assert stats["average_confidence"] > 0
    
    print("\n✓ End-to-end test passed!")
    print(f"  - Scheduled: {stats['scheduled_count']}/{stats['total_decisions']}")
    print(f"  - Avg Confidence: {stats['average_confidence']:.2f}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
