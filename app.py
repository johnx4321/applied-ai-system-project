import streamlit as st
from src.pawpal_system import Owner, Pet, Task, Scheduler, TimeOfDay, Frequency
from src.ai_agent import AISchedulerIntegration
from src.ai_logging import AIDecisionLogger
from src.pet_qa import PetQASystem
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="PawPal+ AI", page_icon="🐾", layout="wide")

# Initialize AI components in session state
if 'ai_integration' not in st.session_state:
    st.session_state.ai_integration = AISchedulerIntegration(use_ollama=False)

if 'ai_logger' not in st.session_state:
    st.session_state.ai_logger = AIDecisionLogger()

if 'pet_qa' not in st.session_state:
    st.session_state.pet_qa = PetQASystem()

# Initialize owner and pets in session state
if 'owner' not in st.session_state:
    loaded_owner = Owner.load_from_json("data.json")
    if loaded_owner:
        st.session_state.owner = loaded_owner
    else:
        st.session_state.owner = Owner(name="Jordan", available_time=120)
        buddy = Pet(name="Mochi", species="cat", age=3)
        st.session_state.owner.add_pet(buddy)

st.title("🐾 PawPal+ AI Pet Care Scheduler")
st.markdown("*Intelligent scheduling powered by AI and pet care knowledge*")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Manage Tasks", "AI Schedule", "Pet Q&A", "Insights", "Settings"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    owner = st.session_state.owner
    with col1:
        st.metric("Owner", owner.name)
    with col2:
        st.metric("Available Time", f"{owner.available_time} min")
    with col3:
        st.metric("Pets", len(owner.pets))
    with col4:
        total_tasks = sum(len(p.get_tasks()) for p in owner.pets)
        st.metric("Total Tasks", total_tasks)
    
    st.divider()
    st.subheader("📋 Pet & Task Overview")
    for pet in owner.pets:
        with st.expander(f"🐱 {pet.name} ({pet.species}, age {pet.age})"):
            if pet.special_needs:
                st.warning(f"⚠️ Special needs: {', '.join(pet.special_needs)}")
            tasks = pet.get_tasks()
            if tasks:
                for task in tasks:
                    status = "✓" if task.is_completed else "⊙"
                    st.write(f"{status} **{task.name}** ({task.duration}min, priority {task.priority}) - {task.category}")
                    if task.description:
                        st.caption(task.description)
            else:
                st.info("No tasks for this pet yet.")

with tab2:
    st.subheader("➕ Add a New Task")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Task Details**")
        task_title = st.text_input("Task title", value="Morning walk", key="task_title")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
        priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: {1: "⭐ Low", 2: "⭐⭐ Medium", 3: "⭐⭐⭐ High"}[x], index=2)
    with col2:
        st.write("**Category & Timing**")
        category = st.selectbox("Category", ["walk", "feed", "medication", "grooming", "enrichment"], format_func=lambda x: {"walk": "🚶 Walk", "feed": "🍽️ Feed", "medication": "💊 Medication", "grooming": "🛁 Grooming", "enrichment": "🎾 Enrichment"}[x])
        preferred_time = st.selectbox("Preferred time", [None, "morning", "afternoon", "evening"], format_func=lambda x: x if x else "⏰ Anytime")
    
    task_desc = st.text_area("Description (optional)", value="Daily exercise and bonding", height=50)
    select_pet = st.selectbox("Select pet", [p.name for p in owner.pets])
    
    if st.button("➕ Add Task", use_container_width=True):
        pet = next(p for p in owner.pets if p.name == select_pet)
        task_id = f"task_{len(pet.get_tasks()) + 1}"
        new_task = Task(task_id=task_id, name=task_title, description=task_desc, category=category, duration=int(duration), priority=priority, frequency=Frequency.DAILY, preferred_time=TimeOfDay[preferred_time.upper()] if preferred_time else None)
        pet.add_task(new_task)
        owner.save_to_json("data.json")
        st.success(f"✓ Added '{task_title}' to {pet.name}")
        st.rerun()
    
    st.divider()
    st.subheader("📝 Manage Current Tasks")
    for pet in owner.pets:
        tasks = pet.get_tasks()
        if tasks:
            st.write(f"**{pet.name}** ({len(tasks)} tasks)")
            for task in tasks:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    status = "✓" if task.is_completed else "⊙"
                    st.write(f"{status} {task.name} ({task.duration}min)")
                with col2:
                    if st.button("Mark done", key=f"done_{task.task_id}", use_container_width=True):
                        pet.complete_and_reschedule(task.task_id)
                        owner.save_to_json("data.json")
                        st.rerun()
                with col3:
                    if st.button("Remove", key=f"remove_{task.task_id}", use_container_width=True):
                        pet.remove_task(task.task_id)
                        owner.save_to_json("data.json")
                        st.rerun()

