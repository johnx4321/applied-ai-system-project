"""
AI Agent for Intelligent Pet Care Scheduling
Combines Retrieval-Augmented Generation (RAG) with Agentic Workflow
Uses Ollama for local LLM inference
"""

import json
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
import time
from datetime import datetime

try:
    import ollama
except ImportError:
    ollama = None

import requests
from threading import Thread
from queue import Queue

from src.pawpal_system import Task, Pet, Owner, Scheduler, TimeOfDay, Frequency


logger = logging.getLogger(__name__)


@dataclass
class SchedulingDecision:
    """Represents an AI-made scheduling decision with reasoning and confidence."""
    task_id: str
    task_name: str
    scheduled: bool
    reasoning: str
    confidence_score: float  # 0.0 to 1.0
    alternative_times: List[str]
    timestamp: str
    model_used: str


class PetCareRAG:
    """
    Retrieval-Augmented Generation system for pet care knowledge.
    Retrieves relevant guidelines based on pet profile and task.
    """

    def __init__(self, guidelines_path: str = "pet_care_guidelines.json"):
        """Initialize RAG with pet care guidelines."""
        self.guidelines = self._load_guidelines(guidelines_path)
        self.task_history: List[Dict] = []  # Track completed tasks for learning

    def _load_guidelines(self, path: str) -> Dict:
        """Load pet care guidelines from JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Guidelines file {path} not found. Using empty guidelines.")
            return {}

    def retrieve_pet_guidelines(self, pet: Pet) -> str:
        """Retrieve relevant guidelines for a specific pet."""
        species = pet.species.lower()
        guidelines = self.guidelines.get("pet_guidelines", {}).get(species, {})
        
        # Build context string with pet-specific guidelines
        context = f"Pet: {pet.name} ({species}, age {pet.age})\n"
        if pet.special_needs:
            context += f"Special needs: {', '.join(pet.special_needs)}\n"
        
        for category, details in guidelines.items():
            context += f"- {category.title()}: {details.get('description', 'N/A')}\n"
        
        return context

    def retrieve_task_guidance(self, task: Task) -> str:
        """Retrieve guidelines for a specific task category."""
        category_defaults = self.guidelines.get("task_category_defaults", {}).get(
            task.category, {}
        )
        
        guidance = f"Task: {task.name} ({task.category})\n"
        guidance += f"Duration: {task.duration} min (Typical: {category_defaults.get('typical_duration', 'N/A')} min)\n"
        guidance += f"Frequency: {task.frequency.value} (Recommended: {category_defaults.get('frequency_recommendation', 'N/A')})\n"
        
        return guidance

    def retrieve_time_slot_guidance(self) -> str:
        """Retrieve guidance on time slot optimization."""
        time_guidance = self.guidelines.get("time_slot_guidance", {})
        context = "Time Slot Optimization Guidelines:\n"
        for slot, description in time_guidance.items():
            context += f"- {slot.title()}: {description}\n"
        return context

    def record_task_outcome(self, task: Task, completed: bool, notes: str = ""):
        """Record task completion for learning and pattern analysis."""
        outcome = {
            "task_id": task.task_id,
            "task_name": task.name,
            "category": task.category,
            "completed": completed,
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
        }
        self.task_history.append(outcome)


class AISchedulingAgent:
    """
    Agentic workflow for intelligent scheduling.
    Follows: Plan → Retrieve → Generate → Evaluate → Select
    """

    def __init__(self, model: str = "deepseek-r1:1.5b", use_ollama: bool = True):
        """
        Initialize the AI agent.
        
        Args:
            model: Ollama model name (e.g., "deepseek-r1:1.5b", "qwen2:1.5b", "gemma2")
            use_ollama: Whether to use Ollama (False = mock mode for testing)
        """
        self.model = model
        self.use_ollama = use_ollama and ollama is not None
        self.rag = PetCareRAG()
        self.decisions: List[SchedulingDecision] = []
        
        if self.use_ollama:
            logger.info(f"AISchedulingAgent initialized with model: {model}")
        else:
            logger.info("AISchedulingAgent in mock mode (no Ollama)")

    def generate_schedule_with_reasoning(self, owner: Owner) -> Dict:
        """
        Main agent entry point: Generate a schedule with AI reasoning.
        
        Returns dict with:
            - schedule: list of scheduled tasks
            - explanations: dict of task_id -> reasoning
            - confidence: average confidence score
            - alternatives: alternative scheduling options
        """
        logger.info(f"Agent: Starting schedule generation for {owner.name}")
        
        # Step 1: Retrieve all relevant context
        all_tasks = owner.get_all_tasks()
        pending_tasks = [t for t in all_tasks if not t.is_completed]
        
        # Step 2: Retrieve pet guidelines for all pets
        pet_contexts = [self.rag.retrieve_pet_guidelines(pet) for pet in owner.pets]
        time_guidance = self.rag.retrieve_time_slot_guidance()
        
        # Step 3: Build prompt for LLM
        prompt = self._build_scheduling_prompt(owner, pending_tasks, pet_contexts, time_guidance)
        
        # Step 4: Get LLM reasoning
        reasoning = self._query_ollama(prompt) if self.use_ollama else self._mock_reasoning()
        logger.info(f"Agent reasoning: {reasoning[:200]}...")
        
        # Step 5: Generate schedule using Scheduler + AI insights
        scheduler = Scheduler(owner)
        scheduler.generate_plan()
        
        # Step 6: Evaluate and score decisions
        decisions = self._evaluate_schedule(scheduler, pending_tasks, reasoning)
        self.decisions.extend(decisions)
        
        # Step 7: Generate alternatives
        alternatives = self._generate_alternatives(scheduler, pending_tasks)
        
        return {
            "scheduled_tasks": scheduler.scheduled_tasks,
            "unscheduled_tasks": scheduler.unscheduled_tasks,
            "explanations": scheduler.explain_plan(),
            "ai_reasoning": reasoning,
            "decisions": decisions,
            "confidence_score": sum(d.confidence_score for d in decisions) / len(decisions) if decisions else 0.5,
            "alternatives": alternatives,
            "conflicts": scheduler.conflicts,
        }

    def _build_scheduling_prompt(
        self,
        owner: Owner,
        tasks: List[Task],
        pet_contexts: List[str],
        time_guidance: str,
    ) -> str:
        """Build a detailed prompt for the LLM."""
        task_list = "\n".join(
            f"- {t.name} ({t.category}): {t.duration}min, priority {t.priority}, prefers {t.preferred_time.value if t.preferred_time else 'anytime'}"
            for t in tasks
        )
        
        pet_info = "\n".join(pet_contexts)
        
        prompt = f"""You are an intelligent pet care scheduling assistant.

