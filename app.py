
import hashlib
import tempfile
from pathlib import Path

import streamlit as st

from src.pdf_loader import extract_text_from_pdf
from src.chunker import chunk_pages
from src.retriever import SemanticRetriever
from src.answer_generator import generate_answer
from src.index_store import (
    DEFAULT_STORAGE_DIR,
    delete_document,
    load_retriever,
    save_retriever,
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
)

st.title("📚 DocuMind AI")
st.caption(
    "Chat with your documents. Get answers grounded in their content."
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def document_names_from_chunks(chunks: list[dict]) -> list[str]:
    """Return unique source names in the order first encountered."""
    names = []
    seen = set()

    for chunk in chunks:
        name = chunk.get("source", "Unknown document")
        if name not in seen:
            names.append(name)
            seen.add(name)

    return names


def document_library_from_chunks(chunks: list[dict]) -> dict:
    """Group indexed chunks by unique document ID."""
    documents = {}

    for chunk in chunks:
        document_id = chunk.get("document_id")

        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "source": chunk.get("source", "Unknown document"),
                "chunk_count": 0,
                "pages": set(),
            }

        documents[document_id]["chunk_count"] += 1

        page = chunk.get("page")
        if page is not None:
            documents[document_id]["pages"].add(page)

    return documents


def show_sources(sources: list[dict]) -> None:
    """Display retrieved passages and their source pages."""
    if not sources:
        return

    with st.expander("View retrieved source passages"):
        for source in sources:
            filename = source.get("source", "Unknown document")
            page = source.get("page", "Unknown")
            score = source.get("score")

            st.markdown(f"**{filename} — Page {page}**")

            if score is not None:
                st.caption(f"Similarity score: {score:.3f}")

            st.write(source.get("text", "No passage text available."))
            st.divider()


def initialize_session() -> None:
    """Initialize session state and restore the saved collection."""
    if "storage_initialized" in st.session_state:
        return

    st.session_state.retriever = None
    st.session_state.messages = []
    st.session_state.storage_error = None

    try:
        st.session_state.retriever = load_retriever(
            DEFAULT_STORAGE_DIR
        )
    except Exception as exc:
        st.session_state.storage_error = str(exc)

    st.session_state.storage_initialized = True


# ---------------------------------------------------------
# INITIALIZE APP STATE
# ---------------------------------------------------------

initialize_session()


# ---------------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------------

with st.sidebar:
    st.header("Settings")

    model_name = st.text_input(
        "Ollama model",
        value="llama3.2:3b",
        help="Use a model name shown by the 'ollama list' command.",
    ).strip()

    top_k = st.slider(
        "Passages to retrieve",
        min_value=1,
        max_value=6,
        value=4,
    )

    st.divider()

    st.subheader("How it works")
    st.markdown(
        """
        1. Upload PDF documents
        2. Extract and split their text
        3. Find relevant passages with semantic search
        4. Generate answers using your local Ollama model
        """
    )


# ---------------------------------------------------------
# STORAGE ERROR
# ---------------------------------------------------------

if st.session_state.storage_error:
    st.error(
        "The saved document index could not be loaded. "
        "Your stored files have not been automatically deleted."
    )
    st.caption(st.session_state.storage_error)


# ---------------------------------------------------------
# PDF UPLOAD AND PROCESSING
# ---------------------------------------------------------

st.header("Add documents")

uploaded_files = st.file_uploader(
    "Upload one or more text-based PDF documents",
    type=["pdf"],
    accept_multiple_files=True,
    help="Scanned PDFs may require OCR before their text can be indexed.",
)

