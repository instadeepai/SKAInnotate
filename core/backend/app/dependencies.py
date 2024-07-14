from typing import Callable
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse

def get_current_role(request: Request):
  role = request.session.get('current_role')
  if not role:
    raise HTTPException(
      status_code=status.HTTP_307_TEMPORARY_REDIRECT,
      headers={"Location": "/auth/login"}
    )
  return role

def role_required(required_role: str) -> Callable:
  def verify_role(role: str = Depends(get_current_role)):
    if role != required_role:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                          detail="Insufficient permissions")
    return role
  return verify_role