Owner: {owner.name}
Available time: {owner.available_time} minutes per day

Pets:
{pet_info}

Pending Tasks:
{task_list}

{time_guidance}

Analyze this scheduling problem and provide:
1. Which tasks MUST be scheduled (critical)
2. Which tasks are IMPORTANT but flexible
3. Recommended scheduling strategy
4. Potential conflicts and how to resolve them
5. Confidence level in your recommendation (0-1 scale)

Be concise and actionable."""
        
        return prompt

    def _query_ollama(self, prompt: str, timeout: int = 60) -> str:
        """
        Query Ollama LLM for scheduling reasoning.
        
        Args:
            prompt: The prompt to send to the model
            timeout: Maximum time to wait for response in seconds (default: 60s)
        
        Returns:
            Model response or error message
        """
        try:
            logger.info(f"Querying Ollama ({self.model}) with timeout={timeout}s...")
            
            # Use requests with timeout instead of ollama library for better control
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Unable to generate reasoning").strip()
                else:
                    error_msg = f"Ollama returned status {response.status_code}"
                    logger.error(error_msg)
                    return f"Error: {error_msg}. Try disabling Ollama and using mock mode."
                    
            except requests.exceptions.Timeout:
                logger.error(f"Ollama query timed out after {timeout}s")
                return (
                    f"⏱️ Ollama timeout (>{timeout}s). Possible causes:\n"
                    "• Model is still loading (first query can be slow)\n"
                    "• Ollama server is slow/unresponsive\n"
                    "• Switch to Mock Mode in UI for instant results"
                )
            except requests.exceptions.ConnectionError:
                logger.error("Could not connect to Ollama server")
                return (
                    "❌ Cannot connect to Ollama server on localhost:11434\n"
                    "Ensure Ollama is running:\n"
                    "  • Open Terminal and run: ollama serve\n"
                    "  • Or start the Ollama app from Applications\n"
                    "For now, switch to Mock Mode in the AI Schedule tab"
                )
                
        except Exception as e:
            logger.error(f"Unexpected error querying Ollama: {e}")
            return (
                f"Error: {str(e)}\n"
                "Switch to Mock Mode in the AI Schedule tab for instant results."
            )

    def _mock_reasoning(self) -> str:
        """Mock reasoning for testing without Ollama."""
        return (
            "Mock AI Reasoning (Ollama not available):\n"
            "1. High-priority tasks (medications, feeding) must be scheduled first\n"
            "2. Morning time slots are optimal for high-energy activities\n"
            "3. Time conflicts should be resolved by adjusting flexible enrichment tasks\n"
            "4. Confidence: 0.75 (based on standard scheduling heuristics)"
        )

    def _evaluate_schedule(
        self, scheduler: Scheduler, tasks: List[Task], reasoning: str
    ) -> List[SchedulingDecision]:
        """Evaluate scheduled decisions and assign confidence scores."""
        decisions = []
        
        for task in tasks:
            is_scheduled = task in scheduler.scheduled_tasks
            confidence = self._calculate_confidence(
                task, is_scheduled, scheduler, reasoning
            )
            
            decision = SchedulingDecision(
                task_id=task.task_id,
                task_name=task.name,
                scheduled=is_scheduled,
                reasoning=scheduler.explain_plan().get(task.task_id, "No explanation"),
                confidence_score=confidence,
                alternative_times=self._find_alternatives(task),
                timestamp=datetime.now().isoformat(),
                model_used=self.model,
            )
            decisions.append(decision)
            logger.info(
                f"Decision: {task.name} - Scheduled: {is_scheduled}, Confidence: {confidence:.2f}"
            )
        
        return decisions

    def _calculate_confidence(
        self, task: Task, is_scheduled: bool, scheduler: Scheduler, reasoning: str
    ) -> float:
        """Calculate confidence score for a scheduling decision."""
        base_confidence = 0.5
        
        # Boost confidence for scheduled high-priority tasks
        if is_scheduled and task.priority == 3:
            base_confidence += 0.3
        
        # Reduce confidence for unscheduled critical tasks
        if not is_scheduled and task.category == "medication":
            base_confidence -= 0.2
        
        # Adjust based on time constraints
        if is_scheduled and task.preferred_time is not None:
            base_confidence += 0.1
        
        # Penalize if there are conflicts
        if scheduler.conflicts:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))

    def _find_alternatives(self, task: Task) -> List[str]:
        """Find alternative time slots for a task."""
        alternatives = []
        
        if task.preferred_time == TimeOfDay.MORNING:
            alternatives = ["afternoon", "evening", "anytime"]
        elif task.preferred_time == TimeOfDay.AFTERNOON:
            alternatives = ["morning", "evening", "anytime"]
        elif task.preferred_time == TimeOfDay.EVENING:
            alternatives = ["morning", "afternoon", "anytime"]
        else:
            alternatives = ["morning", "afternoon", "evening"]
        
        return alternatives

    def _generate_alternatives(
        self, scheduler: Scheduler, tasks: List[Task]
    ) -> List[Dict]:
        """Generate 2-3 alternative scheduling strategies."""
        alternatives = []
        
        # Alternative 1: Prioritize flexibility (move non-critical tasks)
        alt1 = {
            "name": "Flexible Schedule",
            "description": "Move non-critical tasks to later times, prioritize critical care",
            "strategy": "Defer enrichment tasks, keep feeding/meds in place",
            "estimated_success": 0.85,
        }
        alternatives.append(alt1)
        
        # Alternative 2: Time optimization
        alt2 = {
            "name": "Time-Optimized Schedule",
            "description": "Group similar tasks and optimize for owner's natural rhythm",
            "strategy": "Batch morning caregiving, spread afternoon/evening activities",
            "estimated_success": 0.80,
        }
        alternatives.append(alt2)
        
        # Alternative 3: Pet-focused
        alt3 = {
            "name": "Pet-Centric Schedule",
            "description": "Optimize for each pet's needs rather than time slots",
            "strategy": "Match high-energy pets to optimal times based on their profiles",
            "estimated_success": 0.78,
        }
        alternatives.append(alt3)
        
        return alternatives

    def record_feedback(self, task_id: str, feedback: str, success: bool):
        """Record user feedback for continuous improvement."""
        for decision in self.decisions:
            if decision.task_id == task_id:
                logger.info(
                    f"Feedback recorded for {task_id}: Success={success}, Notes={feedback}"
                )
                break


class AISchedulerIntegration:
    """Integration wrapper for the AI agent with the Scheduler."""

    def __init__(self, use_ollama: bool = True):
        """Initialize the integration."""
        self.agent = AISchedulingAgent(use_ollama=use_ollama)

    def schedule_with_ai(self, owner: Owner) -> Dict:
        """Generate a schedule with full AI reasoning and alternatives."""
        result = self.agent.generate_schedule_with_reasoning(owner)
        return result

    def get_decision_history(self) -> List[SchedulingDecision]:
        """Get all scheduling decisions made by the agent."""
        return self.agent.decisions

    def export_decisions(self, filepath: str = "ai_decisions.json"):
        """Export decision history to JSON for analysis."""
        decisions_data = [asdict(d) for d in self.agent.decisions]
        with open(filepath, "w") as f:
            json.dump(decisions_data, f, indent=2)
        logger.info(f"Exported {len(decisions_data)} decisions to {filepath}")
