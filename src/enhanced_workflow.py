"""
Enhanced Agentic Workflow with Observable Decision Chain
Demonstrates multi-step reasoning with tool-calls and planning steps
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from src.pawpal_system import Owner, Task


@dataclass
class AgentStep:
    """Represents a single step in agent's reasoning process."""
    step_number: int
    action: str  # e.g., "retrieve_context", "check_constraints", "rank_tasks"
    tool_used: str  # e.g., "RAG", "constraint_checker", "prioritizer"
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning: str
    confidence: float
    timestamp: str


class EnhancedAgentWorkflow:
    """
    Enhanced agentic workflow with observable intermediate steps.
    Implements multi-step reasoning with tool-calls and decision-making chain.
    """

    def __init__(self):
        """Initialize the enhanced agent."""
        self.steps: List[AgentStep] = []
        self.current_step = 0

    def _record_step(
        self,
        action: str,
        tool: str,
        input_data: Dict,
        output_data: Dict,
        reasoning: str,
        confidence: float = 0.5
    ):
        """Record an intermediate step."""
        step = AgentStep(
            step_number=self.current_step,
            action=action,
            tool_used=tool,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )
        self.steps.append(step)
        self.current_step += 1
        return step

    def execute_scheduling_workflow(self, owner: Owner) -> Dict[str, Any]:
        """
        Execute scheduling with observable steps and tool-calls.
        
        Returns:
            Dict with final decision and step trace
        """
        self.steps = []
        self.current_step = 0

        # ===== STEP 1: RETRIEVE CONTEXT =====
        step1_input = {
            "owner": owner.name,
            "pets": [p.name for p in owner.pets],
            "available_time": owner.available_time
        }
        step1_output = {
            "total_pets": len(owner.pets),
            "all_tasks": sum(len(p.get_tasks()) for p in owner.pets),
            "time_available_minutes": owner.available_time
        }
        self._record_step(
            action="retrieve_context",
            tool="context_retriever",
            input_data=step1_input,
            output_data=step1_output,
            reasoning="Retrieved owner profile and all pet/task data to establish baseline constraints.",
            confidence=0.95
        )

        # ===== STEP 2: CHECK CONSTRAINTS =====
        all_tasks = []
        for pet in owner.pets:
            all_tasks.extend(pet.get_tasks())
        
        pending_tasks = [t for t in all_tasks if not t.is_completed]
        total_duration = sum(t.duration for t in pending_tasks)

        step2_input = {
            "pending_tasks": len(pending_tasks),
            "total_duration": total_duration,
            "available_time": owner.available_time
        }
        step2_output = {
            "feasible": total_duration <= owner.available_time,
            "surplus_time": owner.available_time - total_duration,
            "time_pressure": "high" if total_duration > owner.available_time * 0.9 else "moderate"
        }
        self._record_step(
            action="check_constraints",
            tool="constraint_analyzer",
            input_data=step2_input,
            output_data=step2_output,
            reasoning=f"Analyzed time constraints: {total_duration}min needed vs {owner.available_time}min available.",
            confidence=1.0
        )

        # ===== STEP 3: PRIORITIZE TASKS =====
        critical_tasks = [t for t in pending_tasks if t.priority == 3]
        important_tasks = [t for t in pending_tasks if t.priority == 2]
        low_priority_tasks = [t for t in pending_tasks if t.priority == 1]

        step3_input = {
            "all_pending": len(pending_tasks),
            "prioritization_method": "multi_factor"
        }
        step3_output = {
            "critical_count": len(critical_tasks),
            "critical_duration": sum(t.duration for t in critical_tasks),
            "important_count": len(important_tasks),
            "low_priority_count": len(low_priority_tasks),
            "critical_fit": sum(t.duration for t in critical_tasks) <= owner.available_time
        }
        self._record_step(
            action="prioritize_tasks",
            tool="task_prioritizer",
            input_data=step3_input,
            output_data=step3_output,
            reasoning=f"Sorted tasks: {len(critical_tasks)} critical (health/safety), {len(important_tasks)} important, {len(low_priority_tasks)} optional.",
            confidence=0.9
        )

        # ===== STEP 4: SCHEDULE CRITICAL TASKS =====
        scheduled_time = 0
        scheduled_tasks = []
        
        for task in critical_tasks:
            if scheduled_time + task.duration <= owner.available_time:
                scheduled_tasks.append(task)
                scheduled_time += task.duration

        step4_input = {
            "critical_tasks_available": len(critical_tasks),
            "critical_duration": sum(t.duration for t in critical_tasks)
        }
        step4_output = {
            "critical_scheduled": len(scheduled_tasks),
            "critical_scheduled_time": scheduled_time,
            "critical_coverage": len(scheduled_tasks) / len(critical_tasks) if critical_tasks else 1.0
        }
        self._record_step(
            action="schedule_critical",
            tool="scheduler",
            input_data=step4_input,
            output_data=step4_output,
            reasoning=f"Scheduled all critical tasks: {len(scheduled_tasks)}/{len(critical_tasks)} fit in available time.",
            confidence=0.95
        )

        # ===== STEP 5: SCHEDULE IMPORTANT TASKS =====
        important_scheduled = []
        remaining_time = owner.available_time - scheduled_time

        for task in important_tasks:
            if task.duration <= remaining_time:
                important_scheduled.append(task)
                remaining_time -= task.duration
                scheduled_tasks.append(task)

        step5_input = {
            "important_tasks": len(important_tasks),
            "remaining_time": owner.available_time - scheduled_time
        }
        step5_output = {
            "important_scheduled": len(important_scheduled),
            "important_time": sum(t.duration for t in important_scheduled),
            "remaining_after": remaining_time
        }
        self._record_step(
            action="schedule_important",
            tool="scheduler",
            input_data=step5_input,
            output_data=step5_output,
            reasoning=f"Scheduled {len(important_scheduled)} important tasks using remaining time.",
            confidence=0.85
        )

        # ===== STEP 6: DETECT CONFLICTS =====
        conflicts = []
        time_preferences = {}
        
        for task in scheduled_tasks:
            if task.preferred_time:
                if task.preferred_time.value not in time_preferences:
                    time_preferences[task.preferred_time.value] = []
                time_preferences[task.preferred_time.value].append(task)

        for time_slot, tasks in time_preferences.items():
            if len(tasks) > 1:
                total = sum(t.duration for t in tasks)
                if total > 60:  # Assume 60min per time slot
                    conflicts.append(f"{time_slot}: {len(tasks)} tasks ({total}min) - may conflict")

        step6_input = {
            "scheduled_tasks": len(scheduled_tasks),
            "time_slots_analyzed": len(time_preferences)
        }
        step6_output = {
            "conflicts_detected": len(conflicts),
            "conflict_details": conflicts
        }
        self._record_step(
            action="detect_conflicts",
            tool="conflict_detector",
            input_data=step6_input,
            output_data=step6_output,
            reasoning=f"Analyzed time preferences: detected {len(conflicts)} potential conflicts.",
            confidence=0.75
        )

        # ===== STEP 7: GENERATE ALTERNATIVES =====
        alternatives = []
        
        # Alternative 1: Aggressive (fit as much as possible)
        alt1_scheduled = critical_tasks.copy()
        alt1_time = sum(t.duration for t in alt1_scheduled)
        alt1_scheduled.extend([t for t in important_tasks if alt1_time + t.duration <= owner.available_time])
        
        # Alternative 2: Conservative (only critical + most urgent)
        alt2_scheduled = critical_tasks.copy()
        
        # Alternative 3: Balanced (original plan)
        alt3_scheduled = scheduled_tasks

        step7_input = {
            "critical_tasks": len(critical_tasks),
            "total_tasks": len(pending_tasks)
        }
        step7_output = {
            "alternatives_generated": 3,
            "aggressive_tasks": len(alt1_scheduled),
            "conservative_tasks": len(alt2_scheduled),
            "balanced_tasks": len(alt3_scheduled)
        }
        self._record_step(
            action="generate_alternatives",
            tool="alternative_generator",
            input_data=step7_input,
            output_data=step7_output,
            reasoning="Generated 3 alternative scheduling strategies with different risk/benefit profiles.",
            confidence=0.8
        )

        # ===== STEP 8: FINAL DECISION =====
        unscheduled = [t for t in pending_tasks if t not in scheduled_tasks]

        step8_input = {
            "candidate_schedule_size": len(scheduled_tasks),
            "unscheduled_count": len(unscheduled)
        }
        step8_output = {
            "final_scheduled": len(scheduled_tasks),
            "final_unscheduled": len(unscheduled),
            "time_utilization": (sum(t.duration for t in scheduled_tasks) / owner.available_time) * 100
        }
        self._record_step(
            action="finalize_schedule",
            tool="decision_maker",
            input_data=step8_input,
            output_data=step8_output,
            reasoning=f"Final decision: Schedule {len(scheduled_tasks)} tasks ({(sum(t.duration for t in scheduled_tasks) / owner.available_time) * 100:.0f}% time utilization).",
            confidence=0.88
        )

        return {
            "scheduled_tasks": scheduled_tasks,
            "unscheduled_tasks": unscheduled,
            "conflicts": conflicts,
            "steps": self.steps,
            "execution_trace": self._generate_trace(),
            "metrics": self._calculate_metrics(scheduled_tasks, unscheduled, pending_tasks)
        }

    def _generate_trace(self) -> str:
        """Generate human-readable execution trace."""
        trace = "🔍 **Agent Reasoning Trace**\n\n"
        for step in self.steps:
            trace += f"**Step {step.step_number + 1}: {step.action.replace('_', ' ').title()}**\n"
            trace += f"Tool: `{step.tool_used}`\n"
            trace += f"Reasoning: {step.reasoning}\n"
            trace += f"Confidence: {step.confidence:.0%}\n\n"
        return trace

    def _calculate_metrics(self, scheduled: List, unscheduled: List, all_pending: List) -> Dict:
        """Calculate workflow metrics."""
        return {
            "tasks_scheduled": len(scheduled),
            "tasks_unscheduled": len(unscheduled),
            "scheduling_success_rate": len(scheduled) / len(all_pending) if all_pending else 0,
            "steps_executed": self.current_step,
            "average_confidence": sum(s.confidence for s in self.steps) / len(self.steps) if self.steps else 0
        }

    def get_step_details(self, step_num: int) -> AgentStep:
        """Get detailed information about a specific step."""
        if step_num < len(self.steps):
            return self.steps[step_num]
        return None

    def export_workflow(self, filepath: str = "workflow_trace.json"):
        """Export workflow execution trace."""
        export_data = {
            "workflow_executed": datetime.now().isoformat(),
            "total_steps": len(self.steps),
            "steps": [asdict(s) for s in self.steps]
        }
        with open(filepath, "w") as f:
            import json
            json.dump(export_data, f, indent=2, default=str)
        return filepath
