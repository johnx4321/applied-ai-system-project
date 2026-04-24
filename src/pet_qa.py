"""
Pet Care Q&A System using RAG
Answers pet care questions based on the knowledge base
"""

import json
from typing import List, Dict, Tuple
from src.ai_agent import PetCareRAG
from src.pawpal_system import Pet


class PetQASystem:
    """
    RAG-based Q&A system for answering pet care questions.
    Retrieves relevant knowledge from pet care guidelines and provides answers.
    """

    def __init__(self, guidelines_path: str = "pet_care_guidelines.json"):
        """Initialize the Q&A system with pet care guidelines."""
        self.rag = PetCareRAG(guidelines_path)
        self.conversation_history: List[Dict] = []
        self.faq_database = self._build_faq_database()

    def _build_faq_database(self) -> Dict[str, List[Dict]]:
        """Build a database of common questions and their answers."""
        guidelines = self.rag.guidelines
        
        faq = {
            "grooming": [
                {
                    "questions": ["how often should i groom my dog", "dog grooming frequency", "how often to brush dog"],
                    "answer": "Dogs should be brushed 3-4 times weekly. Professional grooming every 6-8 weeks, nail trim every 4-6 weeks, ear cleaning weekly, and teeth brushing daily if possible."
                },
                {
                    "questions": ["how often should i groom my cat", "cat grooming frequency", "how often to brush cat"],
                    "answer": "Long-haired cats need daily brushing. Short-haired cats need brushing 2-3 times weekly. Nail trim every 2-3 weeks, ear checks weekly, and dental care as recommended by vet."
                },
                {
                    "questions": ["rabbit grooming", "how to groom rabbit", "rabbit nail trim"],
                    "answer": "Rabbits need regular brushing to prevent mats and manage shedding. Nail trimming should be done monthly or when nails get too long. Check fur daily for mats and parasites."
                },
                {
                    "questions": ["nail trim dog", "dog nail trimming", "how to trim dog nails"],
                    "answer": "Dog nails should be trimmed every 4-6 weeks or when they click on the floor. You can do it at home with proper clippers or visit a professional groomer."
                },
                {
                    "questions": ["cat shedding", "manage cat hair", "reduce cat shedding"],
                    "answer": "Regular brushing 2-3 times weekly for short-haired cats and daily for long-haired cats helps reduce shedding. Use a slicker brush or deshedding tool for best results."
                }
            ],
            "feeding": [
                {
                    "questions": ["how often should i feed my dog", "dog feeding frequency", "how many meals per dog"],
                    "answer": "Adult dogs should eat 1-2 meals per day. Puppies (under 6 months) need 3-4 meals daily. Senior dogs (over 7 years) do well with 2 meals per day. Always feed at the same times daily."
                },
                {
                    "questions": ["how often should i feed my cat", "cat feeding frequency", "how many meals per cat"],
                    "answer": "Adult cats eat 1-2 meals per day. Kittens (under 1 year) need 3-4 meals daily. Senior cats (over 10 years) should eat 2-3 small meals daily. Feed at consistent times."
                },
                {
                    "questions": ["rabbit feeding", "what to feed rabbit", "rabbit diet"],
                    "answer": "Rabbits need unlimited timothy hay as the main diet, limited pellets (about 1/4 cup per 5 lbs body weight), and fresh vegetables daily. Provide fresh water constantly through a water bottle or bowl."
                },
                {
                    "questions": ["puppy nutrition", "puppy feeding guide", "how much to feed puppy"],
                    "answer": "Puppies need high-protein food designed for puppies. Feed 3-4 times daily based on age. Use puppy-specific formulas for proper growth. Gradually transition to adult food after 1 year."
                }
            ],
            "exercise": [
                {
                    "questions": ["how much exercise does dog need", "dog exercise requirements", "how long to walk dog"],
                    "answer": "Small breeds (under 10 lbs) need 30 minutes daily. Medium breeds (10-25 lbs) need 60 minutes daily. Large breeds (over 25 lbs) need 60-90 minutes daily. Puppies need 5 minutes per month of age, twice daily."
                },
                {
                    "questions": ["senior dog exercise", "old dog exercise", "how much exercise senior dog"],
                    "answer": "Senior dogs (over 7 years) need 20-30 minutes daily with low-impact activities. Avoid excessive jumping or running. Regular gentle exercise helps maintain muscle and joint health."
                },
                {
                    "questions": ["cat exercise", "how to exercise cat", "mental stimulation for cats"],
                    "answer": "Indoor cats need 15-20 minutes of interactive play daily. Use feather wands, laser pointers, or ball toys. Provide climbing structures and window perches for natural stimulation."
                },
                {
                    "questions": ["rabbit exercise", "rabbit outdoor time", "how to exercise rabbit"],
                    "answer": "Rabbits need 30+ minutes of supervised outdoor or indoor play daily. Provide a safe pen for grazing, allow burrowing in bedding, and ensure they have space to run and jump."
                }
            ],
            "training": [
                {
                    "questions": ["dog training frequency", "training sessions per day", "how long training sessions"],
                    "answer": "Training sessions should be 10-15 minutes, 2-3 times daily. Consistency is key for behavior management. Use positive reinforcement with treats and praise."
                },
                {
                    "questions": ["puppy training tips", "start training puppy", "when to start training puppy"],
                    "answer": "Start training puppies as early as 8 weeks old. Keep sessions short (5-10 minutes) and frequent. Focus on basics like sit, stay, and come. Be patient and use only positive reinforcement."
                },
                {
                    "questions": ["behavioral issues dog", "fix bad dog behavior", "dog behavior training"],
                    "answer": "Address behavioral issues early with consistent training. Use positive reinforcement, not punishment. Consider professional help if issues persist. Understand the root cause (anxiety, energy, etc.)."
                }
            ],
            "health": [
                {
                    "questions": ["cat dental care", "cat teeth care", "how to clean cat teeth"],
                    "answer": "Brush cat teeth daily if possible. Provide dental treats and toys designed for oral health. Regular veterinary check-ups help catch dental issues early."
                },
                {
                    "questions": ["dog ear care", "ear infection dog", "how to clean dog ears"],
                    "answer": "Clean ears weekly to prevent infections. Use a vet-approved ear cleaner and cotton balls. Check for redness, odor, or discharge. Floppy-eared breeds are more prone to infections."
                },
                {
                    "questions": ["medication pet", "giving pet medicine", "pill dog"],
                    "answer": "Medications should be given on a consistent schedule. For pills, you can hide them in food, use pill pockets, or open and sprinkle in wet food (if approved by vet). Always follow vet instructions."
                },
                {
                    "questions": ["senior pet health", "old pet care", "senior dog health"],
                    "answer": "Senior pets need regular vet check-ups (every 6 months). Adjust exercise to be gentler, maintain healthy weight, and watch for signs of pain or behavioral changes."
                }
            ],
            "enrichment": [
                {
                    "questions": ["mental stimulation dog", "enrichment activities dog", "bored dog"],
                    "answer": "Provide puzzle toys, training sessions, interactive games, and varied walking routes. Mental stimulation is as important as physical exercise, especially for intelligent breeds."
                },
                {
                    "questions": ["cat enrichment", "indoor cat activities", "prevent cat boredom"],
                    "answer": "Provide window perches, climbing structures, hiding boxes, and interactive toys. Rotate toys regularly. Use treat puzzles and play fishing rod games daily to stimulate their hunting instincts."
                },
                {
                    "questions": ["rabbit enrichment", "rabbit toys", "keep rabbit entertained"],
                    "answer": "Provide dig boxes with bedding, chew toys, hay tunnels, and safe hiding spaces. Rotate toys weekly. Allow supervised outdoor time for natural behaviors like grazing and burrowing."
                }
            ]
        }
        
        return faq

    def answer_question(self, question: str, pet: Pet = None) -> Tuple[str, str]:
        """
        Answer a pet care question using RAG.
        
        Args:
            question: User's question about pet care
            pet: Optional Pet object to provide species-specific context
        
        Returns:
            Tuple of (answer, confidence_level)
        """
        question_lower = question.lower()
        
        # Step 1: Check FAQ database for exact match
        faq_answer = self._search_faq(question_lower)
        if faq_answer:
            self.conversation_history.append({
                "question": question,
                "answer": faq_answer,
                "source": "FAQ Database",
                "confidence": "high"
            })
            return faq_answer, "high"
        
        # Step 2: Use RAG to find relevant guidelines
        rag_context = self._build_rag_context(question_lower, pet)
        
        if not rag_context:
            answer = "I'm not sure about that specific question. Please consult with a veterinarian for accurate guidance."
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "source": "Default Response",
                "confidence": "low"
            })
            return answer, "low"
        
        # Step 3: Generate answer from RAG context
        answer = self._generate_answer(question_lower, rag_context, pet)
        
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "source": "RAG System",
            "confidence": "medium"
        })
        
        return answer, "medium"

    def _search_faq(self, question: str) -> str:
        """Search FAQ database for matching questions."""
        question_words = set(question.lower().split())
        
        for category, items in self.faq_database.items():
            for item in items:
                for faq_q in item["questions"]:
                    faq_words = set(faq_q.lower().split())
                    # Check for word overlap (at least 2 words matching)
                    overlap = len(question_words & faq_words)
                    if overlap >= 2:
                        return item["answer"]
        
        return ""

    def _build_rag_context(self, question: str, pet: Pet = None) -> str:
        """Build RAG context based on question and pet."""
        context = ""
        
        # Determine what type of question this is
        question_keywords = {
            "grooming": ["groom", "brush", "nail", "coat", "hair", "bathe", "trim"],
            "feeding": ["feed", "meal", "food", "eat", "diet", "nutrition", "appetite"],
            "exercise": ["walk", "run", "exercise", "activity", "energy", "play"],
            "training": ["train", "behavior", "obedience", "command", "trick"],
            "medication": ["medicine", "medication", "sick", "health", "vaccine"],
            "enrichment": ["entertain", "bored", "toy", "activity", "stimulation"]
        }
        
        # Identify question type
        question_type = None
        for qtype, keywords in question_keywords.items():
            if any(kw in question for kw in keywords):
                question_type = qtype
                break
        
        # Retrieve relevant guidelines
        if pet:
            pet_guidance = self.rag.retrieve_pet_guidelines(pet)
            context += f"**Species-specific guidance for {pet.name} ({pet.species}):**\n{pet_guidance}\n\n"
        
        if question_type:
            context += f"**General {question_type} guidance:**\n"
            context += self.rag.retrieve_time_slot_guidance() + "\n"
        
        return context

    def _generate_answer(self, question: str, rag_context: str, pet: Pet = None) -> str:
        """Generate an answer from RAG context."""
        # Simple heuristic-based answer generation
        answers = {
            "groom": f"Based on pet care guidelines:\n{rag_context}\nRegular grooming is essential for your pet's health and comfort. Frequency depends on breed, coat type, and individual needs. If you have specific concerns, consult with a professional groomer or veterinarian.",
            "feed": f"Feeding guidelines:\n{rag_context}\nConsistent feeding times and appropriate portion sizes are crucial for your pet's health.",
            "walk": f"Exercise recommendations:\n{rag_context}\nRegular exercise keeps your pet physically and mentally healthy.",
            "train": f"Training tips:\n{rag_context}\nConsistency and positive reinforcement are key to successful training.",
            "health": f"Health considerations:\n{rag_context}\nFor any health concerns, please consult with your veterinarian.",
        }
        
        # Find the best matching answer
        for keyword, answer_template in answers.items():
            if keyword in question:
                return answer_template
        
        # Default answer
        return f"Based on the pet care guidelines:\n{rag_context}\nFor more specific guidance, consider consulting with a veterinary professional."

    def get_conversation_history(self) -> List[Dict]:
        """Return the conversation history."""
        return self.conversation_history

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_pet_specific_tips(self, pet: Pet) -> str:
        """Get tips specific to a pet's species and age."""
        guidelines = self.rag.retrieve_pet_guidelines(pet)
        tips = f"**Care tips for {pet.name} ({pet.species.title()}, age {pet.age}):**\n\n{guidelines}"
        
        if pet.special_needs:
            tips += f"\n\n⚠️ **Special Considerations:**\n"
            for need in pet.special_needs:
                tips += f"- {need.title()}\n"
        
        return tips

    def search_guidelines(self, query: str) -> str:
        """Search the knowledge base for a specific query."""
        query_lower = query.lower()
        guidelines = self.rag.guidelines
        
        results = []
        
        # Search pet guidelines
        for species, categories in guidelines.get("pet_guidelines", {}).items():
            for category, details in categories.items():
                if query_lower in category.lower() or query_lower in details.get("description", "").lower():
                    results.append(f"**{species.title()} - {category.title()}**: {details.get('description', '')}")
        
        # Search task categories
        for category, details in guidelines.get("task_category_defaults", {}).items():
            if query_lower in category.lower():
                results.append(f"**Task Category - {category.title()}**: {details.get('typical_duration')} min typical, Frequency: {details.get('frequency_recommendation')}")
        
        if results:
            return "\n\n".join(results)
        else:
            return f"No results found for '{query}'. Try searching for pet species, task categories (walk, feed, grooming, medication, enrichment), or specific health topics."
