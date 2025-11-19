"""
Data EDA Component - MLOps Daily Pipeline

Mục đích:
    Thực hiện Exploratory Data Analysis (EDA) trên processed data để hiểu rõ dữ liệu,
    phát hiện patterns, anomalies, và generate insights cho data scientists.

Workflow:
    1. Load processed data từ S3 processed/{date}/ prefix
    2. Statistical analysis: descriptive statistics, distributions
    3. Correlation analysis: feature correlations, multicollinearity
    4. Visualization: generate charts và plots
    5. Anomaly detection: identify outliers và unusual patterns
    6. Generate EDA report (HTML/PDF) và save lên S3
    7. Save visualizations và statistics

Input:
    - Processed data từ S3: s3://{bucket}/processed/{date}/processed_data_*.parquet

Output:
    - EDA report: s3://{bucket}/eda/{date}/eda_report_{timestamp}.html
    - Visualizations: s3://{bucket}/eda/{date}/visualizations/*.png
    - Statistics: s3://{bucket}/eda/{date}/statistics.json
    - Summary: s3://{bucket}/eda/{date}/summary.json

Environment Variables:
    - S3_DATA_LAKE_BUCKET: S3 bucket name for data lake
    - LOG_LEVEL: Logging level

Example:
    python -m src.main
    
    Output:
    - s3://ml-fashion-data-lake/eda/2025-01-15/eda_report_20250115_020000.html
    - s3://ml-fashion-data-lake/eda/2025-01-15/statistics.json

MLOps Integration:
    - Chạy song song với data processing trong Argo Workflow
    - Generate reports để data scientists review
    - Alert nếu phát hiện data drift hoặc anomalies nghiêm trọng
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

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
        "features": [
            "user_id", "item_id", "rating", "timestamp", "category", "price",
            "price_normalized", "category_encoded", "user_activity_score", "item_popularity_score"
        ]
    }


def compute_statistics(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng tính toán statistical summary.
    
    Args:
        data: Processed data metadata
        
    Returns:
        Statistical summary
    """
    logger.info("Computing statistical summary...")
    
    stats = {
        "total_records": data["record_count"],
        "total_features": len(data["features"]),
        "numeric_features": {
            "rating": {
                "mean": 4.2,
                "std": 0.8,
                "min": 1.0,
                "max": 5.0,
                "median": 4.3
            },
            "price": {
                "mean": 45.5,
                "std": 15.2,
                "min": 10.0,
                "max": 200.0,
                "median": 42.0
            }
        },
        "categorical_features": {
            "category": {
                "unique_values": 15,
                "most_common": "clothing",
                "distribution": {"clothing": 0.35, "shoes": 0.25, "accessories": 0.40}
            }
        }
    }
    
    logger.info(f"  - Total records: {stats['total_records']}")
    logger.info(f"  - Numeric features: {len(stats['numeric_features'])}")
    logger.info(f"  - Categorical features: {len(stats['categorical_features'])}")
    
    return stats


def analyze_correlations(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng correlation analysis.
    
    Args:
        data: Processed data metadata
        
    Returns:
        Correlation analysis results
    """
    logger.info("Analyzing feature correlations...")
    
    correlations = {
        "high_correlations": [
            {"feature1": "price", "feature2": "price_normalized", "correlation": 0.95},
            {"feature1": "user_activity_score", "feature2": "rating", "correlation": 0.72}
        ],
        "multicollinearity": False,
        "recommendations": [
            "Consider removing price_normalized (highly correlated with price)",
            "user_activity_score và rating có correlation tốt cho model"
        ]
    }
    
    logger.info(f"  - High correlations found: {len(correlations['high_correlations'])}")
    logger.info(f"  - Multicollinearity detected: {correlations['multicollinearity']}")
    
    return correlations


def detect_anomalies(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng anomaly detection.
    
    Args:
        data: Processed data metadata
        
    Returns:
        Anomaly detection results
    """
    logger.info("Detecting anomalies...")
    
    anomalies = {
        "outliers_detected": 45,
        "outlier_rate": 0.0047,  # 0.47%
        "anomaly_types": {
            "extreme_ratings": 12,
            "price_outliers": 23,
            "unusual_patterns": 10
        },
        "severity": "low",
        "action_required": False
    }
    
    logger.info(f"  - Outliers detected: {anomalies['outliers_detected']} ({anomalies['outlier_rate']:.2%})")
    logger.info(f"  - Severity: {anomalies['severity']}")
    
    if anomalies["outlier_rate"] > 0.05:  # > 5%
        logger.warning("⚠️  High outlier rate detected!")
        anomalies["action_required"] = True
    
    return anomalies


def generate_visualizations(data: Dict[str, Any], date_prefix: str) -> List[str]:
    """
    Mô phỏng generate visualizations.
    
    Args:
        data: Processed data metadata
        date_prefix: Date prefix
        
    Returns:
        List of visualization file paths
    """
    logger.info("Generating visualizations...")
    
    visualizations = [
        f"eda/{date_prefix}/visualizations/distribution_rating.png",
        f"eda/{date_prefix}/visualizations/distribution_price.png",
        f"eda/{date_prefix}/visualizations/correlation_heatmap.png",
        f"eda/{date_prefix}/visualizations/category_distribution.png",
        f"eda/{date_prefix}/visualizations/time_series_analysis.png"
    ]
    
    logger.info(f"  - Generated {len(visualizations)} visualizations")
    
    return visualizations


def main():
    """Main entry point for data EDA component."""
    logger.info("=" * 60)
    logger.info("Data EDA Component - Starting")
    logger.info("=" * 60)
    
    # Get configuration
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    component_name = os.getenv("COMPONENT_NAME", "data_eda")
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    
    logger.info(f"Component: {component_name}")
    logger.info(f"S3 Bucket: {bucket}")
    logger.info(f"Date Prefix: {date_prefix}")
    
    # Step 1: Load processed data
    processed_data = load_processed_data(bucket, date_prefix)
    
    # Step 2: Compute statistics
    statistics = compute_statistics(processed_data)
    
    # Step 3: Analyze correlations
    correlations = analyze_correlations(processed_data)
    
    # Step 4: Detect anomalies
    anomalies = detect_anomalies(processed_data)
    
    # Step 5: Generate visualizations
    visualizations = generate_visualizations(processed_data, date_prefix)
    
    # Step 6: Generate summary report
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report = {
        "eda_date": datetime.utcnow().isoformat(),
        "component": component_name,
        "data_source": processed_data["s3_key"],
        "statistics": statistics,
        "correlations": correlations,
        "anomalies": anomalies,
        "visualizations": visualizations,
        "summary": {
            "data_quality": "good",
            "ready_for_training": True,
            "recommendations": correlations.get("recommendations", [])
        }
    }
    
    report_s3_key = f"eda/{date_prefix}/eda_report_{timestamp}.html"
    stats_s3_key = f"eda/{date_prefix}/statistics_{timestamp}.json"
    
    logger.info("=" * 60)
    logger.info("Data EDA Component - Completed")
    logger.info(f"✅ EDA Report: s3://{bucket}/{report_s3_key}")
    logger.info(f"✅ Statistics: s3://{bucket}/{stats_s3_key}")
    logger.info(f"📊 Summary:")
    logger.info(f"   - Data quality: {report['summary']['data_quality']}")
    logger.info(f"   - Ready for training: {report['summary']['ready_for_training']}")
    logger.info("=" * 60)
    
    return report


if __name__ == "__main__":
    main()