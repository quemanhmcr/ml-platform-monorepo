"""
Train Component - MLOps Daily Pipeline

Mục đích:
    Train ML models (recommendation system) trên processed data và evaluate performance.
    Nếu model tốt hơn baseline, đăng ký vào Model Registry để deploy.

Workflow:
    1. Load processed data từ S3 processed/{date}/ prefix
    2. Split data thành train/validation/test sets
    3. Train model với hyperparameters được cấu hình
    4. Evaluate model trên validation và test sets
    5. Compare với baseline/production model
    6. Nếu model tốt hơn (metrics vượt threshold):
       - Save model artifacts lên S3 artifacts/{date}/models/
       - Register model vào Model Registry với metadata
       - Tag model là "production-ready" hoặc "staging"
    7. Nếu model không tốt:
       - Log metrics và reasons
       - Không register model
    8. Generate training report và metrics

Input:
    - Processed data từ S3: s3://{bucket}/processed/{date}/processed_data_*.parquet
    - Hyperparameters: learning_rate, batch_size, epochs, etc.
    - Baseline model metrics (để so sánh)

Output:
    - Model artifacts: s3://{bucket}/artifacts/{date}/models/model_{timestamp}.pkl
    - Model metadata: s3://{bucket}/artifacts/{date}/models/metadata.json
    - Training metrics: s3://{bucket}/artifacts/{date}/metrics.json
    - Training report: s3://{bucket}/artifacts/{date}/training_report.json

Model Registry:
    - Nếu model tốt: Register vào Model Registry với:
      - Model version (auto-increment)
      - Metrics (accuracy, precision, recall, F1, etc.)
      - Model path trong S3
      - Training timestamp
      - Hyperparameters used
      - Status: "production-ready" hoặc "staging"

Environment Variables:
    - S3_DATA_LAKE_BUCKET: S3 bucket name for data lake
    - S3_ARTIFACTS_PREFIX: Prefix for model artifacts (default: artifacts)
    - HYPERPARAMETERS: JSON string với hyperparameters
    - MODEL_REGISTRY_ENABLED: Enable model registry (default: true)
    - BASELINE_METRICS: JSON string với baseline model metrics
    - METRIC_THRESHOLD: Minimum improvement threshold (default: 0.02 = 2%)

Example:
    python -m src.main
    
    Output (nếu model tốt):
    - s3://ml-fashion-data-lake/artifacts/2025-01-15/models/model_20250115_020000.pkl
    - Model registered: v1.2.3 (production-ready)

MLOps Integration:
    - Chạy sau data processing và EDA trong Argo Workflow
    - Model registry integration với S3-based registry
    - Auto-trigger model deployment nếu model được register
    - Alert nếu training fails hoặc model performance drops
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_processed_data(bucket: str, date_prefix: str) -> Dict[str, Any]:
    """
    Mô phỏng load processed data từ S3.
    
    Args:
        bucket: S3 bucket name
        date_prefix: Date prefix
        
    Returns:
        Processed data metadata
    """
    logger.info(f"Loading processed data from s3://{bucket}/processed/{date_prefix}/")
    
    return {
        "s3_key": f"processed/{date_prefix}/processed_data_20250115_020000.parquet",
        "record_count": 9500,
        "features": 10
    }


def split_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng split data thành train/validation/test sets.
    
    Args:
        data: Processed data metadata
        
    Returns:
        Data splits metadata
    """
    logger.info("Splitting data into train/validation/test sets...")
    
    total = data["record_count"]
    train_size = int(total * 0.7)
    val_size = int(total * 0.15)
    test_size = total - train_size - val_size
    
    splits = {
        "train": train_size,
        "validation": val_size,
        "test": test_size,
        "split_ratio": {"train": 0.7, "validation": 0.15, "test": 0.15}
    }
    
    logger.info(f"  - Train: {splits['train']} ({splits['split_ratio']['train']:.0%})")
    logger.info(f"  - Validation: {splits['validation']} ({splits['split_ratio']['validation']:.0%})")
    logger.info(f"  - Test: {splits['test']} ({splits['split_ratio']['test']:.0%})")
    
    return splits


