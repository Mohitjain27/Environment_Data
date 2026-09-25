import json
import os
from detectors.pii_detector import PIIDetector
from config import DATA_DIR, OUTPUT_DIR
from .metrics import calculate_metrics

def evaluate():
    detector = PIIDetector()
    gt_file = os.path.join(DATA_DIR, 'pii_ground_truth.json')
    
    if not os.path.exists(gt_file):
        print(f"Ground truth file {gt_file} not found. Cannot evaluate.")
        return
        
    with open(gt_file, 'r') as f:
        ground_truth = json.load(f)
        
    tp, fp, fn = 0, 0, 0
    type_stats = {}
    
    for item in ground_truth:
        text = item['text']
        true_entities = item['entities']
        pred_entities = detector.detect(text)
        
        # Simple match logic
        true_set = {(e['start'], e['end'], e['type']) for e in true_entities}
        pred_set = {(e['start'], e['end'], e['type']) for e in pred_entities}
        
        tp += len(true_set & pred_set)
        fp += len(pred_set - true_set)
        fn += len(true_set - pred_set)
        
        # Record stats per type
        for e in true_set:
            t = e[2]
            if t not in type_stats:
                type_stats[t] = {'tp': 0, 'fp': 0, 'fn': 0}
            if e in pred_set:
                type_stats[t]['tp'] += 1
            else:
                type_stats[t]['fn'] += 1
                
        for e in pred_set - true_set:
            t = e[2]
            if t not in type_stats:
                type_stats[t] = {'tp': 0, 'fp': 0, 'fn': 0}
            type_stats[t]['fp'] += 1
            
    # Calculate overall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    report = {
        'overall': {
            'tp': tp, 'fp': fp, 'fn': fn,
            'precision': precision, 'recall': recall, 'f1': f1
        },
        'per_type': type_stats
    }
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(os.path.join(OUTPUT_DIR, 'evaluation_report.json'), 'w') as f:
        json.dump(report, f, indent=2)
        
    # Markdown
    with open(os.path.join(OUTPUT_DIR, 'evaluation_report.md'), 'w') as f:
        f.write("# Evaluation Report\n\n")
        f.write("## Overall Metrics\n")
        f.write(f"- **Precision:** {precision:.2f}\n")
        f.write(f"- **Recall:** {recall:.2f}\n")
        f.write(f"- **F1 Score:** {f1:.2f}\n\n")
        f.write("## Per-Type Metrics\n")
        f.write("| Type | TP | FP | FN | Precision | Recall | F1 |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for t, stats in type_stats.items():
            p = stats['tp'] / (stats['tp'] + stats['fp']) if (stats['tp'] + stats['fp']) > 0 else 0
            r = stats['tp'] / (stats['tp'] + stats['fn']) if (stats['tp'] + stats['fn']) > 0 else 0
            f1_t = 2 * p * r / (p + r) if (p + r) > 0 else 0
            f.write(f"| {t} | {stats['tp']} | {stats['fp']} | {stats['fn']} | {p:.2f} | {r:.2f} | {f1_t:.2f} |\n")
            
    print("Evaluation completed. Reports generated in output/.")
