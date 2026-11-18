from fastapi import APIRouter, HTTPException
from google.genai.errors import APIError

from app.schemas.ideya import (
    CriarIdeyaOut,
    CriarIdeyaRequest,
    LocalOut,
    SurpreendaMeOut,
)
from app.services.ia_service import ia_service
from app.services.sugestao_service import sugestao_service

router = APIRouter()


@router.get("/locais", response_model=list[LocalOut])
def listar_locais() -> list[LocalOut]:
    try:
        return sugestao_service.listar_locais()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/criar-ideya", response_model=CriarIdeyaOut)
def criar_ideya(pedido: CriarIdeyaRequest) -> CriarIdeyaOut:
    try:
        return sugestao_service.obter_opcoes(pedido)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/surpreenda-me", response_model=SurpreendaMeOut)
def surpreenda_me(pedido: CriarIdeyaRequest) -> SurpreendaMeOut:
    try:
        resultado = sugestao_service.obter_opcoes(pedido)
        if not resultado.locais:
            raise HTTPException(
                status_code=404,
                detail="Não foram encontrados locais compatíveis.",
            )
        return ia_service.sugerir(pedido, resultado.locais)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(
            status_code=502,
            detail="Não foi possível obter uma recomendação do Gemini.",
        ) from exc