def train_model(data: Dict[str, Any], hyperparameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng training model.
    
    Args:
        data: Training data metadata
        hyperparameters: Model hyperparameters
        
    Returns:
        Training results
    """
    logger.info("Starting model training...")
    logger.info(f"  - Hyperparameters: {hyperparameters}")
    
    # Mô phỏng training process
    training_results = {
        "epochs": hyperparameters.get("epochs", 10),
        "training_time_seconds": 1200,  # 20 minutes
        "loss_history": [0.5, 0.3, 0.2, 0.15, 0.12, 0.10, 0.09, 0.08, 0.075, 0.07],
        "status": "completed"
    }
    
    logger.info(f"  - Training completed in {training_results['training_time_seconds']}s")
    logger.info(f"  - Final loss: {training_results['loss_history'][-1]:.4f}")
    
    return training_results


def evaluate_model(training_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng evaluate model trên validation và test sets.
    
    Args:
        training_results: Training results
        
    Returns:
        Evaluation metrics
    """
    logger.info("Evaluating model on validation and test sets...")
    
    # Mô phỏng evaluation metrics
    metrics = {
        "validation": {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.88,
            "f1_score": 0.865,
            "rmse": 0.32,
            "mae": 0.25
        },
        "test": {
            "accuracy": 0.86,
            "precision": 0.84,
            "recall": 0.87,
            "f1_score": 0.855,
            "rmse": 0.33,
            "mae": 0.26
        },
        "overall_score": 0.86  # Weighted average
    }
    
    logger.info(f"  - Validation Accuracy: {metrics['validation']['accuracy']:.2%}")
    logger.info(f"  - Test Accuracy: {metrics['test']['accuracy']:.2%}")
    logger.info(f"  - Overall Score: {metrics['overall_score']:.2%}")
    
    return metrics


def compare_with_baseline(metrics: Dict[str, Any], baseline_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    So sánh model mới với baseline/production model.
    
    Args:
        metrics: New model metrics
        baseline_metrics: Baseline model metrics
        
    Returns:
        Comparison results
    """
    logger.info("Comparing with baseline model...")
    
    if baseline_metrics is None:
        # Default baseline metrics
        baseline_metrics = {
            "accuracy": 0.82,
            "f1_score": 0.80,
            "rmse": 0.38
        }
    
    comparison = {
        "baseline": baseline_metrics,
        "new_model": {
            "accuracy": metrics["overall_score"],
            "f1_score": metrics["test"]["f1_score"],
            "rmse": metrics["test"]["rmse"]
        },
        "improvements": {
            "accuracy": metrics["overall_score"] - baseline_metrics["accuracy"],
            "f1_score": metrics["test"]["f1_score"] - baseline_metrics["f1_score"],
            "rmse": baseline_metrics["rmse"] - metrics["test"]["rmse"]  # Lower is better
        },
        "is_better": False
    }
    
    # Check if new model is better
    threshold = float(os.getenv("METRIC_THRESHOLD", "0.02"))  # 2% improvement
    accuracy_improvement = comparison["improvements"]["accuracy"]
    
    comparison["is_better"] = (
        accuracy_improvement >= threshold and
        comparison["improvements"]["f1_score"] >= 0 and
        comparison["improvements"]["rmse"] >= 0
    )
    
    logger.info(f"  - Baseline Accuracy: {baseline_metrics['accuracy']:.2%}")
    logger.info(f"  - New Model Accuracy: {metrics['overall_score']:.2%}")
    logger.info(f"  - Improvement: {accuracy_improvement:+.2%}")
    logger.info(f"  - Is Better: {comparison['is_better']}")
    
    return comparison


def save_model_artifacts(model_data: Dict[str, Any], bucket: str, date_prefix: str) -> str:
    """
    Mô phỏng save model artifacts lên S3.
    
    Args:
        model_data: Model data và metadata
        bucket: S3 bucket name
        date_prefix: Date prefix
        
    Returns:
        S3 key của model artifacts
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"artifacts/{date_prefix}/models/model_{timestamp}.pkl"
    
    logger.info(f"Saving model artifacts to s3://{bucket}/{s3_key}")
    
    return s3_key


def register_model(
    model_s3_key: str,
    metrics: Dict[str, Any],
    hyperparameters: Dict[str, Any],
    comparison: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Register model vào Model Registry nếu model tốt hơn baseline.
    
    Args:
        model_s3_key: S3 key của model artifacts
        metrics: Model evaluation metrics
        hyperparameters: Hyperparameters used
        comparison: Comparison với baseline
        
    Returns:
        Model registry entry nếu registered, None nếu không
    """
    registry_enabled = os.getenv("MODEL_REGISTRY_ENABLED", "true").lower() == "true"
    
    if not registry_enabled:
        logger.info("Model registry is disabled, skipping registration")
        return None
    
    if not comparison["is_better"]:
        logger.warning("⚠️  Model không tốt hơn baseline, không register")
        return None
    
    logger.info("Registering model to Model Registry...")
    
    # Mô phỏng model registry
    # Trong thực tế, có thể là MLflow, S3-based registry, hoặc database
    model_version = "v1.2.3"  # Auto-increment từ registry
    registry_entry = {
        "model_version": model_version,
        "model_s3_key": model_s3_key,
        "metrics": metrics,
        "hyperparameters": hyperparameters,
        "training_timestamp": datetime.utcnow().isoformat(),
        "status": "production-ready",  # hoặc "staging"
        "comparison": comparison,
        "registered_by": "ml-training-pipeline",
        "notes": f"Model improved accuracy by {comparison['improvements']['accuracy']:.2%}"
    }
    
    # Mô phỏng save registry entry
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    registry_s3_key = f"artifacts/model_registry/{model_version}/metadata.json"
    
    logger.info(f"✅ Model registered successfully!")
    logger.info(f"   - Version: {model_version}")
    logger.info(f"   - Status: {registry_entry['status']}")
    logger.info(f"   - Registry entry: s3://{bucket}/{registry_s3_key}")
    
    return registry_entry


def main():
    """Main entry point for training component."""
    logger.info("=" * 60)
    logger.info("Train Component - Starting")
    logger.info("=" * 60)
    
    # Get configuration
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    artifacts_prefix = os.getenv("S3_ARTIFACTS_PREFIX", "artifacts")
    component_name = os.getenv("COMPONENT_NAME", "train")
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Parse hyperparameters
    hyperparams_str = os.getenv("HYPERPARAMETERS", '{"learning_rate": 0.001, "batch_size": 32, "epochs": 10}')
    try:
        hyperparameters = json.loads(hyperparams_str)
    except json.JSONDecodeError:
        logger.warning("Invalid hyperparameters JSON, using defaults")
        hyperparameters = {"learning_rate": 0.001, "batch_size": 32, "epochs": 10}
    
    # Parse baseline metrics
    baseline_str = os.getenv("BASELINE_METRICS", '{"accuracy": 0.82, "f1_score": 0.80, "rmse": 0.38}')
    try:
        baseline_metrics = json.loads(baseline_str)
    except json.JSONDecodeError:
        baseline_metrics = None
    
    logger.info(f"Component: {component_name}")
    logger.info(f"S3 Bucket: {bucket}")
    logger.info(f"Date Prefix: {date_prefix}")
    logger.info(f"Hyperparameters: {hyperparameters}")
    
    # Step 1: Load processed data
    processed_data = load_processed_data(bucket, date_prefix)
    
    # Step 2: Split data
    data_splits = split_data(processed_data)
    
    # Step 3: Train model
    training_results = train_model(processed_data, hyperparameters)
    
    # Step 4: Evaluate model
    metrics = evaluate_model(training_results)
    
    # Step 5: Compare with baseline
    comparison = compare_with_baseline(metrics, baseline_metrics)
    
    # Step 6: Save model artifacts
    model_s3_key = save_model_artifacts(training_results, bucket, date_prefix)
    
    # Step 7: Register model nếu tốt hơn baseline
    registry_entry = register_model(model_s3_key, metrics, hyperparameters, comparison)
    
    # Generate training report
    report = {
        "training_date": datetime.utcnow().isoformat(),
        "component": component_name,
        "data_source": processed_data["s3_key"],
        "data_splits": data_splits,
        "hyperparameters": hyperparameters,
        "training_results": training_results,
        "metrics": metrics,
        "comparison": comparison,
        "model_s3_key": model_s3_key,
        "model_registered": registry_entry is not None,
        "registry_entry": registry_entry
    }
    
    logger.info("=" * 60)
    logger.info("Train Component - Completed")
    logger.info(f"✅ Model artifacts: s3://{bucket}/{model_s3_key}")
    if registry_entry:
        logger.info(f"✅ Model registered: {registry_entry['model_version']} ({registry_entry['status']})")
    else:
        logger.info("ℹ️  Model not registered (not better than baseline)")
    logger.info("=" * 60)
    
    return report


if __name__ == "__main__":
    main()