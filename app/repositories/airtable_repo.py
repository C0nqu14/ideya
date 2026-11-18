from typing import Any

from pyairtable import Api

from app.core.config import get_settings
from app.schemas.ideya import CategoriaEnum, LocalOut

VALIDATION_FIELD = "Status de Validação"
AIRTABLE_FIELDS = {
    "nome": "Nome do Lugar",
    "categoria": "Categoria",
    "zona": "Zona de Luanda",
    "preco_medio_pessoa": "Preço Médio por Pessoa",
    "fotos": "Fotos do Local",
    "latitude": "Coordenadas Latitude",
    "longitude": "Coordenadas Longitude",
    "notas_rapidas": "Notas Rápidas",
}


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _photo_urls(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [
        item["url"]
        for item in value
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    ]


def _to_local(record: dict[str, Any]) -> LocalOut:
    fields = record["fields"]
    return LocalOut(
        id=record["id"],
        nome=fields[AIRTABLE_FIELDS["nome"]],
        categoria=CategoriaEnum(fields[AIRTABLE_FIELDS["categoria"]]),
        zona=fields[AIRTABLE_FIELDS["zona"]],
        preco_medio_pessoa=int(fields[AIRTABLE_FIELDS["preco_medio_pessoa"]]),
        latitude=_optional_float(fields.get(AIRTABLE_FIELDS["latitude"])),
        longitude=_optional_float(fields.get(AIRTABLE_FIELDS["longitude"])),
        fotos=_photo_urls(fields.get(AIRTABLE_FIELDS["fotos"])),
        notas_rapidas=fields.get(AIRTABLE_FIELDS["notas_rapidas"]),
    )


class AirtableRepository:
    def _table(self) -> Any:
        settings = get_settings()
        if not settings.airtable_api_key or not settings.airtable_base_id:
            raise RuntimeError(
                "AIRTABLE_API_KEY e AIRTABLE_BASE_ID têm de estar configurados."
            )
        return Api(settings.airtable_api_key).table(
            settings.airtable_base_id,
            settings.airtable_table_name,
        )

    def listar_locais_validados(self) -> list[LocalOut]:
        records = self._table().all(
            formula=f"{{{VALIDATION_FIELD}}}='Validado'"
        )
        return [_to_local(record) for record in records]

    def filtrar_locais(
        self,
        preco_maximo_pessoa: int,
        zona: str | None = None,
        categoria: str | None = None,
    ) -> list[LocalOut]:
        locais = self.listar_locais_validados()
        zona_filtro = zona.strip().casefold() if zona and zona.strip() else None
        categoria_filtro = (
            categoria.strip().casefold()
            if categoria and categoria.strip()
            else None
        )

        return [
            local
            for local in locais
            if local.preco_medio_pessoa <= preco_maximo_pessoa
            and (zona_filtro is None or local.zona.casefold() == zona_filtro)
            and (
                categoria_filtro is None
                or local.categoria.value.casefold() == categoria_filtro
            )
        ]


airtable_repo = AirtableRepository()
