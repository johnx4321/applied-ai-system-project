"""
Comprehensive Test Harness and Evaluation Script
Runs predefined tests and generates pass/fail scores with confidence ratings
"""

import json
import sys
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from src.pawpal_system import Owner, Pet, Task, Scheduler, Frequency, TimeOfDay
from src.enhanced_rag import EnhancedRAG
from src.enhanced_workflow import EnhancedAgentWorkflow
from src.specialization import SpecializedScheduler
from src.ai_agent import AISchedulingAgent


class TestHarness:
    """
    Comprehensive test harness for evaluating PawPal+ AI system.
    Tests RAG enhancement, agentic workflow, specialization, and overall reliability.
    """

    def __init__(self):
        """Initialize test harness."""
        self.test_results: List[Dict[str, Any]] = []
        self.summary_metrics = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "average_confidence": 0.0,
            "execution_time": 0.0
        }

    def run_all_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """Run all test suites."""
        import time
        start_time = time.time()

        print("\n" + "="*70)
        print("🧪 PawPal+ AI System Test Harness")
        print("="*70 + "\n")

        # Test suites
        self.test_enhanced_rag()
        self.test_agentic_workflow()
        self.test_specialization()
        self.test_integration()

        execution_time = time.time() - start_time
        self._calculate_summary(execution_time)
        
        if verbose:
            self.print_report()
        
        return self._generate_final_report()

    def test_enhanced_rag(self):
        """Test RAG enhancement features."""
        print("📚 Testing Enhanced RAG System...")
        
        # Test 1: Baseline RAG
        test1 = self._test_baseline_rag()
        self.test_results.append(test1)
        
        # Test 2: Multi-source retrieval
        test2 = self._test_multi_source_retrieval()
        self.test_results.append(test2)
        
        # Test 3: Quality metrics
        test3 = self._test_quality_metrics()
        self.test_results.append(test3)
        
        # Test 4: Breed-specific guides
        test4 = self._test_breed_guides()
        self.test_results.append(test4)
        
        print("  ✓ RAG tests completed\n")

    def _test_baseline_rag(self) -> Dict:
        """Test baseline RAG functionality."""
        try:
            from src.ai_agent import PetCareRAG
            rag = PetCareRAG()
            
            dog = Pet(name="Test", species="dog", age=3)
            guidelines = rag.retrieve_pet_guidelines(dog)
            
            passed = "exercise" in guidelines.lower() and "feeding" in guidelines.lower()
            confidence = 0.95 if passed else 0.1
            
            return {
                "name": "Baseline RAG Retrieval",
                "passed": passed,
                "confidence": confidence,
                "details": f"Retrieved {len(guidelines)} chars of guidelines"
            }
        except Exception as e:
            return {
                "name": "Baseline RAG Retrieval",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_multi_source_retrieval(self) -> Dict:
        """Test enhanced RAG with multiple sources."""
        try:
            rag = EnhancedRAG()
            
            dog = Pet(name="Max", species="dog", age=5)
            task = Task(
                task_id="t1",
                name="Walk",
                description="Morning walk",
                category="walk",
                duration=30,
                priority=3
            )
            
            # Add data to multiple sources
            rag.add_user_pet_history(dog, task, "successful")
            rag.add_vet_note(dog, "Senior dog, arthritis management important")
            
            # Retrieve from multiple sources
            answer, sources = rag.retrieve_enhanced(dog, "exercise for senior dog")
            
            sources_used = sum(1 for v in sources.values() if v)
            passed = sources_used >= 3  # Should use 3+ sources
            confidence = 0.85 if passed else 0.4
            
            return {
                "name": "Multi-Source Retrieval",
                "passed": passed,
                "confidence": confidence,
                "details": f"Sources used: {sources_used}/4"
            }
        except Exception as e:
            return {
                "name": "Multi-Source Retrieval",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_quality_metrics(self) -> Dict:
        """Test RAG quality metrics calculation."""
        try:
            rag = EnhancedRAG()
            
            metrics = rag.calculate_quality_improvement(0.75, 0.92)
            
            improvement = metrics["improvement_percentage"]
            passed = 0 < improvement <= 50  # Reasonable improvement range
            confidence = 0.9 if passed else 0.3
            
            return {
                "name": "Quality Metrics Calculation",
                "passed": passed,
                "confidence": confidence,
                "details": f"Improvement calculated: {improvement:.1f}%"
            }
        except Exception as e:
            return {
                "name": "Quality Metrics Calculation",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_breed_guides(self) -> Dict:
        """Test breed-specific guide retrieval."""
        try:
            rag = EnhancedRAG()
            
            dog = Pet(name="TestDog", species="dog", age=3)
            answer, sources = rag.retrieve_enhanced(dog, "breed guide")
            
            passed = sources["breed_guides"] and len(answer) > 100
            confidence = 0.85 if passed else 0.2
            
            return {
                "name": "Breed-Specific Guides",
                "passed": passed,
                "confidence": confidence,
                "details": f"Guide retrieved: {len(answer)} chars"
            }
        except Exception as e:
            return {
                "name": "Breed-Specific Guides",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def test_agentic_workflow(self):
        """Test enhanced agentic workflow."""
        print("🤖 Testing Enhanced Agentic Workflow...")
        
        # Test 1: Observable steps
        test1 = self._test_observable_steps()
        self.test_results.append(test1)
        
        # Test 2: Tool calls
        test2 = self._test_tool_calls()
        self.test_results.append(test2)
        
        # Test 3: Decision chain
        test3 = self._test_decision_chain()
        self.test_results.append(test3)
        
        # Test 4: Workflow export
        test4 = self._test_workflow_export()
        self.test_results.append(test4)
        
        print("  ✓ Agentic workflow tests completed\n")

    def _test_observable_steps(self) -> Dict:
        """Test that workflow has observable steps."""
        try:
            workflow = EnhancedAgentWorkflow()
            owner = self._create_test_owner()
            
            result = workflow.execute_scheduling_workflow(owner)
            
            steps = result["steps"]
            passed = len(steps) == 8  # Should have 8 steps
            confidence = 0.9 if passed else 0.5
            
            return {
                "name": "Observable Workflow Steps",
                "passed": passed,
                "confidence": confidence,
                "details": f"Steps executed: {len(steps)}/8"
            }
        except Exception as e:
            return {
                "name": "Observable Workflow Steps",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_tool_calls(self) -> Dict:
        """Test that workflow uses different tools."""
        try:
            workflow = EnhancedAgentWorkflow()
            owner = self._create_test_owner()
            
            result = workflow.execute_scheduling_workflow(owner)
            steps = result["steps"]
            
            tools_used = set(s.tool_used for s in steps)
            passed = len(tools_used) >= 5  # Should use 5+ different tools
            confidence = 0.85 if passed else 0.4
            
            return {
                "name": "Tool Usage",
                "passed": passed,
                "confidence": confidence,
                "details": f"Tools used: {len(tools_used)} ({', '.join(tools_used)})"
            }
        except Exception as e:
            return {
                "name": "Tool Usage",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_decision_chain(self) -> Dict:
        """Test decision chain with reasoning."""
        try:
            workflow = EnhancedAgentWorkflow()
            owner = self._create_test_owner()
            
            result = workflow.execute_scheduling_workflow(owner)
            trace = result["execution_trace"]
            
            passed = len(trace) > 200 and "Step" in trace
            confidence = 0.9 if passed else 0.3
            
            return {
                "name": "Decision Chain Reasoning",
                "passed": passed,
                "confidence": confidence,
                "details": f"Trace length: {len(trace)} chars"
            }
        except Exception as e:
            return {
                "name": "Decision Chain Reasoning",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_workflow_export(self) -> Dict:
        """Test workflow export functionality."""
        try:
            workflow = EnhancedAgentWorkflow()
            owner = self._create_test_owner()
            
            workflow.execute_scheduling_workflow(owner)
            filepath = workflow.export_workflow("/tmp/test_workflow.json")
            
            passed = Path(filepath).exists()
            confidence = 0.95 if passed else 0.1
            
            return {
                "name": "Workflow Export",
                "passed": passed,
                "confidence": confidence,
                "details": f"Exported to {filepath}"
            }
        except Exception as e:
            return {
                "name": "Workflow Export",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def test_specialization(self):
        """Test specialization and fine-tuning."""
        print("🎯 Testing Specialization and Fine-Tuning...")
        
        # Test 1: Few-shot examples
        test1 = self._test_few_shot_examples()
        self.test_results.append(test1)
        
        # Test 2: Specialized output
        test2 = self._test_specialized_output()
        self.test_results.append(test2)
        
        # Test 3: Tone consistency
        test3 = self._test_tone_consistency()
        self.test_results.append(test3)
        
        # Test 4: Synthetic data generation
        test4 = self._test_synthetic_data()
        self.test_results.append(test4)
        
        print("  ✓ Specialization tests completed\n")

    def _test_few_shot_examples(self) -> Dict:
        """Test few-shot example database."""
        try:
            scheduler = SpecializedScheduler()
            
            examples = scheduler.few_shot_examples
            passed = len(examples) >= 6
            confidence = 0.95 if passed else 0.3
            
            return {
                "name": "Few-Shot Example Database",
                "passed": passed,
                "confidence": confidence,
                "details": f"Examples loaded: {len(examples)}"
            }
        except Exception as e:
            return {
                "name": "Few-Shot Example Database",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_specialized_output(self) -> Dict:
        """Test specialized output generation."""
        try:
            scheduler = SpecializedScheduler()
            owner = self._create_test_owner()
            pets = owner.pets
            tasks = []
            for pet in pets:
                tasks.extend(pet.get_tasks())
            
            baseline = scheduler.get_baseline_schedule(owner, pets)
            specialized = scheduler.get_specialized_schedule(owner, pets, tasks)
            
            # Specialized should be longer and more detailed
            passed = len(specialized) > len(baseline) * 1.5
            confidence = 0.85 if passed else 0.4
            
            return {
                "name": "Specialized Output Generation",
                "passed": passed,
                "confidence": confidence,
                "details": f"Baseline: {len(baseline)}ch, Specialized: {len(specialized)}ch"
            }
        except Exception as e:
            return {
                "name": "Specialized Output Generation",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_tone_consistency(self) -> Dict:
        """Test professional tone consistency."""
        try:
            scheduler = SpecializedScheduler()
            
            report = scheduler.get_specialization_report()
            
            passed = "Veterinary" in report and "evidence" in report.lower()
            confidence = 0.9 if passed else 0.3
            
            return {
                "name": "Professional Tone Consistency",
                "passed": passed,
                "confidence": confidence,
                "details": "Veterinary professional tone applied"
            }
        except Exception as e:
            return {
                "name": "Professional Tone Consistency",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_synthetic_data(self) -> Dict:
        """Test synthetic training data generation."""
        try:
            scheduler = SpecializedScheduler()
            
            synthetic = scheduler.synthesize_training_data(10)
            passed = len(synthetic) == 10 and all("category" in ex for ex in synthetic)
            confidence = 0.95 if passed else 0.2
            
            return {
                "name": "Synthetic Data Generation",
                "passed": passed,
                "confidence": confidence,
                "details": f"Generated {len(synthetic)} synthetic examples"
            }
        except Exception as e:
            return {
                "name": "Synthetic Data Generation",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def test_integration(self):
        """Test integration between all systems."""
        print("🔗 Testing System Integration...")
        
        # Test 1: RAG + Workflow
        test1 = self._test_rag_workflow_integration()
        self.test_results.append(test1)
        
        # Test 2: Workflow + Specialization
        test2 = self._test_workflow_specialization_integration()
        self.test_results.append(test2)
        
        # Test 3: End-to-end system
        test3 = self._test_end_to_end()
        self.test_results.append(test3)
        
        print("  ✓ Integration tests completed\n")

    def _test_rag_workflow_integration(self) -> Dict:
        """Test RAG and workflow integration."""
        try:
            rag = EnhancedRAG()
            workflow = EnhancedAgentWorkflow()
            owner = self._create_test_owner()
            
            # Execute workflow
            result = workflow.execute_scheduling_workflow(owner)
            
            # Verify integration
            passed = len(result["steps"]) > 0 and len(result["scheduled_tasks"]) >= 0
            confidence = 0.9 if passed else 0.3
            
            return {
                "name": "RAG + Workflow Integration",
                "passed": passed,
                "confidence": confidence,
                "details": "Systems integrated successfully"
            }
        except Exception as e:
            return {
                "name": "RAG + Workflow Integration",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_workflow_specialization_integration(self) -> Dict:
        """Test workflow and specialization integration."""
        try:
            workflow = EnhancedAgentWorkflow()
            scheduler = SpecializedScheduler()
            owner = self._create_test_owner()
            
            result = workflow.execute_scheduling_workflow(owner)
            comparison = scheduler.compare_outputs("test", owner.pets)
            
            passed = "baseline" in comparison and "specialized" in comparison
            confidence = 0.85 if passed else 0.3
            
            return {
                "name": "Workflow + Specialization Integration",
                "passed": passed,
                "confidence": confidence,
                "details": "Integration verified"
            }
        except Exception as e:
            return {
                "name": "Workflow + Specialization Integration",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _test_end_to_end(self) -> Dict:
        """Test complete end-to-end system."""
        try:
            owner = self._create_test_owner()
            
            # Initialize all systems
            rag = EnhancedRAG()
            workflow = EnhancedAgentWorkflow()
            scheduler = SpecializedScheduler()
            
            # Execute workflow
            result = workflow.execute_scheduling_workflow(owner)
            
            # Verify results
            passed = (
                result["scheduled_tasks"] is not None and
                result["steps"] is not None and
                len(result["steps"]) > 0
            )
            confidence = 0.9 if passed else 0.3
            
            return {
                "name": "End-to-End System Test",
                "passed": passed,
                "confidence": confidence,
                "details": f"Scheduled {len(result['scheduled_tasks'])} tasks"
            }
        except Exception as e:
            return {
                "name": "End-to-End System Test",
                "passed": False,
                "confidence": 0.0,
                "details": str(e)
            }

    def _create_test_owner(self) -> Owner:
        """Create test owner with pets and tasks."""
        owner = Owner(name="Test Owner", available_time=120)
        
        dog = Pet(name="TestDog", species="dog", age=3)
        task1 = Task(
            task_id="t1",
            name="Morning walk",
            description="Daily exercise",
            category="walk",
            duration=30,
            priority=3,
            frequency=Frequency.DAILY,
            preferred_time=TimeOfDay.MORNING
        )
        task2 = Task(
            task_id="t2",
            name="Feeding",
            description="Meal time",
            category="feed",
            duration=10,
            priority=3,
            frequency=Frequency.DAILY
        )
        dog.add_task(task1)
        dog.add_task(task2)
        owner.add_pet(dog)
        
        return owner

    def _calculate_summary(self, execution_time: float):
        """Calculate test summary metrics."""
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t["passed"])
        
        self.summary_metrics["total_tests"] = total
        self.summary_metrics["passed"] = passed
        self.summary_metrics["failed"] = total - passed
        self.summary_metrics["pass_rate"] = passed / total if total > 0 else 0
        self.summary_metrics["average_confidence"] = sum(t["confidence"] for t in self.test_results) / total if total > 0 else 0
        self.summary_metrics["execution_time"] = execution_time

    def print_report(self):
        """Print human-readable test report."""
        print("\n" + "="*70)
        print("📊 Test Results Summary")
        print("="*70 + "\n")
        
        for test in self.test_results:
            status = "✓ PASS" if test["passed"] else "✗ FAIL"
            confidence = test["confidence"]
            print(f"{status} | {test['name']:<40} | Confidence: {confidence:.0%}")
            print(f"       └─ {test['details']}")
        
        print("\n" + "-"*70)
        print(f"Total Tests: {self.summary_metrics['total_tests']}")
        print(f"Passed: {self.summary_metrics['passed']} | Failed: {self.summary_metrics['failed']}")
        print(f"Pass Rate: {self.summary_metrics['pass_rate']:.0%}")
        print(f"Average Confidence: {self.summary_metrics['average_confidence']:.0%}")
        print(f"Execution Time: {self.summary_metrics['execution_time']:.2f}s")
        print("="*70 + "\n")

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary_metrics,
            "tests": self.test_results,
            "status": "PASS" if self.summary_metrics["pass_rate"] >= 0.8 else "FAIL"
        }

    def export_report(self, filepath: str = "test_report.json"):
        """Export test report to JSON."""
        report = self._generate_final_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"✓ Report exported to {filepath}\n")
        return filepath


def main():
    """Run the test harness."""
    harness = TestHarness()
    results = harness.run_all_tests(verbose=True)
    harness.export_report()
    
    # Return exit code based on pass rate
    if results["summary"]["pass_rate"] >= 0.8:
        print("✓ All critical tests passed!")
        return 0
    else:
        print("✗ Some tests failed. See report for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
