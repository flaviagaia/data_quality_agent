from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from .sample_data import load_record


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_DIGITS_REGEX = re.compile(r"\D")


def get_record_context(record_id: str) -> dict[str, Any]:
    """Retorna o registro original consultado pelo agente."""
    return load_record(record_id)


def validate_record_fields(record_id: str) -> dict[str, Any]:
    """Executa validações básicas de completude e formato."""
    record = load_record(record_id)
    issues: list[str] = []

    email = str(record["email"])
    if not EMAIL_REGEX.match(email):
        issues.append("email_invalido")

    phone_digits = PHONE_DIGITS_REGEX.sub("", str(record["phone"]))
    if len(phone_digits) not in {10, 11}:
        issues.append("telefone_invalido")

    birth_date = str(record["birth_date"])
    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        issues.append("data_nascimento_invalida")

    if float(record["income_br"]) < 0:
        issues.append("renda_negativa")

    if not str(record["customer_name"]).strip():
        issues.append("nome_ausente")

    return {
        "record_id": record_id,
        "issue_count": len(issues),
        "issues": issues,
    }


def suggest_record_corrections(record_id: str) -> dict[str, Any]:
    """Propõe correções operacionais para os problemas encontrados."""
    record = load_record(record_id)
    validation = validate_record_fields(record_id)
    suggestions: list[str] = []

    if "email_invalido" in validation["issues"]:
        suggestions.append("solicitar confirmação ou correção manual do e-mail do cliente")
    if "telefone_invalido" in validation["issues"]:
        suggestions.append("normalizar telefone para DDD + número e validar tamanho")
    if "data_nascimento_invalida" in validation["issues"]:
        suggestions.append("validar data de nascimento com regra ISO yyyy-mm-dd e corrigir valor inconsistente")
    if "renda_negativa" in validation["issues"]:
        suggestions.append("revisar regra de captura da renda e bloquear valores negativos")
    if not suggestions:
        suggestions.append("registro consistente para uso analítico sem correções imediatas")

    return {
        "record_id": record_id,
        "suggestions": suggestions,
        "status_recommendation": "corrigir_antes_do_uso" if validation["issues"] else "aprovado_para_uso",
        "customer_name": record["customer_name"],
    }


def build_data_quality_summary(record_id: str) -> str:
    """Gera resumo executivo de qualidade do dado."""
    record = load_record(record_id)
    validation = validate_record_fields(record_id)
    correction = suggest_record_corrections(record_id)
    if validation["issues"]:
        return (
            f"O registro {record_id} de {record['customer_name']} apresenta {validation['issue_count']} problema(s) "
            f"de qualidade: {', '.join(validation['issues'])}. Recomendação: {correction['status_recommendation']}."
        )
    return (
        f"O registro {record_id} de {record['customer_name']} não apresentou inconsistências críticas e está "
        "aprovado para uso analítico."
    )


def build_fallback_report(record_id: str, user_question: str) -> dict[str, Any]:
    record = get_record_context(record_id)
    validation = validate_record_fields(record_id)
    correction = suggest_record_corrections(record_id)
    summary = build_data_quality_summary(record_id)

    final_message = (
        f"Pergunta analítica: {user_question}\n\n"
        f"Registro consultado:\n{json.dumps(record, ensure_ascii=False, indent=2)}\n\n"
        f"Validação:\n{json.dumps(validation, ensure_ascii=False, indent=2)}\n\n"
        f"Correções propostas:\n{json.dumps(correction, ensure_ascii=False, indent=2)}\n\n"
        f"Resumo executivo:\n{summary}"
    )

    return {
        "record_id": record_id,
        "record": record,
        "validation": validation,
        "corrections": correction,
        "summary": summary,
        "final_message": final_message,
    }
