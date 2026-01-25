import re
import json
from pathlib import Path

def parse_validation_response(response):
    status = "WARNING"
    explanation = "Unable to parse model response"
    confidence = 0.5

    response = response.strip()
    
    # Handle various response formats
    response_upper = response.upper()
    
    # Check for simple status words
    if "VALID" in response_upper and "INVALID" not in response_upper:
        status = "VALID"
        explanation = "The question is academically valid and well-formed."
        confidence = 0.85
    elif "WARNING" in response_upper or "WARN" in response_upper:
        status = "WARNING"
        explanation = "The question needs clarification or improvement."
        confidence = 0.65
    elif "REJECT" in response_upper or "INVALID" in response_upper:
        status = "REJECTED"
        explanation = "The question contains errors or is inappropriate."
        confidence = 0.95
    
    # Try to extract structured format
    status_match = re.search(
        r'STATUS\s*:\s*(VALID|WARNING|REJECTED)',
        response,
        re.IGNORECASE
    )
    if status_match:
        status = status_match.group(1).upper()

    # Extract explanation if available
    explanation_match = re.search(
        r'EXPLANATION\s*:\s*(.*?)(?:CONFIDENCE|$)',
        response,
        re.IGNORECASE | re.DOTALL
    )
    if explanation_match:
        explanation = explanation_match.group(1).strip()

    # Extract confidence if available
    confidence_match = re.search(
        r'CONFIDENCE\s*:\s*([0-9]*\.?[0-9]+)',
        response
    )
    if confidence_match:
        confidence = float(confidence_match.group(1))
        confidence = max(0.0, min(1.0, confidence))
    else:
        # Default confidence based on status
        confidence = {"VALID": 0.85, "WARNING": 0.65, "REJECTED": 0.95}[status]

    return {
        "status": status,
        "explanation": explanation,
        "confidence": confidence
    }

def format_final_response(layer1_result, layer2_result=None, question=""):
    """
    Format the final response from both layers
    
    Args:
        layer1_result (dict): Result from Layer 1 DistilBERT
        layer2_result (dict): Result from Layer 2 FLAN-T5 (optional)
        question (str): Original question
        
    Returns:
        dict: Formatted final response
    """
    if not layer1_result['relevant']:
        # Out-of-syllabus response
        return {
            'question': question,
            'layer1_result': 'OUT_OF_SYLLABUS',
            'layer2_result': None,
            'final_status': 'OUT_OF_SYLLABUS',
            'message': 'This question is not related to the CA3104 Computer Networks syllabus.',
            'suggestion': 'Please ask questions about network protocols, architectures, or concepts covered in Units I-V.',
            'confidence': layer1_result['confidence']
        }
    
    # In-syllabus response with Layer 2 validation
    return {
        'question': question,
        'layer1_result': 'IN_SYLLABUS',
        'layer2_result': layer2_result['status'],
        'final_status': layer2_result['status'],
        'explanation': layer2_result['explanation'],
        'confidence': layer2_result['confidence']
    }

def load_syllabus_context():
    """Load CA3104 syllabus context for validation"""
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
    """
    Basic validation of question format
    
    Args:
        question (str): Question to validate
        
    Returns:
        dict: Validation result
    """
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
    """Get standard response templates for different scenarios"""
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
    """
    Calculate combined confidence score from both layers
    
    Args:
        layer1_confidence (float): Confidence from Layer 1
        layer2_confidence (float): Confidence from Layer 2 (optional)
        
    Returns:
        float: Combined confidence score
    """
    if layer2_confidence is None:
        return layer1_confidence
    
    # Weighted average: Layer 1 (30%) + Layer 2 (70%)
    return (0.3 * layer1_confidence) + (0.7 * layer2_confidence)

def save_validation_log(results, log_file='validation_log.json'):
    """Save validation results to log file"""
    log_path = Path('reports') / log_file
    log_path.parent.mkdir(exist_ok=True)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return log_path