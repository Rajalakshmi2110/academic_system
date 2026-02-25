"""
Metrics Tracker - Tracks real-time usage metrics for the system
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class MetricsTracker:
    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = Path(__file__).parent.parent.parent / 'subjects'
        else:
            self.base_path = Path(base_path)
    
    def _get_metrics_file(self, subject_id):
        metrics_dir = self.base_path / subject_id / 'metrics'
        metrics_dir.mkdir(parents=True, exist_ok=True)
        return metrics_dir / 'usage_metrics.json'
    
    def _load_metrics(self, subject_id):
        metrics_file = self._get_metrics_file(subject_id)
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                return json.load(f)
        return self._init_metrics()
    
    def _init_metrics(self):
        return {
            'total_questions': 0,
            'layer1_pass': 0,
            'layer1_fail': 0,
            'layer2_valid': 0,
            'layer2_warning': 0,
            'layer2_out_of_syllabus': 0,
            'layer2_rejected': 0,
            'confidence_scores': [],
            'latencies': [],
            'daily_stats': {},
            'last_updated': None
        }
    
    def _save_metrics(self, subject_id, metrics):
        metrics_file = self._get_metrics_file(subject_id)
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def track_question(self, subject_id, result):
        """Track a question and its result"""
        metrics = self._load_metrics(subject_id)
        
        # Update counters
        metrics['total_questions'] += 1
        
        # Track Layer 1
        if result.get('layer1_result') == 'PASS':
            metrics['layer1_pass'] += 1
        else:
            metrics['layer1_fail'] += 1
        
        # Track Layer 2
        layer2_status = result.get('layer2_result') or result.get('final_status')
        if layer2_status == 'VALID' or layer2_status == 'IN_SYLLABUS':
            metrics['layer2_valid'] += 1
        elif layer2_status == 'WARNING':
            metrics['layer2_warning'] += 1
        elif layer2_status == 'OUT_OF_SYLLABUS':
            metrics['layer2_out_of_syllabus'] += 1
        elif layer2_status == 'REJECTED':
            metrics['layer2_rejected'] += 1
        
        # Track confidence score
        if result.get('confidence_score'):
            metrics['confidence_scores'].append(result['confidence_score'])
            # Keep only last 1000 scores
            if len(metrics['confidence_scores']) > 1000:
                metrics['confidence_scores'] = metrics['confidence_scores'][-1000:]
        
        # Track latency
        if result.get('total_latency_ms'):
            metrics['latencies'].append(result['total_latency_ms'])
            # Keep only last 1000 latencies
            if len(metrics['latencies']) > 1000:
                metrics['latencies'] = metrics['latencies'][-1000:]
        
        # Track daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in metrics['daily_stats']:
            metrics['daily_stats'][today] = 0
        metrics['daily_stats'][today] += 1
        
        # Keep only last 30 days
        if len(metrics['daily_stats']) > 30:
            sorted_dates = sorted(metrics['daily_stats'].keys())
            for old_date in sorted_dates[:-30]:
                del metrics['daily_stats'][old_date]
        
        metrics['last_updated'] = datetime.now().isoformat()
        
        self._save_metrics(subject_id, metrics)
    
    def get_metrics(self, subject_id):
        """Get aggregated metrics for a subject"""
        metrics = self._load_metrics(subject_id)
        
        # Calculate averages
        avg_confidence = sum(metrics['confidence_scores']) / len(metrics['confidence_scores']) if metrics['confidence_scores'] else 0
        avg_latency = sum(metrics['latencies']) / len(metrics['latencies']) if metrics['latencies'] else 0
        
        # Count low confidence answers
        low_confidence_count = sum(1 for score in metrics['confidence_scores'] if score < 0.6)
        
        # Get today's and this week's stats
        today = datetime.now().strftime('%Y-%m-%d')
        today_count = metrics['daily_stats'].get(today, 0)
        
        # Calculate week total
        from datetime import timedelta
        week_count = 0
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            week_count += metrics['daily_stats'].get(date, 0)
        
        return {
            'usage': {
                'total_questions': metrics['total_questions'],
                'today': today_count,
                'this_week': week_count,
                'avg_confidence': round(avg_confidence, 2),
                'avg_latency_ms': round(avg_latency, 2),
                'low_confidence_count': low_confidence_count
            },
            'layer1': {
                'pass': metrics['layer1_pass'],
                'fail': metrics['layer1_fail'],
                'pass_rate': round(metrics['layer1_pass'] / metrics['total_questions'] * 100, 1) if metrics['total_questions'] > 0 else 0
            },
            'layer2': {
                'valid': metrics['layer2_valid'],
                'warning': metrics['layer2_warning'],
                'out_of_syllabus': metrics['layer2_out_of_syllabus'],
                'rejected': metrics['layer2_rejected']
            },
            'daily_stats': metrics['daily_stats'],
            'last_updated': metrics['last_updated']
        }
    
    def get_feedback_metrics(self, subject_id):
        """Get feedback metrics from feedback.json"""
        feedback_file = self.base_path.parent / 'backend' / 'feedback.json'
        if not feedback_file.exists():
            return {'helpful': 0, 'not_helpful': 0, 'total': 0, 'helpful_rate': 0}
        
        try:
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
            
            helpful = sum(1 for f in feedback_list if f.get('feedback') == 'helpful')
            not_helpful = sum(1 for f in feedback_list if f.get('feedback') == 'not_helpful')
            total = len(feedback_list)
            
            return {
                'helpful': helpful,
                'not_helpful': not_helpful,
                'total': total,
                'helpful_rate': round(helpful / total * 100, 1) if total > 0 else 0
            }
        except:
            return {'helpful': 0, 'not_helpful': 0, 'total': 0, 'helpful_rate': 0}
