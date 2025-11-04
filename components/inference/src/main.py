"""
Dịch vụ Inference (FastAPI)

Mục đích:
- Cung cấp API kiểm tra sức khỏe và endpoint dự đoán mẫu để xác nhận triển khai.
- Có thể mở rộng để tải model từ S3 và phục vụ dự đoán thực tế.

Endpoints:
- GET /healthz: Kiểm tra tình trạng dịch vụ.
- POST /predict: Nhận payload mẫu và trả về kết quả mô phỏng.

Version: 1.0.1 - Updated for EKS deployment testing
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import os
from datetime import datetime


class PredictRequest(BaseModel):
    user_id: str
    item_ids: list[str]
    top_k: int = 5


app = FastAPI(title="HM Inference Service", version="1.0.1")


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "inference",
        "version": os.environ.get("APP_VERSION", "1.0.1"),
        "timestamp": datetime.utcnow().isoformat(),
        "deployed": True,
    }


@app.post("/predict")
def predict(req: PredictRequest) -> Dict[str, Any]:
    # Logic mô phỏng: trả về top_k item_ids đầu vào như là gợi ý
    recommendations = req.item_ids[: req.top_k]
    return {
        "user_id": req.user_id,
        "recommendations": recommendations,
        "count": len(recommendations),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=False)

