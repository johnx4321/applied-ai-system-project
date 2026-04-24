"""
Logging and Audit System for AI Scheduling Decisions
Tracks all decisions, confidence scores, and outcomes for reliability analysis
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class AIDecisionLogger:
    """Logs and audits all AI scheduling decisions for reliability and transparency."""

    def __init__(self, log_dir: str = "logs"):
        """Initialize the decision logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up main logger
        self.logger = logging.getLogger("pawpal_ai")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for detailed logs
        log_file = self.log_dir / f"ai_decisions_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for stdout
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        self.decision_journal: List[Dict] = []

    def log_scheduling_decision(
        self,
        task_id: str,
        task_name: str,
        scheduled: bool,
        confidence: float,
        reasoning: str,
        model_used: str,
    ):
        """Log a scheduling decision."""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "task_name": task_name,
            "scheduled": scheduled,
            "confidence": confidence,
            "reasoning": reasoning,
            "model_used": model_used,
        }
        self.decision_journal.append(decision)
        
        status = "✓ SCHEDULED" if scheduled else "✗ UNSCHEDULED"
        self.logger.info(
            f"{status}: {task_name} (ID: {task_id}) | "
            f"Confidence: {confidence:.2f} | Model: {model_used}"
        )

    def log_conflict_detection(self, conflicts: List[str]):
        """Log detected scheduling conflicts."""
        if conflicts:
            self.logger.warning(f"Scheduling conflicts detected: {len(conflicts)}")
            for conflict in conflicts:
                self.logger.warning(f"  - {conflict}")

    def log_plan_generation(self, owner_name: str, num_tasks: int, available_time: int):
        """Log the start of a plan generation."""
        self.logger.info(
            f"Generating plan for {owner_name}: "
            f"{num_tasks} tasks, {available_time} min available"
        )

    def log_plan_summary(
        self,
        scheduled_count: int,
        unscheduled_count: int,
        avg_confidence: float,
        total_time: float,
    ):
        """Log summary of a completed plan."""
        self.logger.info(
            f"Plan summary: {scheduled_count} scheduled, {unscheduled_count} unscheduled, "
            f"Avg confidence: {avg_confidence:.2f}, Time: {total_time:.2f}s"
        )

    def log_error(self, error_type: str, message: str, recovery_action: str = ""):
        """Log an error with context and recovery action."""
        self.logger.error(f"[{error_type}] {message}")
        if recovery_action:
            self.logger.info(f"Recovery action: {recovery_action}")

    def log_user_feedback(self, task_id: str, feedback: str, success: bool):
        """Log user feedback on a scheduling decision."""
        self.logger.info(
            f"User feedback for {task_id}: Success={success}, "
            f"Feedback='{feedback}'"
        )

    def export_journal(self, filepath: str = "decision_journal.json"):
        """Export decision journal to JSON file."""
        journal_file = self.log_dir / filepath
        with open(journal_file, "w") as f:
            json.dump(self.decision_journal, f, indent=2)
        self.logger.info(f"Exported decision journal ({len(self.decision_journal)} entries) to {journal_file}")
        return str(journal_file)

    def get_reliability_stats(self) -> Dict:
        """Calculate reliability statistics from decision history."""
        if not self.decision_journal:
            return {"total_decisions": 0, "average_confidence": 0, "success_rate": 0}
        
        total = len(self.decision_journal)
        scheduled = sum(1 for d in self.decision_journal if d["scheduled"])
        avg_confidence = sum(d["confidence"] for d in self.decision_journal) / total
        
        return {
            "total_decisions": total,
            "scheduled_count": scheduled,
            "unscheduled_count": total - scheduled,
            "average_confidence": avg_confidence,
            "scheduling_rate": scheduled / total if total > 0 else 0,
        }

    def generate_reliability_report(self) -> str:
        """Generate a human-readable reliability report."""
        stats = self.get_reliability_stats()
        
        report = "\n" + "="*60 + "\n"
        report += "AI SCHEDULING RELIABILITY REPORT\n"
        report += "="*60 + "\n"
        report += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "STATISTICS:\n"
        report += f"  Total decisions: {stats['total_decisions']}\n"
        report += f"  Tasks scheduled: {stats['scheduled_count']}\n"
        report += f"  Tasks unscheduled: {stats['unscheduled_count']}\n"
        report += f"  Scheduling rate: {stats['scheduling_rate']:.1%}\n"
        report += f"  Average confidence: {stats['average_confidence']:.2f}/1.0\n\n"
        
        report += "DECISION BREAKDOWN:\n"
        high_conf = sum(1 for d in self.decision_journal if d["confidence"] >= 0.8)
        med_conf = sum(1 for d in self.decision_journal if 0.5 <= d["confidence"] < 0.8)
        low_conf = sum(1 for d in self.decision_journal if d["confidence"] < 0.5)
        
        report += f"  High confidence (≥0.8): {high_conf} ({high_conf/max(len(self.decision_journal), 1):.1%})\n"
        report += f"  Medium confidence (0.5-0.8): {med_conf} ({med_conf/max(len(self.decision_journal), 1):.1%})\n"
        report += f"  Low confidence (<0.5): {low_conf} ({low_conf/max(len(self.decision_journal), 1):.1%})\n"
        report += "="*60 + "\n"
        
        return report


def setup_logging(level=logging.INFO):
    """Set up global logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
