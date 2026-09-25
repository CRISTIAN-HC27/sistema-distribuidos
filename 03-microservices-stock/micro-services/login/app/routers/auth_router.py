from fastapi import APIRouter # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from pydantic import BaseModel # type: ignore

import security # type: ignore
from services.login_service import CredencialesInvalidas, autenticar

router = APIRouter()


class LoginBody(BaseModel):
    email: str
    contrasena: str


@router.post("/login")
def hacer_login(body: LoginBody):
    email = security.normalizar_email(body.email)

    if not security.email_valido(email):
        return JSONResponse(status_code=400, content={"error": "email inválido"})

    try:
        usuario = autenticar(email, body.contrasena)
    except CredencialesInvalidas:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "error": "correo o contraseña incorrectos"},
        )

    return JSONResponse(
        status_code=200,
        content={"ok": True, "email": usuario["email"]},
    )
