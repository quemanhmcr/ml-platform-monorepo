"""
Data Ingestion Component - MLOps Daily Pipeline

Mục đích:
    Thu thập dữ liệu raw từ nhiều nguồn (APIs, databases, files) và lưu vào S3 data lake.
    Đây là bước đầu tiên trong ML pipeline, chạy hàng ngày để cập nhật dữ liệu mới nhất.

Workflow:
    1. Kết nối với data sources (APIs, databases)
    2. Extract raw data từ các nguồn
    3. Validate data format và schema cơ bản
    4. Upload raw data lên S3 bucket tại prefix raw/{date}/
    5. Ghi log metadata về data ingestion (số lượng records, timestamp)

Input:
    - Data sources: External APIs, databases, file systems
    - Config: S3 bucket name, data source credentials

Output:
    - Raw data files trong S3: s3://{bucket}/raw/{date}/{source}_{timestamp}.parquet
    - Metadata log: s3://{bucket}/raw/{date}/metadata.json

Environment Variables:
    - S3_DATA_LAKE_BUCKET: S3 bucket name for data lake
    - DATA_SOURCE_CONFIG: JSON config for data sources
    - LOG_LEVEL: Logging level (INFO, DEBUG, ERROR)

Example:
    python -m src.main
    
    Output:
    - s3://ml-fashion-data-lake/raw/2025-01-15/api_fashion_20250115_020000.parquet
    - s3://ml-fashion-data-lake/raw/2025-01-15/db_users_20250115_020000.parquet
    - s3://ml-fashion-data-lake/raw/2025-01-15/metadata.json

MLOps Integration:
    - Chạy tự động hàng ngày qua Argo CronWorkflow
    - Trigger data processing step sau khi ingestion hoàn thành
    - Monitor data quality và alert nếu có anomalies
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ingest_data_from_source(source_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mô phỏng việc ingest data từ một source.
    
    Args:
        source_name: Tên của data source (e.g., 'api_fashion', 'db_users')
        config: Configuration cho data source
        
    Returns:
        Dict chứa metadata về data đã ingest
    """
    logger.info(f"Starting data ingestion from source: {source_name}")
    
    # Mô phỏng: Giả sử đã fetch được data
    record_count = 1000  # Simulated record count
    timestamp = datetime.utcnow().isoformat()
    
    # Mô phỏng upload lên S3
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    date_prefix = datetime.utcnow().strftime("%Y-%m-%d")
    s3_key = f"raw/{date_prefix}/{source_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
    
    logger.info(f"Simulated upload to s3://{bucket}/{s3_key}")
    logger.info(f"Records ingested: {record_count}")
    
    return {
        "source": source_name,
        "record_count": record_count,
        "s3_bucket": bucket,
        "s3_key": s3_key,
        "timestamp": timestamp,
        "status": "success"
    }


def main():
    """Main entry point for data ingestion component."""
    logger.info("=" * 60)
    logger.info("Data Ingestion Component - Starting")
    logger.info("=" * 60)
    
    # Get configuration
    bucket = os.getenv("S3_DATA_LAKE_BUCKET", "ml-fashion-data-lake")
    component_name = os.getenv("COMPONENT_NAME", "data_ingestion")
    
    logger.info(f"Component: {component_name}")
    logger.info(f"S3 Bucket: {bucket}")
    
    # Mô phỏng ingest từ nhiều sources
    sources = [
        {"name": "api_fashion", "type": "rest_api"},
        {"name": "db_users", "type": "database"},
        {"name": "file_products", "type": "file_system"}
    ]
    
    results = []
    for source in sources:
        try:
            result = ingest_data_from_source(source["name"], source)
            results.append(result)
            logger.info(f"✅ Successfully ingested from {source['name']}")
        except Exception as e:
            logger.error(f"❌ Failed to ingest from {source['name']}: {str(e)}")
            results.append({
                "source": source["name"],
                "status": "failed",
                "error": str(e)
            })
    
    # Mô phỏng lưu metadata
    metadata = {
        "ingestion_date": datetime.utcnow().isoformat(),
        "component": component_name,
        "sources": results,
        "total_records": sum(r.get("record_count", 0) for r in results if r.get("status") == "success")
    }
    
    logger.info(f"📊 Ingestion Summary:")
    logger.info(f"   - Total sources: {len(sources)}")
    logger.info(f"   - Successful: {sum(1 for r in results if r.get('status') == 'success')}")
    logger.info(f"   - Total records: {metadata['total_records']}")
    
    logger.info("=" * 60)
    logger.info("Data Ingestion Component - Completed")
    logger.info("=" * 60)
    
    return metadata


if __name__ == "__main__":
    main()