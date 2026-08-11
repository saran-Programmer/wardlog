import jwt
from fastapi import Header, HTTPException

from graph.config import DoctorContext

_CLAIM_TO_FIELD = {
    "sub": "id",
    "name": "name",
    "age": "age",
    "sex": "sex",
    "tone": "tone",
    "assistantName": "assistant_name",
}


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    return token


def get_doctor_context(authorization: str | None = Header(default=None)) -> DoctorContext:
    # The gateway has already validated this token's signature and expiry — anything that
    # reaches this service is trusted. We decode without verification purely to read the
    # claims. This is only safe because the service is not publicly reachable; if that ever
    # changes, signature verification must be turned back on here.
    token = _extract_token(authorization)
    claims = jwt.decode(token, options={"verify_signature": False})

    fields = {field: claims[claim] for claim, field in _CLAIM_TO_FIELD.items() if claim in claims}
    # rush is not in the token — the endpoint fills it in per request.
    return DoctorContext(**fields, rush=False)
