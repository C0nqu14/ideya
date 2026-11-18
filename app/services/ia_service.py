import json
from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.schemas.ideya import CriarIdeyaRequest, LocalOut, SurpreendaMeOut

_LUANDA = ZoneInfo("Africa/Luanda")
_DIAS_DA_SEMANA = (
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
)
_FERIADOS_ANGOLA = {
    (1, 1): "Dia de Ano Novo",
    (2, 4): "Dia do Início da Luta Armada de Libertação Nacional",
    (4, 4): "Dia da Paz e da Reconciliação Nacional",
    (9, 17): "Dia do Fundador da Nação e do Herói Nacional",
    (11, 11): "Dia da Independência Nacional",
    (12, 25): "Dia de Natal",
}


def _analisar_contexto_temporal(dt: datetime) -> str:
    data_hora_luanda = (
        dt.replace(tzinfo=_LUANDA)
        if dt.tzinfo is None
        else dt.astimezone(_LUANDA)
    )
    hora = data_hora_luanda.hour
    if 6 <= hora < 12:
        turno = "Manhã"
    elif 12 <= hora < 18:
        turno = "Horário de Almoço/Tarde"
    elif 18 <= hora < 23:
        turno = "Jantar/Noite"
    else:
        turno = "Madrugada"

    feriado = _FERIADOS_ANGOLA.get(
        (data_hora_luanda.month, data_hora_luanda.day)
    )
    contexto_feriado = feriado or "Não coincide com um dos feriados nacionais fixos considerados"
    return (
        f"Data: {data_hora_luanda:%d/%m/%Y}; "
        f"hora local: {data_hora_luanda:%H:%M} (Africa/Luanda); "
        f"dia da semana: {_DIAS_DA_SEMANA[data_hora_luanda.weekday()]}; "
        f"turno: {turno}; feriado: {contexto_feriado}."
    )


class _GeminiSelection(BaseModel):
    local_id: str
    justificativa: str


class IASugestaoService:
    def sugerir(
        self,
        pedido: CriarIdeyaRequest,
        locais: list[LocalOut],
    ) -> SurpreendaMeOut:
        if not locais:
            raise ValueError("Não existem locais compatíveis para surpreender o grupo.")

        api_key = get_settings().gemini_api_key
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY tem de estar configurada.")

        client = genai.Client(api_key=api_key)
        candidate_data = [
            {
                "id": local.id,
                "nome": local.nome,
                "categoria": local.categoria.value,
                "zona": local.zona,
                "preco_medio_pessoa": local.preco_medio_pessoa,
                "notas_rapidas": local.notas_rapidas,
            }
            for local in locais
        ]
        data_hora = pedido.data_hora or datetime.now(_LUANDA)
        contexto_temporal = _analisar_contexto_temporal(data_hora)
        valor_por_pessoa = pedido.orcamento_total // pedido.num_pessoas
        zona = (pedido.zona or "").strip() or "sem preferência"
        prompt = (
            "Escolhe o local MAIS ADEQUADO para este grupo, horário e ocasião. "
            "Responde em português de Angola, com uma justificativa natural, "
            "entusiasta e direta. Escolhe exclusivamente um id da lista fornecida. "
            "Não inventes locais, eventos, horários de funcionamento ou "
            "disponibilidade.\n"
            f"Orçamento total: {pedido.orcamento_total} Kz\n"
            f"Orçamento por pessoa: {valor_por_pessoa} Kz\n"
            f"Número de pessoas: {pedido.num_pessoas}\n"
            f"Zona preferida: {zona}\n"
            f"Contexto temporal: {contexto_temporal}\n"
            "Usa o horário para adequar a recomendação: às 00h, prioriza "
            "bares, discotecas ou festas/eventos se existirem na lista; às 12h, "
            "considera restaurantes, praias ou espaços ao ar livre. Em feriados, "
            "como 11 de Novembro, destaca o clima de celebração em Luanda. "
            "Se nenhum local disponível parecer adequado ao horário, escolhe a "
            "melhor alternativa possível e explica isso educadamente na "
            "justificativa, recomendando confirmar o horário de funcionamento.\n"
            f"Locais candidatos: {json.dumps(candidate_data, ensure_ascii=False)}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": _GeminiSelection,
            },
        )

        response_text = response.text
        if not response_text:
            raise ValueError("O Gemini devolveu uma resposta vazia.")
        try:
            selection = _GeminiSelection.model_validate_json(response_text)
        except ValidationError as exc:
            raise ValueError("O Gemini devolveu uma resposta inválida.") from exc

        selected_local = next(
            (local for local in locais if local.id == selection.local_id),
            None,
        )
        if selected_local is None:
            raise ValueError("O Gemini selecionou um local fora da lista candidata.")
        return SurpreendaMeOut(
            local=selected_local,
            justificativa=selection.justificativa,
        )


ia_service = IASugestaoService()
