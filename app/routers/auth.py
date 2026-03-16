"""
Router de autenticación
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.auth import Token, LoginRequest, ChangePasswordRequest
from app.schemas.usuarios import UsuarioMeResponse
from app.services.auth_service import AuthService
from app.db.models.usuarios import Usuario

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login
    
    - **usuario**: Nombre de usuario
    - **contrasenia**: Contraseña
    
    Returns JWT access token
    """
    # Autenticar usuario
    user = AuthService.authenticate_user(
        db=db,
        usuario=login_data.usuario,
        contrasenia=login_data.contrasenia
    )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.usuario_id,
            "usuario": user.usuario,
            "perfil_id": user.perfil_id
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": user.usuario_id,
        "usuario": user.usuario,
        "nombre": user.empleado.nombre if user.empleado else user.usuario,
        "perfil_id": user.perfil_id,
    }


@router.post("/login-form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint de login compatible con OAuth2PasswordRequestForm
    Para usar con herramientas que esperan este formato
    """
    user = AuthService.authenticate_user(
        db=db,
        usuario=form_data.username,
        contrasenia=form_data.password
    )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.usuario_id,
            "usuario": user.usuario,
            "perfil_id": user.perfil_id
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioMeResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener información del usuario actual
    """
    return UsuarioMeResponse(
        usuario_id=current_user.usuario_id,
        usuario=current_user.usuario,
        perfil_id=current_user.perfil_id,
        estado_id=current_user.estado_id,
        empleado_id=current_user.empleado_id,
        intentos=current_user.intentos,
        empleado_nombre=current_user.empleado.nombre if current_user.empleado else None,
        perfil_descripcion=current_user.perfil.descripcion if current_user.perfil else None
    )


@router.post("/change-password")
async def change_password(
    change_password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario actual
    """
    AuthService.change_password(
        db=db,
        usuario_id=current_user.usuario_id,
        contrasenia_actual=change_password_data.contrasenia_actual,
        contrasenia_nueva=change_password_data.contrasenia_nueva
    )
    
    return {"message": "Contraseña actualizada exitosamente"}


@router.post("/reset-attempts/{usuario_id}")
async def reset_attempts(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Resetear intentos de login de un usuario (solo para admins)
    TODO: Agregar validación de rol admin
    """
    AuthService.reset_login_attempts(db=db, usuario_id=usuario_id)
    return {"message": "Intentos de login reseteados"}
