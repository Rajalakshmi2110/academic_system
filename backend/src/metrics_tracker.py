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
                data = json.load(f)
            if data:
                # Merge with defaults to ensure all keys exist
                defaults = self._init_metrics()
                defaults.update(data)
                return defaults
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
            'layer3_success': 0,
            'layer3_error': 0,
            'confidence_scores': [],
            'latencies': [],
            'layer1_latencies': [],
            'layer2_latencies': [],
            'layer3_latencies': [],
            'daily_stats': {},
            'hourly_stats': {},
            'last_updated': None
        }
    
    def _save_metrics(self, subject_id, metrics):
        metrics_file = self._get_metrics_file(subject_id)
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def _cap_list(self, lst, limit=1000):
        return lst[-limit:] if len(lst) > limit else lst

    def track_question(self, subject_id, result):
        """Track a question and its result"""
        metrics = self._load_metrics(subject_id)
        
        # Ensure new fields exist for older metrics files
        for key, default in [('layer3_success', 0), ('layer3_error', 0),
                             ('layer1_latencies', []), ('layer2_latencies', []),
                             ('layer3_latencies', []), ('hourly_stats', {})]:
            if key not in metrics:
                metrics[key] = default
        
        metrics['total_questions'] += 1
        
        # Track Layer 1 (pipeline returns 'IN_SYLLABUS' or 'OUT_OF_SYLLABUS')
        l1 = result.get('layer1_result', '')
        if l1 in ('PASS', 'IN_SYLLABUS'):
            metrics['layer1_pass'] += 1
        else:
            metrics['layer1_fail'] += 1
        
        # Track Layer 2
        layer2_status = result.get('layer2_result') or result.get('final_status')
        if layer2_status in ('VALID', 'IN_SYLLABUS'):
            metrics['layer2_valid'] += 1
        elif layer2_status == 'WARNING':
            metrics['layer2_warning'] += 1
        elif layer2_status == 'OUT_OF_SYLLABUS':
            metrics['layer2_out_of_syllabus'] += 1
        elif layer2_status == 'REJECTED':
            metrics['layer2_rejected'] += 1
        
        # Track Layer 3
        if result.get('status') == 'success':
            metrics['layer3_success'] += 1
        elif result.get('final_status') in ('OUT_OF_SYLLABUS', 'REJECTED'):
            pass  # didn't reach Layer 3
        elif result.get('status') == 'error':
            metrics['layer3_error'] += 1
        
        # Track confidence score
        if result.get('confidence_score'):
            metrics['confidence_scores'].append(result['confidence_score'])
            metrics['confidence_scores'] = self._cap_list(metrics['confidence_scores'])
        
        # Track per-layer latencies
        steps = result.get('intermediate_steps', {})
        if steps.get('layer1', {}).get('latency_ms'):
            metrics['layer1_latencies'].append(steps['layer1']['latency_ms'])
            metrics['layer1_latencies'] = self._cap_list(metrics['layer1_latencies'])
        if steps.get('layer2', {}).get('latency_ms'):
            metrics['layer2_latencies'].append(steps['layer2']['latency_ms'])
            metrics['layer2_latencies'] = self._cap_list(metrics['layer2_latencies'])
        if steps.get('layer3', {}).get('latency_ms'):
            metrics['layer3_latencies'].append(steps['layer3']['latency_ms'])
            metrics['layer3_latencies'] = self._cap_list(metrics['layer3_latencies'])
        
        # Track total latency
        if result.get('total_latency_ms'):
            metrics['latencies'].append(result['total_latency_ms'])
            metrics['latencies'] = self._cap_list(metrics['latencies'])
        
        # Track daily stats
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        if today not in metrics['daily_stats']:
            metrics['daily_stats'][today] = 0
        metrics['daily_stats'][today] += 1
        
        # Track hourly stats
        hour = str(now.hour)
        if hour not in metrics['hourly_stats']:
            metrics['hourly_stats'][hour] = 0
        metrics['hourly_stats'][hour] += 1
        
        # Keep only last 30 days
        if len(metrics['daily_stats']) > 30:
            sorted_dates = sorted(metrics['daily_stats'].keys())
            for old_date in sorted_dates[:-30]:
                del metrics['daily_stats'][old_date]
        
        metrics['last_updated'] = now.isoformat()
        
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
        
        def _avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else 0

        total = metrics['total_questions']
        return {
            'usage': {
                'total_questions': total,
                'today': today_count,
                'this_week': week_count,
                'avg_confidence': round(avg_confidence, 2),
                'avg_latency_ms': round(avg_latency, 2),
                'low_confidence_count': low_confidence_count
            },
            'layer1': {
                'pass': metrics['layer1_pass'],
                'fail': metrics['layer1_fail'],
                'pass_rate': round(metrics['layer1_pass'] / total * 100, 1) if total > 0 else 0,
                'avg_latency_ms': _avg(metrics.get('layer1_latencies', []))
            },
            'layer2': {
                'valid': metrics['layer2_valid'],
                'warning': metrics['layer2_warning'],
                'out_of_syllabus': metrics['layer2_out_of_syllabus'],
                'rejected': metrics['layer2_rejected'],
                'avg_latency_ms': _avg(metrics.get('layer2_latencies', []))
            },
            'layer3': {
                'success': metrics.get('layer3_success', 0),
                'error': metrics.get('layer3_error', 0),
                'success_rate': round(metrics.get('layer3_success', 0) / total * 100, 1) if total > 0 else 0,
                'avg_latency_ms': _avg(metrics.get('layer3_latencies', []))
            },
            'daily_stats': metrics['daily_stats'],
            'hourly_stats': metrics.get('hourly_stats', {}),
            'last_updated': metrics['last_updated']
        }
    
    def get_overall_metrics(self, subject_ids):
        """Get aggregated metrics across all subjects"""
        from datetime import timedelta
        combined = self._init_metrics()
        all_confidence = []
        all_latencies = []
        all_l1_lat = []
        all_l2_lat = []
        all_l3_lat = []
        all_daily = {}
        all_hourly = {}

        for sid in subject_ids:
            m = self._load_metrics(sid)
            combined['total_questions'] += m.get('total_questions', 0)
            combined['layer1_pass'] += m.get('layer1_pass', 0)
            combined['layer1_fail'] += m.get('layer1_fail', 0)
            combined['layer2_valid'] += m.get('layer2_valid', 0)
            combined['layer2_warning'] += m.get('layer2_warning', 0)
            combined['layer2_out_of_syllabus'] += m.get('layer2_out_of_syllabus', 0)
            combined['layer2_rejected'] += m.get('layer2_rejected', 0)
            combined['layer3_success'] = combined.get('layer3_success', 0) + m.get('layer3_success', 0)
            combined['layer3_error'] = combined.get('layer3_error', 0) + m.get('layer3_error', 0)
            all_confidence.extend(m.get('confidence_scores', []))
            all_latencies.extend(m.get('latencies', []))
            all_l1_lat.extend(m.get('layer1_latencies', []))
            all_l2_lat.extend(m.get('layer2_latencies', []))
            all_l3_lat.extend(m.get('layer3_latencies', []))
            for d, c in m.get('daily_stats', {}).items():
                all_daily[d] = all_daily.get(d, 0) + c
            for h, c in m.get('hourly_stats', {}).items():
                all_hourly[h] = all_hourly.get(h, 0) + c

        def _avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else 0

        total = combined['total_questions']
        avg_confidence = _avg(all_confidence)
        avg_latency = _avg(all_latencies)
        low_confidence_count = sum(1 for s in all_confidence if s < 0.6)

        today = datetime.now().strftime('%Y-%m-%d')
        today_count = all_daily.get(today, 0)
        week_count = sum(all_daily.get((datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 0) for i in range(7))

        # Per-subject breakdown
        per_subject = {}
        for sid in subject_ids:
            m = self._load_metrics(sid)
            per_subject[sid] = {
                'total_questions': m.get('total_questions', 0),
                'layer3_success': m.get('layer3_success', 0),
                'avg_confidence': _avg(m.get('confidence_scores', []))
            }

        # Combine feedback across all subjects
        all_feedback = {'helpful': 0, 'not_helpful': 0, 'total': 0}
        fb = self.get_feedback_metrics(None)
        all_feedback = fb

        return {
            'usage': {
                'total_questions': total,
                'today': today_count,
                'this_week': week_count,
                'avg_confidence': avg_confidence,
                'avg_latency_ms': avg_latency,
                'low_confidence_count': low_confidence_count
            },
            'layer1': {
                'pass': combined['layer1_pass'],
                'fail': combined['layer1_fail'],
                'pass_rate': round(combined['layer1_pass'] / total * 100, 1) if total > 0 else 0,
                'avg_latency_ms': _avg(all_l1_lat)
            },
            'layer2': {
                'valid': combined['layer2_valid'],
                'warning': combined['layer2_warning'],
                'out_of_syllabus': combined['layer2_out_of_syllabus'],
                'rejected': combined['layer2_rejected'],
                'avg_latency_ms': _avg(all_l2_lat)
            },
            'layer3': {
                'success': combined.get('layer3_success', 0),
                'error': combined.get('layer3_error', 0),
                'success_rate': round(combined.get('layer3_success', 0) / total * 100, 1) if total > 0 else 0,
                'avg_latency_ms': _avg(all_l3_lat)
            },
            'daily_stats': all_daily,
            'hourly_stats': all_hourly,
            'per_subject': per_subject,
            'feedback': all_feedback,
            'last_updated': datetime.now().isoformat()
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
