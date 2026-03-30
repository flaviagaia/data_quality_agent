from __future__ import annotations

import streamlit as st

from src.agent import ask_data_quality_agent
from src.sample_data import load_dataset


st.set_page_config(page_title="Data Quality Agent", layout="wide")
st.title("Data Quality Agent")
st.caption("MVP com Haystack Agents para enriquecimento e validação de registros de dados.")

dataset = load_dataset()
options = dataset.set_index("record_id")["customer_name"].to_dict()

with st.sidebar:
    st.header("Stack Técnica")
    st.markdown(
        """
        - `Haystack Agents` para tool-calling
        - `OpenAIChatGenerator` como backend do chat model
        - `Tool` para validação e correção de registros
        - fallback determinístico para execução local
        - `Streamlit` para inspeção técnica
        """
    )
    st.header("Objetivo do MVP")
    st.markdown(
        """
        - detectar problemas de qualidade de dados
        - sugerir correções operacionais
        - produzir um resumo executivo do registro
        - apoiar uso analítico mais seguro
        """
    )

record_id = st.selectbox(
    "Selecione o registro",
    options=list(options.keys()),
    format_func=lambda rid: f"{rid} - {options[rid]}",
)

question = st.text_area(
    "Pergunta analítica",
    value="Esse registro pode ser usado com segurança em análises ou precisa de correção antes?",
    height=120,
)

if st.button("Executar agente", type="primary"):
    result = ask_data_quality_agent(record_id=record_id, user_question=question)

    c1, c2, c3 = st.columns(3)
    c1.metric("Runtime mode", result["runtime_mode"])
    c2.metric("Issue count", result["validation"]["issue_count"])
    c3.metric("Status recomendado", result["corrections"]["status_recommendation"])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Mensagem final", "Validação", "Correções", "Registro consultado"]
    )
    with tab1:
        st.markdown(result["final_message"])
    with tab2:
        st.write(result["summary"])
        st.json(result["validation"])
    with tab3:
        st.json(result["corrections"])
    with tab4:
        st.json(result["record"])

st.divider()
st.subheader("Arquitetura resumida")
st.code(
    """Analista -> Haystack Agent -> tools de qualidade -> resumo executivo + correções
          \\-> fallback determinístico local (sem OPENAI_API_KEY / sem runtime Haystack)""",
    language="text",
)
