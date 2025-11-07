"""
Data Processing Component - MLOps Daily Pipeline

Mục đích:
    Xử lý và làm sạch dữ liệu raw từ S3, transform sang format chuẩn cho training.
    Bao gồm: data cleaning, feature engineering, data validation, và normalization.

Workflow:
    1. Load raw data từ S3 raw/{date}/ prefix
    2. Data cleaning: xử lý missing values, outliers, duplicates
    3. Feature engineering: tạo features mới, encode categorical variables
    4. Data validation: kiểm tra data quality, schema validation
    5. Normalization/Standardization: chuẩn hóa dữ liệu
    6. Save processed data lên S3 processed/{date}/ prefix
    7. Generate data quality report

Input:
    - Raw data từ S3: s3://{bucket}/raw/{date}/*.parquet
    - Processing config: feature definitions, validation rules

Output:
    - Processed data: s3://{bucket}/processed/{date}/processed_data_{timestamp}.parquet
    - Data quality report: s3://{bucket}/processed/{date}/quality_report.json
    - Feature statistics: s3://{bucket}/processed/{date}/feature_stats.json

Environment Variables:
    - S3_DATA_LAKE_BUCKET: S3 bucket name for data lake
    - S3_PROCESSED_PREFIX: Prefix for processed data (default: processed)
    - PROCESSING_CONFIG: JSON config for processing rules
    - LOG_LEVEL: Logging level

Example:
    python -m src.main
    
    Output:
    - s3://ml-fashion-data-lake/processed/2025-01-15/processed_data_20250115_020000.parquet
    - s3://ml-fashion-data-lake/processed/2025-01-15/quality_report.json

MLOps Integration:
    - Chạy sau data ingestion step trong Argo Workflow
    - Validate data quality trước khi chuyển sang training
    - Alert nếu data quality không đạt threshold
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


def load_raw_data(bucket: str, date_prefix: str) -> Dict[str, Any]:
    """
    Mô phỏng load raw data từ S3.
    
    Args:
        bucket: S3 bucket name
        date_prefix: Date prefix (YYYY-MM-DD)
        
    Returns:
        Dict chứa raw data metadata
    """
    logger.info(f"Loading raw data from s3://{bucket}/raw/{date_prefix}/")
    
    # Mô phỏng: Giả sử đã load được data
    return {
        "files": [
            f"raw/{date_prefix}/api_fashion_20250115_020000.parquet",
            f"raw/{date_prefix}/db_users_20250115_020000.parquet",
            f"raw/{date_prefix}/file_products_20250115_020000.parquet"
        ],
        "total_records": 10000,
        "columns": ["user_id", "item_id", "rating", "timestamp", "category", "price"]
    }


def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng data cleaning process.
    
    Args:
        data: Raw data metadata
        
    Returns:
        Cleaned data metadata
    """
    logger.info("Starting data cleaning...")
    
    # Mô phỏng cleaning operations
    original_count = data["total_records"]
    removed_duplicates = int(original_count * 0.05)  # 5% duplicates
    removed_missing = int(original_count * 0.02)  # 2% missing values
    cleaned_count = original_count - removed_duplicates - removed_missing
    
    logger.info(f"  - Original records: {original_count}")
    logger.info(f"  - Removed duplicates: {removed_duplicates}")
    logger.info(f"  - Removed missing: {removed_missing}")
    logger.info(f"  - Cleaned records: {cleaned_count}")
    
    return {
        **data,
        "total_records": cleaned_count,
        "cleaning_stats": {
            "duplicates_removed": removed_duplicates,
            "missing_removed": removed_missing,
            "cleaning_rate": cleaned_count / original_count
        }
    }


def engineer_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng feature engineering process.
    
    Args:
        data: Cleaned data metadata
        
    Returns:
        Data với engineered features
    """
    logger.info("Starting feature engineering...")
    
    # Mô phỏng feature engineering
    engineered_features = [
        "user_id",
        "item_id",
        "rating",
        "timestamp",
        "category",
        "price",
        "price_normalized",  # New feature
        "category_encoded",  # New feature
        "user_activity_score",  # New feature
        "item_popularity_score"  # New feature
    ]
    
    logger.info(f"  - Original features: {len(data['columns'])}")
    logger.info(f"  - Engineered features: {len(engineered_features)}")
    logger.info(f"  - New features: {len(engineered_features) - len(data['columns'])}")
    
    return {
        **data,
        "columns": engineered_features,
        "feature_engineering": {
            "new_features": engineered_features[len(data['columns']):],
            "transformation_applied": True
        }
    }


def validate_data_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng data quality validation.
    
    Args:
        data: Processed data metadata
        
    Returns:
        Quality report
    """
    logger.info("Validating data quality...")
    
    # Mô phỏng quality checks
    quality_report = {
        "schema_valid": True,
        "completeness": 0.98,
        "consistency": 0.95,
        "accuracy": 0.97,
        "overall_score": 0.97,
        "passed": True
    }
    
    logger.info(f"  - Schema valid: {quality_report['schema_valid']}")
    logger.info(f"  - Completeness: {quality_report['completeness']:.2%}")
    logger.info(f"  - Overall score: {quality_report['overall_score']:.2%}")
    
    if quality_report["overall_score"] < 0.90:
        logger.warning("⚠️  Data quality below threshold!")
        quality_report["passed"] = False
    
    return quality_report


def save_processed_data(data: Dict[str, Any], bucket: str, date_prefix: str) -> str:
    """
    Mô phỏng save processed data lên S3.
    
    Args:
        data: Processed data
        bucket: S3 bucket name
        date_prefix: Date prefix
        
    Returns:
        S3 key của processed data
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"processed/{date_prefix}/processed_data_{timestamp}.parquet"
    
    logger.info(f"Saving processed data to s3://{bucket}/{s3_key}")
    logger.info(f"  - Records: {data['total_records']}")
    logger.info(f"  - Features: {len(data['columns'])}")
    
    return s3_key


def main():
    """Main entry point for data processing component."""
    logger.info("=" * 60)
    logger.info("Data Processing Component - Starting")
    logger.info("=" * 60)
    
    # Get configuration
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    processed_prefix = os.getenv("S3_PROCESSED_PREFIX", "processed")
    component_name = os.getenv("COMPONENT_NAME", "data_processing")
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    
    logger.info(f"Component: {component_name}")
    logger.info(f"S3 Bucket: {bucket}")
    logger.info(f"Date Prefix: {date_prefix}")
    
    # Step 1: Load raw data
    raw_data = load_raw_data(bucket, date_prefix)
    
    # Step 2: Clean data
    cleaned_data = clean_data(raw_data)
    
    # Step 3: Engineer features
    processed_data = engineer_features(cleaned_data)
    
    # Step 4: Validate quality
    quality_report = validate_data_quality(processed_data)
    
    if not quality_report["passed"]:
        logger.error("❌ Data quality validation failed!")
        raise ValueError("Data quality below threshold")
    
    # Step 5: Save processed data
    s3_key = save_processed_data(processed_data, bucket, date_prefix)
    
    logger.info("=" * 60)
    logger.info("Data Processing Component - Completed")
    logger.info(f"✅ Processed data saved: s3://{bucket}/{s3_key}")
    logger.info("=" * 60)
    
    return {
        "status": "success",
        "s3_key": s3_key,
        "quality_report": quality_report,
        "processed_data": processed_data
    }


if __name__ == "__main__":
    main()