with tab3:
    st.subheader("🤖 AI-Powered Smart Scheduling")
    st.caption("Uses AI reasoning with pet care guidelines for intelligent task prioritization")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        use_ollama = st.checkbox("Use Ollama", value=False, help="Requires local Ollama instance running")
    with col3:
        if st.button("📋 Check Ollama Status", help="Diagnose Ollama connection issues"):
            st.info("Run this in terminal to check Ollama setup:\n```\npython diagnose_ollama.py\n```")
    
    if st.button("🚀 Generate AI Schedule", use_container_width=True):
        status_placeholder = st.empty()
        
        try:
            if use_ollama:
                status_placeholder.info("⏳ Connecting to Ollama... (first query can take 30-60s)")
            else:
                status_placeholder.info("⚡ Using Mock AI (instant results)")
            
            with st.spinner("🤖 Analyzing tasks and generating optimal schedule..."):
                ai_integration = AISchedulerIntegration(use_ollama=use_ollama)
                result = ai_integration.schedule_with_ai(owner)
                st.session_state.last_ai_result = result
                for decision in result["decisions"]:
                    st.session_state.ai_logger.log_scheduling_decision(
                        task_id=decision.task_id, 
                        task_name=decision.task_name, 
                        scheduled=decision.scheduled, 
                        confidence=decision.confidence_score, 
                        reasoning=decision.reasoning, 
                        model_used=decision.model_used
                    )
                status_placeholder.success("✅ Schedule generated successfully!")
                
        except Exception as e:
            status_placeholder.error(
                f"❌ Error generating schedule:\n\n{str(e)}\n\n"
                "**Troubleshooting:**\n"
                "• If using Ollama: Run `python diagnose_ollama.py` to check setup\n"
                "• Switch to Mock Mode (uncheck 'Use Ollama') for instant results\n"
                "• Ensure Ollama server is running: `ollama serve`"
            )
            logger.error(f"Schedule generation failed: {e}")
    
    if "last_ai_result" in st.session_state:
        result = st.session_state.last_ai_result
        st.divider()
        with st.expander("🧠 AI Reasoning", expanded=True):
            st.markdown(result.get("ai_reasoning", "No reasoning available"))
        
        confidence = result.get("confidence_score", 0.5)
        confidence_pct = int(confidence * 100)
        st.metric("Overall Confidence", f"{confidence_pct}%", delta=f"{confidence:.2f}/1.0")
        st.divider()
        
        st.subheader(f"✅ Scheduled Tasks ({len(result['scheduled_tasks'])})")
        scheduled_time = sum(t.duration for t in result["scheduled_tasks"])
        st.write(f"Total time: {scheduled_time} / {owner.available_time} min")
        if result["scheduled_tasks"]:
            for task in result["scheduled_tasks"]:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{task.name}**")
                        st.caption(task.description)
                    with col2:
                        st.write(f"{task.duration} min")
                        st.write(f"Priority: {task.priority}")
                    with col3:
                        if task.preferred_time:
                            st.write(f"⏰ {task.preferred_time.value}")
                        st.write(f"({task.category})")
        else:
            st.info("No tasks scheduled (check available time)")
        
        if result["unscheduled_tasks"]:
            st.subheader(f"⏳ Could Not Fit ({len(result['unscheduled_tasks'])})")
            for task in result["unscheduled_tasks"]:
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{task.name}**")
                        st.caption(f"{task.description} ({task.duration} min)")
                    with col2:
                        st.write(f"Priority: {task.priority}")
        
        if result["conflicts"]:
            st.subheader(f"⚠️ Scheduling Conflicts ({len(result['conflicts'])})")
            for conflict in result["conflicts"]:
                st.warning(conflict)
        
        st.divider()
        st.subheader("📊 Decision Analysis")
        decision_data = []
        for decision in result["decisions"]:
            decision_data.append({"Task": decision.task_name, "Scheduled": "✓" if decision.scheduled else "✗", "Confidence": f"{decision.confidence_score:.2f}", "Reason": decision.reasoning[:50] + "..." if len(decision.reasoning) > 50 else decision.reasoning})
        st.dataframe(decision_data, use_container_width=True)
        
        st.divider()
        st.subheader("🔄 Alternative Strategies")
        for alt in result.get("alternatives", []):
            with st.expander(f"📌 {alt['name']}"):
                st.write(f"**Description:** {alt['description']}")
                st.write(f"**Strategy:** {alt['strategy']}")
                st.write(f"**Estimated Success:** {alt['estimated_success']:.0%}")
    else:
        st.info("Click 'Generate AI Schedule' to get started")

