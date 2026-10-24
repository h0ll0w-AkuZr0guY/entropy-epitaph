"""
Extinction archive router — the 消逝档案.

The archive itself loses pages over time: certificates whose own
entropy exceeds a threshold are hidden (archived=True), so even
the proof of extinction eventually disappears.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import ExtinctionCertificate
from backend.schemas import CertificateOut, ArchiveEntryOut

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("", response_model=list[ArchiveEntryOut])
@router.get("/", response_model=list[ArchiveEntryOut])
async def list_archive(db: AsyncSession = Depends(get_db)):
    """
    The 消逝档案 — minimal entries: index + certificate id + time.
    Archived (faded-out) certificates are excluded: the archive forgets.
    """
    result = await db.execute(
        select(ExtinctionCertificate)
        .where(ExtinctionCertificate.archived.is_(False))
        .order_by(ExtinctionCertificate.created_at.asc())
    )
    certs = result.scalars().all()
    return [
        ArchiveEntryOut(
            index=idx + 1,
            cert_id=c.cert_id,
            created_at=c.created_at,
            entropy_score=round(c.entropy_score, 4),
        )
        for idx, c in enumerate(certs)
    ]


@router.get("/{cert_id}", response_model=CertificateOut)
async def get_certificate(cert_id: str, db: AsyncSession = Depends(get_db)):
    cert = await db.get(ExtinctionCertificate, cert_id)
    if not cert or cert.archived:
        raise HTTPException(404, "此凭证已不可考——连它曾经存在过的证明也消失了。")
    return CertificateOut.model_validate(cert)
