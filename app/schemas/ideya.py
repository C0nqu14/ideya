from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoriaEnum(str, Enum):
    BARES = "Bares"
    RESTAURANTES = "Restaurantes"
    PRAIA = "Praia"
    AR_LIVRE = "Ar Livre"
    CULTURA = "Cultura"
    FESTAS_EVENTOS = "Festas/Eventos"
    CINEMA = "Cinema"
    FAST_FOOD = "Fast Food"
    HAMBURGUERIA = "Fast Food"

    @classmethod
    def _missing_(cls, value: object) -> "CategoriaEnum | None":
        if isinstance(value, str) and value.strip().casefold() in {
            "hamburgueria",
            "hambuegueria",
        }:
            return cls.FAST_FOOD
        return None


class LocalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    categoria: CategoriaEnum
    zona: str
    preco_medio_pessoa: int
    latitude: float | None = None
    longitude: float | None = None
    fotos: list[str] = Field(default_factory=list)
    notas_rapidas: str | None = None
    descricao: str | None = None


class CriarIdeyaRequest(BaseModel):
    orcamento_total: int = Field(..., gt=0)
    num_pessoas: int = Field(..., gt=0)
    zona: Optional[str] = None
    categoria: Optional[CategoriaEnum] = None
    data_hora: Optional[datetime] = Field(
        None,
        description="Data e hora desejada para a saída. Se vazio, usa a hora atual de Luanda.",
    )


class CriarIdeyaOut(BaseModel):
    orcamento_total: int
    num_pessoas: int
    valor_por_pessoa: int
    total_locais: int
    locais: List[LocalOut]


class SurpreendaMeOut(BaseModel):
    local: LocalOut
    justificativa: str
