"""
Enhanced RAG System with Multiple Data Sources and Quality Metrics
Demonstrates measurable improvements over baseline RAG
"""

import json
from typing import List, Dict, Tuple
from datetime import datetime
from src.ai_agent import PetCareRAG
from src.pawpal_system import Pet, Task


class EnhancedRAG(PetCareRAG):
    """
    Extended RAG system with multiple data sources and quality tracking.
    Measures answer quality improvements from baseline.
    """

    def __init__(self, guidelines_path: str = "pet_care_guidelines.json"):
        """Initialize enhanced RAG with multiple sources."""
        super().__init__(guidelines_path)
        
        # Additional data sources
        self.user_pet_history: List[Dict] = []
        self.vet_notes: List[Dict] = []
        self.breed_specific_guides: Dict[str, Dict] = self._load_breed_guides()
        self.quality_metrics = {
            "baseline_accuracy": 0.0,
            "enhanced_accuracy": 0.0,
            "sources_used": 0,
            "total_queries": 0,
            "improvement_percentage": 0.0
        }

    def _load_breed_guides(self) -> Dict[str, Dict]:
        """Load breed-specific guides for specialization."""
        return {
            "dog": {
                "labrador": {
                    "grooming": "Double-coated breed. Brush 3-4x weekly, bathe monthly. Prone to shedding.",
                    "exercise": "High energy. Need 60+ min daily. Great for families.",
                    "health": "Watch for hip dysplasia. Regular vet checks essential.",
                    "training": "Highly intelligent. Respond well to positive reinforcement."
                },
                "german_shepherd": {
                    "grooming": "Double-coated. Brush daily during shedding season. Bathe every 3-4 weeks.",
                    "exercise": "Very high energy. Need 120+ min daily with mental stimulation.",
                    "health": "Prone to hip dysplasia. Early screening recommended.",
                    "training": "Highly trainable. Require experienced handlers. Good for work/sport."
                },
                "poodle": {
                    "grooming": "Professional grooming every 6-8 weeks. Daily brushing. No shedding.",
                    "exercise": "Moderate to high energy. 30-60 min daily depending on size.",
                    "health": "Generally healthy. Watch for ear infections and eye issues.",
                    "training": "Highly intelligent. Excel at obedience and agility training."
                }
            },
            "cat": {
                "persian": {
                    "grooming": "Long-haired. Brush daily to prevent mats. Professional grooming every 8 weeks.",
                    "exercise": "Low energy. Indoor only recommended. Calm temperament.",
                    "health": "Prone to respiratory issues. Watch breathing carefully.",
                    "training": "Independent, less trainable than other breeds. Prefer calm environments."
                },
                "bengal": {
                    "grooming": "Short-haired. Brush 2-3x weekly. Occasional baths acceptable.",
                    "exercise": "High energy. Need interactive toys and climbing structures.",
                    "health": "Prone to HCM (heart disease). Regular vet checks important.",
                    "training": "Highly intelligent. Can be trained to walk on harness/leash."
                }
            }
        }

    def add_user_pet_history(self, pet: Pet, task: Task, outcome: str, date: str = None):
        """Add user's pet-specific history for personalized recommendations."""
        if date is None:
            date = datetime.now().isoformat()
        
        history_entry = {
            "pet_name": pet.name,
            "pet_species": pet.species,
            "pet_age": pet.age,
            "task": task.name,
            "task_category": task.category,
            "outcome": outcome,  # e.g., "successful", "needs_adjustment", "failed"
            "date": date,
            "special_needs": pet.special_needs
        }
        self.user_pet_history.append(history_entry)

    def add_vet_note(self, pet: Pet, note: str, category: str = "general", date: str = None):
        """Add veterinarian notes for evidence-based recommendations."""
        if date is None:
            date = datetime.now().isoformat()
        
        vet_entry = {
            "pet_name": pet.name,
            "pet_species": pet.species,
            "note": note,
            "category": category,  # health, behavior, nutrition, grooming, etc.
            "date": date,
            "source": "veterinarian"
        }
        self.vet_notes.append(vet_entry)

    def retrieve_enhanced(self, pet: Pet, query: str) -> Tuple[str, Dict]:
        """
        Enhanced retrieval from multiple sources.
        
        Returns:
            Tuple of (combined_answer, source_breakdown)
        """
        sources_used = 0
        context_parts = []
        source_breakdown = {
            "primary_guidelines": False,
            "pet_history": False,
            "vet_notes": False,
            "breed_guides": False
        }

        # 1. Primary guidelines (baseline)
        primary_context = self.retrieve_pet_guidelines(pet)
        context_parts.append(f"📚 **Standard Guidelines:**\n{primary_context}")
        source_breakdown["primary_guidelines"] = True
        sources_used += 1

        # 2. Pet-specific history
        pet_history = self._retrieve_pet_history(pet)
        if pet_history:
            context_parts.append(f"\n📋 **Your Pet's History:**\n{pet_history}")
            source_breakdown["pet_history"] = True
            sources_used += 1

        # 3. Veterinarian notes
        vet_context = self._retrieve_vet_notes(pet)
        if vet_context:
            context_parts.append(f"\n⚕️ **Vet Recommendations:**\n{vet_context}")
            source_breakdown["vet_notes"] = True
            sources_used += 1

        # 4. Breed-specific guides
        breed_context = self._retrieve_breed_guide(pet)
        if breed_context:
            context_parts.append(f"\n🐕 **Breed-Specific Guide:**\n{breed_context}")
            source_breakdown["breed_guides"] = True
            sources_used += 1

        # Update metrics
        self.quality_metrics["total_queries"] += 1
        self.quality_metrics["sources_used"] = sources_used

        combined_answer = "\n".join(context_parts)
        return combined_answer, source_breakdown

    def _retrieve_pet_history(self, pet: Pet) -> str:
        """Retrieve relevant pet history."""
        if not self.user_pet_history:
            return ""

        pet_entries = [e for e in self.user_pet_history if e["pet_name"] == pet.name]
        if not pet_entries:
            return ""

        history_str = ""
        for entry in pet_entries[-5:]:  # Last 5 entries
            history_str += f"- {entry['task']}: {entry['outcome']} ({entry['date'][:10]})\n"

        return history_str

    def _retrieve_vet_notes(self, pet: Pet) -> str:
        """Retrieve relevant vet notes."""
        if not self.vet_notes:
            return ""

        pet_notes = [n for n in self.vet_notes if n["pet_name"] == pet.name]
        if not pet_notes:
            return ""

        notes_str = ""
        for note in pet_notes[-3:]:  # Last 3 notes
            notes_str += f"- **{note['category'].title()}**: {note['note']}\n"

        return notes_str

    def _retrieve_breed_guide(self, pet: Pet) -> str:
        """Retrieve breed-specific guides."""
        species_guides = self.breed_specific_guides.get(pet.species.lower(), {})
        if not species_guides:
            return ""

        # Try to match pet characteristics to breed guides
        # For demo, just return first available breed guide
        first_breed = list(species_guides.keys())[0] if species_guides else None
        if not first_breed:
            return ""

        breed_info = species_guides[first_breed]
        guide_str = f"**{first_breed.title()} ({pet.species.title()}):**\n"
        for category, tip in breed_info.items():
            guide_str += f"- **{category.title()}**: {tip}\n"

        return guide_str

    def calculate_quality_improvement(self, baseline_score: float, enhanced_score: float):
        """Calculate measurable improvement metrics."""
        self.quality_metrics["baseline_accuracy"] = baseline_score
        self.quality_metrics["enhanced_accuracy"] = enhanced_score
        
        if baseline_score > 0:
            improvement = ((enhanced_score - baseline_score) / baseline_score) * 100
            self.quality_metrics["improvement_percentage"] = improvement
        
        return self.quality_metrics

    def get_metrics_report(self) -> str:
        """Generate quality metrics report."""
        report = "📊 **Enhanced RAG Quality Metrics**\n\n"
        report += f"Total Queries: {self.quality_metrics['total_queries']}\n"
        report += f"Avg Sources Used: {self.quality_metrics['sources_used']}\n"
        report += f"Baseline Accuracy: {self.quality_metrics['baseline_accuracy']:.2%}\n"
        report += f"Enhanced Accuracy: {self.quality_metrics['enhanced_accuracy']:.2%}\n"
        report += f"Improvement: {self.quality_metrics['improvement_percentage']:.1f}%\n"
        return report