with tab4:
    st.subheader("� Pet Care Q&A")
    st.caption("Ask questions about grooming, feeding, exercise, training, health, and enrichment")
    
    # Get pet-specific tips
    if st.session_state.owner.pets:
        selected_pet_name = st.selectbox("Select a pet for context (optional)", ["General", *[p.name for p in st.session_state.owner.pets]])
        selected_pet = None
        if selected_pet_name != "General":
            selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        
        if selected_pet:
            with st.expander(f"📌 Care Tips for {selected_pet.name}", expanded=True):
                tips = st.session_state.pet_qa.get_pet_specific_tips(selected_pet)
                st.markdown(tips)
        
        st.divider()
    
    # Q&A interface
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.text_input("Ask a pet care question:", placeholder="e.g., 'How often should I groom my dog?'", key="qa_input")
    with col2:
        ask_btn = st.button("🔍 Ask", use_container_width=True)
    
    if ask_btn and user_question:
        selected_pet_for_qa = None
        if selected_pet_name != "General":
            selected_pet_for_qa = selected_pet
        
        with st.spinner("🤖 Searching knowledge base..."):
            answer, confidence = st.session_state.pet_qa.answer_question(user_question, selected_pet_for_qa)
        
        st.divider()
        st.markdown(f"**Q: {user_question}**")
        
        # Display confidence level
        confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        confidence_emoji = confidence_colors.get(confidence, "❓")
        st.caption(f"Confidence: {confidence_emoji} {confidence.upper()}")
        
        st.markdown(f"**A:** {answer}")
        
        st.divider()
    
    st.divider()
    st.subheader("🔎 Knowledge Base Search")
    search_query = st.text_input("Search guidelines:", placeholder="e.g., 'dog exercise', 'cat grooming', 'rabbit diet'", key="search_input")
    if search_query:
        search_results = st.session_state.pet_qa.search_guidelines(search_query)
        st.markdown(search_results)
    
    st.divider()
    st.subheader("💭 Conversation History")
    history = st.session_state.pet_qa.get_conversation_history()
    if history:
        for i, entry in enumerate(reversed(history[-5:])):  # Show last 5
            with st.expander(f"Q: {entry['question'][:60]}..."):
                st.markdown(f"**Answer:** {entry['answer']}")
                st.caption(f"Source: {entry['source']} | Confidence: {entry['confidence']}")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.pet_qa.clear_history()
            st.rerun()
    else:
        st.info("No questions asked yet. Ask something to see history!")

with tab5:
    st.subheader("�📈 AI Reliability & Insights")
    logger_instance = st.session_state.ai_logger
    stats = logger_instance.get_reliability_stats()
    
    if stats["total_decisions"] > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Decisions", stats["total_decisions"])
        with col2:
            st.metric("Scheduled", stats["scheduled_count"])
        with col3:
            st.metric("Avg Confidence", f"{stats['average_confidence']:.2f}/1.0")
        with col4:
            st.metric("Scheduling Rate", f"{stats['scheduling_rate']:.0%}")
        
        st.divider()
        with st.expander("📋 Full Reliability Report", expanded=True):
            report = logger_instance.generate_reliability_report()
            st.code(report, language="text")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export Decision Journal"):
                journal_path = logger_instance.export_journal()
                st.success(f"✓ Exported to {journal_path}")
        with col2:
            if st.button("📊 View Decision History"):
                st.json([{"task": d["task_name"], "scheduled": d["scheduled"], "confidence": d["confidence"], "time": d["timestamp"]} for d in logger_instance.decision_journal[:10]])
    else:
        st.info("No decisions recorded yet. Generate a schedule to see insights.")

with tab6:
    st.subheader("⚙️ Settings")
    st.write("**Owner Settings**")
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Owner name", value=owner.name)
        if new_name != owner.name:
            owner.name = new_name
            owner.save_to_json("data.json")
            st.success("✓ Updated")
    with col2:
        new_time = st.number_input("Available time (minutes/day)", value=owner.available_time, min_value=1)
        if new_time != owner.available_time:
            owner.available_time = new_time
            owner.save_to_json("data.json")
            st.success("✓ Updated")
    
    st.divider()
    st.write("**Pet Management**")
    for i, pet in enumerate(owner.pets):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.write(f"**{pet.name}** ({pet.species}, age {pet.age})")
        with col2:
            if pet.special_needs:
                st.write(f"Special needs: {', '.join(pet.special_needs)}")
        with col3:
            if st.button("Remove", key=f"remove_pet_{i}", use_container_width=True):
                owner.remove_pet(pet.name)
                owner.save_to_json("data.json")
                st.rerun()
    
    st.divider()
    st.write("**Add New Pet**")
    col1, col2, col3 = st.columns(3)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
    with col3:
        new_pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)
    
    special_needs = st.text_input("Special needs (comma-separated, optional)")
    if st.button("➕ Add Pet", use_container_width=True):
        if new_pet_name:
            special_needs_list = [s.strip() for s in special_needs.split(",") if s.strip()]
            new_pet = Pet(name=new_pet_name, species=new_pet_species, age=new_pet_age, special_needs=special_needs_list)
            owner.add_pet(new_pet)
            owner.save_to_json("data.json")
            st.success(f"✓ Added {new_pet_name}")
            st.rerun()
        else:
            st.warning("Please enter a pet name")
    
    st.divider()
    st.write("**AI Configuration**")
    st.info("Current mode: Mock AI (Ollama not connected). Enable Ollama in AI Schedule tab to use local model.")
