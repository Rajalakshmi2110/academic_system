from groq import Groq
import time
import json
from pathlib import Path

class MCPValidator:
    def __init__(self):
        # Get free API key from: https://console.groq.com/keys
        self.client = Groq(
            api_key="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"  # Replace with your free key
        )
        
        # Load syllabus
        syllabus_path = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'ca3101_syllabus.json'
        with open(syllabus_path, 'r') as f:
            self.syllabus = json.load(f)
        
        print("MCP-based validator initialized with Groq (Llama 3.1 70B)")
    
    def get_syllabus_topics(self):
        """MCP Tool: Get allowed topics from CA3101 syllabus"""
        topics = []
        for unit in self.syllabus['units']:
            topics.extend(unit['topics'])
        return topics
    
    def validate_question(self, question):
        """Validate question using Groq Llama 3.1 with function calling (MCP-style)"""
        start_time = time.time()
        
        # Define MCP-style tool
        tools = [{
            "type": "function",
            "function": {
                "name": "get_syllabus_topics",
                "description": "Get the list of allowed topics in CA3101 Data Structures syllabus",
                "parameters": {"type": "object", "properties": {}}
            }
        }]
        
        try:
            # Call Groq with MCP tool
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated model
                messages=[
                    {"role": "system", "content": """You are a validator for CA3101 Data Structures course.

Your job: Categorize questions into 3 types:

1. REJECTED - Complete gibberish or out-of-syllabus:
   - Gibberish: asdfasdf, ?????, qwertyuiop
   - Out-of-syllabus DS: Skip lists, Fibonacci heaps, Red-black trees, Splay trees, Suffix trees, Segment trees
   - Non-DS: AWS, cloud, React, SQL, databases

2. WARNING - Contains incorrect facts (but still answer it!):
   - "Stack is FIFO right?" → WARNING (wrong fact, but Layer 3 will correct)
   - "Is binary search O(n^2)?" → WARNING (wrong complexity)
   - "Queue is LIFO correct?" → WARNING (wrong fact)
   - "Trees can have cycles?" → WARNING (wrong concept)

3. VALID - Everything else:
   - Correct questions
   - Questions with typos
   - Vague or short questions
   - Questions about AVL, 2-3 trees, B-trees (in syllabus!)

Respond with JSON:
{"status": "VALID", "reason": "Question is clear"}
or
{"status": "WARNING", "reason": "Contains incorrect fact: [what's wrong]"}
or
{"status": "OUT_OF_SYLLABUS", "reason": "Topic X not in CA3101"}
or
{"status": "REJECTED", "reason": "Complete gibberish"}"""},
                    {"role": "user", "content": f"Validate: {question}"}
                ],
                tools=tools,
                tool_choice="auto",
                temperature=0,
                max_tokens=200
            )
            
            message = response.choices[0].message
            
            # Check if LLM wants to call the tool
            if message.tool_calls:
                # LLM called get_syllabus_topics
                topics = self.get_syllabus_topics()
                
                # Send tool result back to LLM
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Validate the question against these topics."},
                        {"role": "user", "content": f"Question: {question}"},
                        {"role": "assistant", "content": None, "tool_calls": message.tool_calls},
                        {"role": "tool", "tool_call_id": message.tool_calls[0].id, "content": json.dumps(topics)}
                    ],
                    temperature=0,
                    max_tokens=200
                )
                message = response.choices[0].message
            
            # Parse LLM response
            result_text = message.content.strip()
            
            # Try to parse as JSON
            try:
                result = json.loads(result_text)
                status = result.get('status', 'VALID')
                reason = result.get('reason', '')
            except:
                # Fallback parsing
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
                # WARNING: Question has incorrect facts but still proceed to Layer 3
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
                    'suggestion': 'Please ask about CA3101 topics: arrays, linked lists, stacks, queues, trees, graphs, heaps, hashing, sorting.',
                    'confidence': 0.90,
                    'inference_time_ms': inference_time
                }
            else:  # REJECTED
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
