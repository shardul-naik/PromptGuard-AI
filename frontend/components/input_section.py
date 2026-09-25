from typing import Any

import streamlit as st


def render_input_section(
    status: str = "idle",
) -> tuple[str, Any, bool, Any]:

    st.markdown(
        """
        <h1 style="margin-bottom: 0;">PromptGuard-AI</h1>
        <p style="margin-top: 0; color: #777;">
        Quality-aware LLM routing and semantic caching gateway
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Enter your input")

    prompt = st.text_area(
        "Prompt",
        placeholder=(
            "Ask a question, explain something, "
            "analyze information, or provide instructions..."
        ),
        height=140,
        label_visibility="collapsed",
    )

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf"],
        help="PDF documents only.",
    )

    analyze_clicked = st.button(
        "Analyze",
        type="primary",
        use_container_width=True,
    )

    status_box = st.empty()

    if status == "processing":
        status_box.info(
            "⏳ Analyzing..."
        )
    elif status == "complete":
        status_box.success(
            "✓ Analysis complete"
        )
    elif status == "blocked":
        status_box.error(
            "✕ Request blocked by security layer"
        )

    return (
        prompt,
        uploaded_file,
        analyze_clicked,
        status_box,
    )