# ui/app.py
import gradio as gr
import requests
import json
from typing import List, Dict, Any, Tuple
from config import CODES


def get_available_law_codes() -> List[str]:
    """
    Get the list of available law codes from the API.

    Returns:
        List of law code names
    """
    try:
        response = requests.get("http://localhost:8000/api/law-codes")
        response.raise_for_status()
        data = response.json()
        return data.get("law_codes", [])
    except Exception:
        # Fallback to some common codes if API is not available
        return CODES


def query_api(
    query: str, law_codes: List[str], use_search: bool, use_rag: bool
) -> Tuple[str, str, str]:
    """
    Query the API with the given parameters.

    Args:
        query: The query to send
        law_codes: List of law codes to use
        use_search: Whether to use search
        use_rag: Whether to use RAG

    Returns:
        Tuple of (direct_answer, multi_agent_answer)
    """
    # Build request
    request = {
        "query": query,
        "law_codes": law_codes,
        "use_search": use_search,
        "use_rag": use_rag,
        "verbose": True,
    }

    # Send request to API
    try:
        response = requests.post("http://localhost:8000/api/query", json=request)
        response.raise_for_status()
        data = response.json()

        # Extract answers
        direct_answer = data.get("direct_answer", "Non disponible")
        multi_agent_answer = data.get("multi_agent_answer", "Non disponible")

        return direct_answer, multi_agent_answer

    except Exception as e:
        error_message = f"⚠️ Erreur: {str(e)}"
        return error_message, error_message, error_message


def create_ui():
    """
    Create and launch the Gradio UI.

    Returns:
        Gradio Interface
    """
    available_codes = get_available_law_codes()

    with gr.Blocks(
        title="Assistant Juridique Français", theme=gr.themes.Base()
    ) as demo:
        gr.Markdown(
            """
            <div style="text-align:center; font-size: 2em; font-weight: bold;">
                ⚖️ Assistant Juridique Français
            </div>
            <p style="text-align:center; font-size: 1.1em;">
                Posez une question de droit et comparez :
                <ul>
                    <li>🧠 Réponse directe (LLM seul)</li>
                    <li>🤖 Réponse multi-agent (RAG + Google Search)</li>
                </ul>
            </p>
            """,
        )

        with gr.Row():
            query_input = gr.Textbox(
                label="❓ Votre question juridique",
                placeholder="Ex : Quels sont mes droits en cas de licenciement ?",
                lines=3,
                max_lines=5,
                autofocus=True,
                show_label=True,
                interactive=True,
                container=True,
                elem_id="query-input",
            )

        with gr.Row():
            with gr.Column(scale=1):
                law_codes = gr.Dropdown(
                    choices=available_codes,
                    label="📘 Code(s) de loi à utiliser",
                    value=available_codes[:1],
                    multiselect=True,
                    interactive=True,
                )

            with gr.Column(scale=1):
                with gr.Accordion("⚙️ Options", open=False):
                    use_search = gr.Checkbox(
                        label="🔎 Utiliser Google Search", value=True
                    )
                    use_rag = gr.Checkbox(
                        label="📚 Utiliser la base juridique (RAG)", value=True
                    )

        submit_btn = gr.Button("🚀 Comparer les réponses", variant="primary", size="lg")

        gr.Markdown("---")

        with gr.Row(equal_height=True):
            with gr.Column():
                direct_output = gr.Textbox(
                    label="🧠 Réponse LLM Direct", lines=15, show_copy_button=True
                )
            with gr.Column():
                multi_output = gr.Textbox(
                    label="🤖 Réponse Multi-Agent", lines=15, show_copy_button=True
                )

        submit_btn.click(
            fn=query_api,
            inputs=[query_input, law_codes, use_search, use_rag],
            outputs=[direct_output, multi_output],
        )

    return demo


def launch_ui():
    """
    Launch the UI.
    """
    demo = create_ui()
    demo.launch()
