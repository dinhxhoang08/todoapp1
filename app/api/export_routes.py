from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.services.export_service import ExportService
from app.models.user import User

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_csv(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ExportService(db)
    csv_data = svc.export_tasks_csv(user.id)
    return StreamingResponse(
        iter([csv_data.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"},
    )


@router.get("/excel")
async def export_excel(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ExportService(db)
    excel_data = svc.export_tasks_excel(user.id)
    return StreamingResponse(
        iter([excel_data.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tasks.xlsx"},
    )
