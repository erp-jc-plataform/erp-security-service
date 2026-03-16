"""
Schemas para autenticación
"""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Request para login"""
    usuario: str
    contrasenia: str


class Token(BaseModel):
    """Response de token JWT"""
    access_token: str
    token_type: str = "bearer"
    usuario_id: Optional[int] = None
    usuario: Optional[str] = None
    nombre: Optional[str] = None
    perfil_id: Optional[int] = None


class TokenData(BaseModel):
    """Datos dentro del token"""
    usuario_id: Optional[int] = None
    usuario: Optional[str] = None
    perfil_id: Optional[int] = None


class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña"""
    contrasenia_actual: str
    contrasenia_nueva: str
