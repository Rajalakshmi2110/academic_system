import re
import json
from pathlib import Path

def parse_validation_response(response):
    status = "WARNING"
    explanation = "Unable to parse model response"
    confidence = 0.5

    response = response.strip()
    print(f"DEBUG - Raw FLAN-T5 Response: '{response}'")
    
    simple_match = re.search(r'(VALID|WARNING|REJECTED)\s*-\s*(.+)', response, re.IGNORECASE)
    if simple_match:
        status = simple_match.group(1).upper()
        explanation = simple_match.group(2).strip()
        confidence = {"VALID": 0.85, "WARNING": 0.65, "REJECTED": 0.95}[status]
        return {
            "status": status,
            "explanation": explanation,
            "confidence": confidence
        }
    
    status_match = re.search(r'STATUS\s*:\s*(VALID|WARNING|REJECTED)', response, re.IGNORECASE)
    if status_match:
        status = status_match.group(1).upper()
        
        explanation_match = re.search(r'EXPLANATION\s*:\s*(.+?)(?:CONFIDENCE|$)', response, re.IGNORECASE | re.DOTALL)
        if explanation_match:
            explanation = explanation_match.group(1).strip()
        
        confidence_match = re.search(r'CONFIDENCE\s*:\s*([0-9]*\.?[0-9]+)', response)
        if confidence_match:
            confidence = float(confidence_match.group(1))
            confidence = max(0.0, min(1.0, confidence))
        else:
            confidence = {"VALID": 0.85, "WARNING": 0.65, "REJECTED": 0.95}[status]
        
        return {
            "status": status,
            "explanation": explanation,
            "confidence": confidence
        }
    
    response_upper = response.upper()
    if "VALID" in response_upper and "INVALID" not in response_upper:
        status = "VALID"
        explanation = "The question is academically valid and well-formed."
        confidence = 0.85
    elif "REJECT" in response_upper:
        status = "REJECTED"
        explanation = "The question contains errors or is inappropriate."
        confidence = 0.95
    elif "WARNING" in response_upper or "WARN" in response_upper:
        status = "WARNING"
        explanation = "The question needs clarification or improvement."
        confidence = 0.65
    else:
        status = "WARNING"
        explanation = f"Unable to parse response: {response[:100]}..."
        confidence = 0.5

    return {
        "status": status,
        "explanation": explanation,
        "confidence": confidence
    }

def format_final_response(layer1_result, layer2_result=None, question=""):
    if not layer1_result['relevant']:
        return {
            'question': question,
            'layer1_result': 'OUT_OF_SYLLABUS',
            'layer2_result': None,
            'final_status': 'OUT_OF_SYLLABUS',
            'message': 'This question is not related to the CA3104 Computer Networks syllabus.',
            'suggestion': 'Please ask questions about network protocols, architectures, or concepts covered in Units I-V.',
            'confidence': layer1_result['confidence']
        }
    
    return {
        'question': question,
        'layer1_result': 'IN_SYLLABUS',
        'layer2_result': layer2_result['status'],
        'final_status': layer2_result['status'],
        'explanation': layer2_result['explanation'],
        'confidence': layer2_result['confidence']
    }

def load_syllabus_context():
    return {
        'unit_1': {
            'title': 'Introduction to Computer Networks',
            'topics': [
                'Network components and topologies',
                'OSI and TCP/IP protocol models',
                'Network performance metrics',
                'Network types (LAN, WAN, MAN)'
            ]
        },
        'unit_2': {
            'title': 'Physical and Data Link Layer',
            'topics': [
                'Transmission media and encoding',
                'Framing and error detection/correction',
                'Multiple access protocols (CSMA/CD, CSMA/CA)',
                'Ethernet and wireless LANs'
            ]
        },
        'unit_3': {
            'title': 'Network Layer',
            'topics': [
                'IP addressing and subnetting',
                'Routing algorithms (distance vector, link state)',
                'IPv4/IPv6 protocols',
                'ICMP, ARP, NAT'
            ]
        },
        'unit_4': {
            'title': 'Transport Layer',
            'topics': [
                'TCP and UDP protocols',
                'Flow control and congestion control',
                'Connection establishment/termination',
                'Reliable data transfer'
            ]
        },
        'unit_5': {
            'title': 'Application Layer & Network Management',
            'topics': [
                'DNS, HTTP, SMTP, FTP',
                'Network security fundamentals',
                'SNMP and network monitoring',
                'Software-Defined Networking (SDN)'
            ]
        }
    }

def validate_question_format(question):
    if not question or not question.strip():
        return {
            'valid': False,
            'error': 'Question cannot be empty'
        }
    
    if len(question.strip()) < 10:
        return {
            'valid': False,
            'error': 'Question too short (minimum 10 characters)'
        }
    
    if len(question) > 500:
        return {
            'valid': False,
            'error': 'Question too long (maximum 500 characters)'
        }
    
    return {'valid': True}

def get_response_templates():
    return {
        'out_of_syllabus': {
            'message': 'This question is not related to the CA3104 Computer Networks syllabus.',
            'suggestion': 'Please ask questions about network protocols, architectures, or concepts covered in Units I-V.'
        },
        'valid': {
            'message': 'Question is valid and can be answered.',
        },
        'warning': {
            'message': 'Question needs clarification or has ambiguous elements.',
            'suggestion': 'Please provide more specific details or rephrase the question.'
        },
        'rejected': {
            'message': 'Question contains conceptual errors or incorrect assumptions.',
            'suggestion': 'Please review the relevant course material and rephrase the question.'
        }
    }

def calculate_confidence_score(layer1_confidence, layer2_confidence=None):
    if layer2_confidence is None:
        return layer1_confidence
    
    return (0.3 * layer1_confidence) + (0.7 * layer2_confidence)

def save_validation_log(results, log_file='validation_log.json'):
    log_path = Path('reports') / log_file
    log_path.parent.mkdir(exist_ok=True)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return log_path