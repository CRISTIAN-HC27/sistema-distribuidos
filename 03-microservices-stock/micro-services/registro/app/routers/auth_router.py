from fastapi import APIRouter # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from pydantic import BaseModel # type: ignore

import security # type: ignore
from services.registro_service import EmailYaExiste, registrar

router = APIRouter()


class RegistroBody(BaseModel):
    email: str
    contrasena: str


@router.post("/registro")
def hacer_registro(body: RegistroBody):
    email = security.normalizar_email(body.email)

    if not security.email_valido(email):
        return JSONResponse(status_code=400, content={"error": "email inválido"})

    error_pw = security.validar_contrasena(body.contrasena)
    if error_pw:
        return JSONResponse(status_code=400, content={"error": error_pw})

    try:
        usuario = registrar(email, body.contrasena)
    except EmailYaExiste:
        return JSONResponse(
            status_code=409,
            content={"error": "ya existe una cuenta con ese email"},
        )

    return JSONResponse(
        status_code=201,
        content={"ok": True, "email": usuario["email"]},
    )