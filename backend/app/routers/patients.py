# backend/app/routers/patients.py
"""Patient dashboard endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..infrastructure.database import get_db
from ..domain.models.user import User
from ..core.deps import get_current_user
from ..services.dashboard import get_dashboard_stats

router = APIRouter()


@router.get("/dashboard")
async def dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return aggregated dashboard statistics for the current user."""
    stats = get_dashboard_stats(db, user_id=user.id)
    return stats
