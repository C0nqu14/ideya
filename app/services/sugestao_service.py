from app.repositories.airtable_repo import AirtableRepository, airtable_repo
from app.schemas.ideya import CriarIdeyaOut, CriarIdeyaRequest, LocalOut


class SugestaoService:
    def __init__(self, repository: AirtableRepository) -> None:
        self._repository = repository

    def listar_locais(self) -> list[LocalOut]:
        return self._repository.listar_locais_validados()

    def obter_opcoes(self, pedido: CriarIdeyaRequest) -> CriarIdeyaOut:
        valor_por_pessoa = pedido.orcamento_total // pedido.num_pessoas
        zona = (pedido.zona or "").strip() or None
        categoria = pedido.categoria.value if pedido.categoria else None
        locais = self._repository.filtrar_locais(
            preco_maximo_pessoa=valor_por_pessoa,
            zona=zona,
            categoria=categoria,
        )
        return CriarIdeyaOut(
            orcamento_total=pedido.orcamento_total,
            num_pessoas=pedido.num_pessoas,
            valor_por_pessoa=valor_por_pessoa,
            total_locais=len(locais),
            locais=locais,
        )


sugestao_service = SugestaoService(airtable_repo)