if st.button("Process documents", type="primary"):
    if not uploaded_files:
        st.warning("Upload at least one PDF first.")

    else:
        existing_retriever = st.session_state.retriever

        existing_chunks = (
            list(existing_retriever.chunks)
            if existing_retriever is not None
            else []
        )

        existing_ids = {
            chunk.get("document_id")
            for chunk in existing_chunks
            if chunk.get("document_id")
        }

        processed_ids = set(existing_ids)
        new_chunks = []
        skipped_duplicates = []
        unreadable_documents = []

        try:
            progress = st.progress(0, text="Preparing documents...")

            for position, uploaded_file in enumerate(uploaded_files):
                pdf_bytes = uploaded_file.getvalue()
                digest = hashlib.sha256(pdf_bytes).hexdigest()

                # Skip a PDF already present in the collection.
                if digest in processed_ids:
                    skipped_duplicates.append(uploaded_file.name)
                    progress.progress(
                        (position + 1) / len(uploaded_files),
                        text=f"Skipping duplicate: {uploaded_file.name}",
                    )
                    continue

                progress.progress(
                    position / len(uploaded_files),
                    text=f"Extracting text: {uploaded_file.name}",
                )

                temp_path = None

                try:
                    with tempfile.NamedTemporaryFile(
                        suffix=".pdf",
                        delete=False,
                    ) as temp_file:
                        temp_file.write(pdf_bytes)
                        temp_path = Path(temp_file.name)

                    pages = extract_text_from_pdf(str(temp_path))

                finally:
                    if temp_path is not None:
                        temp_path.unlink(missing_ok=True)

                if not pages:
                    unreadable_documents.append(uploaded_file.name)
                    continue

                chunks = chunk_pages(pages)

                if not chunks:
                    unreadable_documents.append(uploaded_file.name)
                    continue

                for chunk in chunks:
                    chunk["source"] = uploaded_file.name
                    chunk["document_id"] = digest

                new_chunks.extend(chunks)
                processed_ids.add(digest)

                progress.progress(
                    (position + 1) / len(uploaded_files),
                    text=f"Processed: {uploaded_file.name}",
                )

            progress.empty()

            if unreadable_documents:
                st.warning(
                    "No searchable text was extracted from: "
                    + ", ".join(unreadable_documents)
                    + ". These PDFs may be scanned or contain no extractable text."
                )

            if new_chunks:
                with st.spinner("Creating semantic embeddings and saving index..."):
                    if existing_retriever is None:
                        retriever = SemanticRetriever()
                        retriever.build_index(new_chunks)
                    else:
                        retriever = existing_retriever
                        retriever.add_chunks(new_chunks)

                    # Save before updating session state.
                    save_retriever(retriever, DEFAULT_STORAGE_DIR)

                    st.session_state.retriever = retriever
                    st.session_state.storage_error = None

                st.success(
                    f"Added {len(new_chunks)} chunks. "
                    f"The collection now contains "
                    f"{len(retriever.chunks)} chunks."
                )

            elif st.session_state.retriever is not None:
                st.info("No new searchable content was added.")

            else:
                st.warning(
                    "No searchable text was found. "
                    "Try a text-based PDF."
                )

            if skipped_duplicates:
                st.info(
                    "Already indexed: "
                    + ", ".join(skipped_duplicates)
                )

        except Exception as exc:
            st.error(f"Could not process the documents: {exc}")


# ---------------------------------------------------------
# DOCUMENT LIBRARY
# ---------------------------------------------------------

st.divider()
st.header("Document library")

retriever = st.session_state.retriever

if retriever is None or not retriever.chunks:
    st.info("No documents indexed yet. Upload a PDF to get started.")

else:
    library = document_library_from_chunks(retriever.chunks)

    total_chunks = len(retriever.chunks)

    col1, col2 = st.columns(2)
    col1.metric("Documents", len(library))
    col2.metric("Indexed chunks", total_chunks)

    if not library:
        st.warning(
            "The saved index has no document IDs. "
            "Re-upload these PDFs if you want to manage them individually."
        )

    for document_id, details in library.items():
        filename = details["source"]
        chunk_count = details["chunk_count"]
        pages = sorted(details["pages"])

        with st.expander(
            f"📄 {filename} — {chunk_count} chunks"
        ):
            st.write(f"**Filename:** {filename}")
            st.write(f"**Indexed chunks:** {chunk_count}")

            if pages:
                st.write(f"**Pages represented:** {len(pages)}")
                st.caption(
                    "Page numbers: "
                    + ", ".join(str(page) for page in pages)
                )

            st.caption(f"Document ID: {document_id[:12]}…")

            confirmed = st.checkbox(
                f"Confirm deletion of {filename}",
                key=f"confirm_delete_{document_id}",
            )

            if st.button(
                "Delete document",
                key=f"delete_doc_{document_id}",
                disabled=not confirmed,
                type="secondary",
            ):
                try:
                    with st.spinner(f"Removing {filename}..."):
                        updated_retriever = delete_document(
                            st.session_state.retriever,
                            document_id,
                            DEFAULT_STORAGE_DIR,
                        )

                    st.session_state.retriever = updated_retriever

                    # Remove old answers that may cite the deleted PDF.
                    st.session_state.messages = []

                    st.success(f"Deleted {filename} from the index.")
                    st.rerun()

                except Exception as exc:
                    st.error(f"Could not delete the document: {exc}")


# ---------------------------------------------------------
# CHAT INTERFACE
# ---------------------------------------------------------

st.divider()
st.header("Chat with your documents")

if st.session_state.retriever is None:
    st.info("Process at least one PDF before asking questions.")

# Render previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            show_sources(message.get("sources", []))


prompt = st.chat_input(
    "Ask a question about your indexed documents..."
)

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.retriever is None:
            answer = "Please upload and process a PDF before asking questions."
            sources = []

            st.warning(answer)

        elif not model_name:
            answer = "Enter an Ollama model name in the sidebar."
            sources = []

            st.warning(answer)

        else:
            try:
                with st.spinner("Searching documents and generating an answer..."):
                    sources = st.session_state.retriever.search(
                        prompt,
                        top_k=top_k,
                    )

                    if not sources:
                        answer = (
                            "I couldn't find relevant passages in the indexed documents."
                        )
                    else:
                        answer = generate_answer(
                        prompt,
                        sources,
                        model=model_name,
                    )

                st.markdown(answer)
                show_sources(sources)

            except Exception as exc:
                answer = f"Unable to answer: {exc}"
                sources = []
                st.error(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )
