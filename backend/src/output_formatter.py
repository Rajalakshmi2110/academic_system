from typing import Dict, Any
import re
import html

class OutputFormatter:
    @staticmethod
    def format_response(data: Dict[str, Any], format_type: str = 'json') -> Any:
        # Clean HTML entities from answer
        if 'answer' in data and isinstance(data['answer'], str):
            data['answer'] = html.unescape(data['answer'])
        
        if format_type == 'structured':
            data['formatted_answer'] = OutputFormatter._structure_answer(data.get('answer', ''))
        return data
    
    @staticmethod
    def _structure_answer(text: str) -> Dict[str, Any]:
        """Parse answer into structured sections"""
        result = {'sections': []}
        
        # Split by code blocks (``` or ```language markers)
        parts = re.split(r'```(?:\w+)?\n?', text)
        
        for i, part in enumerate(parts):
            if i % 2 == 1:  # Code block
                result['sections'].append({
                    'type': 'code',
                    'content': part.strip()
                })
            else:  # Text
                # Check for numbered steps
                if re.search(r'^\s*\d+[\.\)]', part, re.MULTILINE):
                    steps = [s.strip() for s in re.split(r'\n(?=\d+[\.\)])', part) if s.strip()]
                    result['sections'].append({
                        'type': 'steps',
                        'content': steps
                    })
                elif part.strip():
                    result['sections'].append({
                        'type': 'text',
                        'content': part.strip()
                    })
        
        return result
