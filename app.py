
import hashlib
import tempfile
from pathlib import Path

import streamlit as st

from src.pdf_loader import extract_text_from_pdf
from src.chunker import chunk_pages
from src.retriever import SemanticRetriever
from src.answer_generator import generate_answer


st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
)

st.title("📚 DocuMind AI")
st.caption("Chat with your documents. Get answers grounded in their content.")

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_names" not in st.session_state:
    st.session_state.document_names = []

with st.sidebar:
    st.header("Settings")

    model_name = st.text_input(
        "Ollama model",
        value="llama3.2:3b",
        help="Enter a model name shown by the `ollama list` command.",
    )

    top_k = st.slider(
        "Passages to retrieve",
        min_value=1,
        max_value=6,
        value=4,
    )

    st.divider()
    st.write("**Processing pipeline**")
    st.write("1. Extract PDF text")
    st.write("2. Split text into chunks")
    st.write("3. Search relevant passages")
    st.write("4. Generate an answer locally")

uploaded_files = st.file_uploader(
    "Upload one or more text-based PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
)

if st.button("Process documents", type="primary"):
    if not uploaded_files:
        st.warning("Upload at least one PDF first.")
    else:
        all_chunks = []
        successful_documents = []

        try:
            with st.spinner(
                "Extracting text and building the search index..."
            ):
                for uploaded_file in uploaded_files:
                    pdf_bytes = uploaded_file.getvalue()

                    # Avoid processing the same file twice.
                    digest = hashlib.sha256(pdf_bytes).hexdigest()

                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf", delete=False
                    ) as temp_file:
                        temp_file.write(pdf_bytes)
                        temp_path = Path(temp_file.name)

                    try:
                        pages = extract_text_from_pdf(str(temp_path))
                    finally:
                        temp_path.unlink(missing_ok=True)

                    if not pages:
                        st.warning(
                            f"No extractable text found in "
                            f"{uploaded_file.name}. It may be scanned."
                        )
                        continue

                    chunks = chunk_pages(pages)

                    for chunk in chunks:
                        chunk["source"] = uploaded_file.name
                        chunk["document_id"] = digest

                    all_chunks.extend(chunks)
                    successful_documents.append(uploaded_file.name)

                if not all_chunks:
                    st.error(
                        "No searchable text was found. Try a "
                        "text-based PDF rather than a scanned PDF."
                    )
                else:
                    retriever = SemanticRetriever()
                    retriever.build_index(all_chunks)

                    st.session_state.retriever = retriever
                    st.session_state.document_names = successful_documents
                    st.session_state.messages = []

                    st.success(
                        f"Indexed {len(successful_documents)} document(s) "
                        f"into {len(all_chunks)} chunks."
                    )

        except Exception as exc:
            st.error(f"Could not process the documents: {exc}")

if st.session_state.document_names:
    st.caption(
        "Loaded documents: "
        + ", ".join(st.session_state.document_names)
    )

    if st.button("Clear documents and chat"):
        st.session_state.retriever = None
        st.session_state.document_names = []
        st.session_state.messages = []
        st.rerun()

st.divider()
st.subheader("Chat with your documents")

# Display existing conversation.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("View retrieved source passages"):
                for source in message["sources"]:
                    st.markdown(
                        f"**{source['source']} — page {source['page']}**"
                    )
                    st.write(source["text"])
                    st.caption(
                        f"Similarity score: {source['score']:.3f}"
                    )

question = st.chat_input(
    "Ask a question about your PDFs...",
    disabled=st.session_state.retriever is None,
)

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching documents and generating an answer..."):
                results = st.session_state.retriever.search(
                    question,
                    top_k=top_k,
                )

                answer = generate_answer(
                    question,
                    results,
                    model=model_name,
                )

            st.markdown(answer)

            with st.expander("View retrieved source passages"):
                for source in results:
                    st.markdown(
                        f"**{source.get('source', 'Unknown document')} "
                        f"— page {source['page']}**"
                    )
                    st.write(source["text"])
                    st.caption(
                        f"Similarity score: {source['score']:.3f}"
                    )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": results,
                }
            )

        except Exception as exc:
            error_message = str(exc)
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Unable to answer: {error_message}",
                }
            )
