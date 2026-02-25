from groq import Groq
import time
import json
import os
from pathlib import Path
from dotenv import load_dotenv

class MCPValidator:
    def __init__(self, subject_id='data_structures'):
        load_dotenv()  # Load GROQ_API_KEY from .env
        
        self.subject_id = subject_id
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set. Get free key from: https://console.groq.com/keys")
        
        self.client = Groq(api_key=api_key)
        
        # Load syllabus from subjects/{subject_id}/syllabus.json
        base_dir = Path(__file__).parent.parent.parent.parent
        syllabus_path = base_dir / 'subjects' / subject_id / 'syllabus.json'
        
        if not syllabus_path.exists():
            raise FileNotFoundError(f"Syllabus not found for {subject_id} at {syllabus_path}")
        
        with open(syllabus_path, 'r') as f:
            self.syllabus = json.load(f)
        
        self.subject_name = self.syllabus.get('course_name', subject_id)
        print(f"MCP-based validator initialized for {self.subject_name} with Groq (Llama 3.3 70B)")
    
    def get_syllabus_topics(self):
        topics = []
        for unit in self.syllabus['units']:
            topics.extend(unit['topics'])
        return topics
    
    def validate_question(self, question):
        start_time = time.time()
        
        # Get syllabus topics for validation
        syllabus_topics = self.get_syllabus_topics()
        syllabus_topics_lower = [topic.lower() for topic in syllabus_topics]
        question_lower = question.lower()
        
        found_in_syllabus = any(topic_word in question_lower for topic in syllabus_topics_lower for topic_word in topic.split())
        
        tools = [{
            "type": "function",
            "function": {
                "name": "get_syllabus_topics",
                "description": f"Get the list of allowed topics in {self.subject_name} syllabus",
                "parameters": {"type": "object", "properties": {}}
            }
        }]
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated model
                messages=[
                    {"role": "system", "content": f"""You are a strict syllabus validator for {self.subject_name} course.

IMPORTANT: You MUST call get_syllabus_topics() tool first to check the exact syllabus topics.

Your job: Categorize questions into 4 types:

1. REJECTED ❌ - Gibberish OR Non-{self.subject_name} topics:
   - Gibberish: asdfasdf, ?????, qwertyuiop
   - Completely unrelated topics (e.g., cooking, sports, other subjects)
   Action: Return REJECTED immediately

2. OUT_OF_SYLLABUS 🚫 - {self.subject_name} topics NOT in the syllabus:
   - CRITICAL: Call get_syllabus_topics() to get exact syllabus topics
   - If topic is related to {self.subject_name} but NOT in the syllabus list → OUT_OF_SYLLABUS
   - Example: "Red-Black tree" is a DS topic, but if not in syllabus → OUT_OF_SYLLABUS
   - Example: "Fibonacci heap" is a DS topic, but if not in syllabus → OUT_OF_SYLLABUS
   Action: Show "Not in syllabus but covered in materials" with "Answer Anyway" button

3. WARNING ⚠️ - Contains incorrect facts (but still answer it!):
   - Questions with wrong assumptions or facts
   - Only use if question is IN syllabus but has wrong facts
   Action: Proceed to Layer 3 with warning badge

4. VALID ✅ - Questions about topics IN the syllabus:
   - MUST match topics from get_syllabus_topics()
   - Questions with typos are still VALID if topic is in syllabus
   - Vague questions are VALID if topic is in syllabus
   Action: Proceed to Layer 3

STRICT RULE: Always call get_syllabus_topics() first, then check if question topic matches ANY topic in the list.

Respond with JSON:
{{"status": "VALID", "reason": "Topic found in syllabus: [topic name]"}}
or
{{"status": "WARNING", "reason": "Contains incorrect fact: [what's wrong]"}}
or
{{"status": "OUT_OF_SYLLABUS", "reason": "[Topic] is a {self.subject_name} topic but not in this course syllabus"}}
or
{{"status": "REJECTED", "reason": "Gibberish or unrelated to {self.subject_name}"}}"""},
                    {"role": "user", "content": f"Validate: {question}"}
                ],
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "get_syllabus_topics"}},  # Force calling the tool
                temperature=0,
                max_tokens=200
            )
            
            message = response.choices[0].message
            
            # LLM called the tool - send syllabus topics back
            if message.tool_calls:
                topics = self.get_syllabus_topics()
                
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"""You received the COMPLETE syllabus topics list for {self.subject_name}.

IMPORTANT: Check if the question is RELATED to any syllabus topic, not just exact matches.

Validation rules:
1. Extract the main concept from the question
2. Check if it's related to ANY syllabus topic (including examples, problems, or applications)
3. If YES (related) → VALID
4. If NO but it's a {self.subject_name} topic → OUT_OF_SYLLABUS
5. If completely unrelated → REJECTED

Examples for Operating Systems:
- Question: "dining philosophers problem" + Topics: ["Semaphores", "Deadlock"] → VALID (classic example for semaphores/deadlock)
- Question: "producer-consumer problem" + Topics: ["Process Synchronization"] → VALID (classic synchronization example)
- Question: "banker's algorithm" + Topics: ["Deadlock Avoidance"] → VALID (algorithm for deadlock avoidance)
- Question: "RAID levels" + Topics: ["Disk Structures"] → OUT_OF_SYLLABUS (RAID not covered)

Examples for Data Structures:
- Question: "fibonacci heap" + Topics: ["Binary Heaps"] → OUT_OF_SYLLABUS (different heap type)
- Question: "red-black tree" + Topics: ["AVL Trees", "Binary Search Trees"] → OUT_OF_SYLLABUS (different tree type)
- Question: "AVL tree rotation" + Topics: ["AVL Trees"] → VALID (related to AVL trees)

Be FLEXIBLE: If the question is about a classic problem/example/algorithm that teaches a syllabus topic, mark it VALID.
Be STRICT: Only mark OUT_OF_SYLLABUS if it's a different specific data structure/algorithm not covered.

Respond with JSON only: {{"status": "VALID/OUT_OF_SYLLABUS/REJECTED", "reason": "..."}}"""},
                        {"role": "user", "content": f"Question: {question}\n\nSyllabus topics: {json.dumps(syllabus_topics)}"},
                        {"role": "assistant", "content": None, "tool_calls": message.tool_calls},
                        {"role": "tool", "tool_call_id": message.tool_calls[0].id, "content": json.dumps(syllabus_topics)}
                    ],
                    temperature=0,
                    max_tokens=200
                )
                message = response.choices[0].message
            
            result_text = message.content.strip()
            
            try:
                result = json.loads(result_text)
                status = result.get('status', 'VALID')
                reason = result.get('reason', '')
            except:
                if 'WARNING' in result_text or 'warning' in result_text.lower():
                    status = 'WARNING'
                    reason = result_text
                elif 'OUT_OF_SYLLABUS' in result_text or 'out of syllabus' in result_text.lower():
                    status = 'OUT_OF_SYLLABUS'
                    reason = result_text
                elif 'REJECTED' in result_text or 'rejected' in result_text.lower():
                    status = 'REJECTED'
                    reason = result_text
                else:
                    status = 'VALID'
                    reason = 'Question is clear and within syllabus'
            
            inference_time = (time.time() - start_time) * 1000
            
            if status == 'VALID':
                return {
                    'question': question,
                    'status': 'VALID',
                    'explanation': reason or 'Question is clear and within syllabus.',
                    'confidence': 0.90,
                    'inference_time_ms': inference_time
                }
            elif status == 'WARNING':
                return {
                    'question': question,
                    'status': 'WARNING',
                    'explanation': reason,
                    'confidence': 0.85,
                    'inference_time_ms': inference_time
                }
            elif status == 'OUT_OF_SYLLABUS':
                return {
                    'question': question,
                    'final_status': 'OUT_OF_SYLLABUS',
                    'explanation': reason,
                    'suggestion': f'Please ask about {self.subject_name} topics covered in the syllabus.',
                    'confidence': 0.90,
                    'inference_time_ms': inference_time
                }
            else:
                return {
                    'question': question,
                    'final_status': 'REJECTED',
                    'explanation': reason,
                    'confidence': 0.90,
                    'inference_time_ms': inference_time
                }
                
        except Exception as e:
            return {
                'question': question,
                'final_status': 'REJECTED',
                'explanation': f'Validation error: {str(e)}',
                'confidence': 0.0,
                'inference_time_ms': (time.time() - start_time) * 1000
            }
