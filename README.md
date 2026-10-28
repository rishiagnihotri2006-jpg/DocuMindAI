\# DocuMindAI 📚🤖



\### Ask Questions. Understand Documents. Get Source-Grounded Answers.



DocuMindAI is a locally running AI-powered document question-answering application that allows users to upload PDF documents, retrieve relevant information, and ask questions in natural language.



It combines document processing, semantic search, vector retrieval, and a locally hosted large language model to help users interact with their documents without manually searching through every page.



\## ✨ Features



\- \*\*PDF Text Extraction:\*\* Extract text and page information from PDF documents.

\- \*\*Intelligent Text Chunking:\*\* Divide extracted text into manageable, overlapping chunks for retrieval.

\- \*\*Semantic Search:\*\* Retrieve relevant document passages using vector embeddings and FAISS.

\- \*\*AI-Powered Question Answering:\*\* Generate natural-language answers using a locally hosted Ollama model.

\- \*\*Source References:\*\* Use retrieved document passages and their page information to support answers.

\- \*\*Persistent Document Index:\*\* Save the document index locally so processed documents can remain available after restarting the application.

\- \*\*Document Library:\*\* Manage processed documents through the application.

\- \*\*Duplicate Detection:\*\* Detect previously indexed documents to avoid unnecessary reprocessing.

\- \*\*Document Deletion:\*\* Remove individual documents from the document library.

\- \*\*Local Inference:\*\* Run the language model on your own machine using Ollama.



\## 🛠️ Technology Stack



| Technology | Purpose |

|---|---|

| Python | Application logic and document processing |

| Streamlit | Interactive web interface |

| PyMuPDF | PDF text extraction |

| Sentence Transformers | Generate semantic embeddings |

| FAISS | Efficient vector similarity search |

| Ollama | Run the language model locally |

| Llama 3.2 3B | Local language model used for answer generation |

| Pytest | Automated testing |



\## 🏗️ Application Architecture



DocuMindAI follows a retrieval-augmented question-answering workflow.



```text

&#x20;                ┌─────────────────────┐

&#x20;                │     PDF Upload      │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │   PDF Text          │

&#x20;                │   Extraction        │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │   Text Chunking     │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │ Embedding Generation│

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │   FAISS Vector      │

&#x20;                │   Index             │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;               User Question

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │ Relevant Passage    │

&#x20;                │ Retrieval           │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │ Ollama + Llama 3.2  │

&#x20;                │ Answer Generation   │

&#x20;                └──────────┬──────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                ┌─────────────────────┐

&#x20;                │ Answer and Source   │

&#x20;                │ References           │

&#x20;                └─────────────────────┘

```



\### How It Works



1\. \*\*Upload:\*\* The user uploads a PDF through the Streamlit interface.

2\. \*\*Extract:\*\* PyMuPDF extracts text and associated page information.

3\. \*\*Chunk:\*\* The extracted text is divided into smaller, overlapping passages.

4\. \*\*Embed:\*\* Sentence Transformers converts the passages into vector embeddings.

5\. \*\*Index:\*\* FAISS stores the vectors to support similarity-based retrieval.

6\. \*\*Retrieve:\*\* When a user asks a question, the application retrieves relevant passages from the indexed documents.

7\. \*\*Generate:\*\* The retrieved passages are supplied to the local Llama model through Ollama.

8\. \*\*Respond:\*\* The application presents the generated answer and associated source information.



The retrieval step helps ground answers in the uploaded documents. However, generated answers should still be checked against their cited source passages.



\## 💻 Requirements



Before installing DocuMindAI, make sure you have:



\- Windows, macOS, or Linux.

\- Python installed.

\- Git installed.

\- Ollama installed and working.

\- Sufficient memory and disk space for the embedding model and local language model.



The project was developed and tested on Windows using Python 3.14.3.



The language model and embedding model require additional disk space. Performance depends on your hardware and the size of your documents.



\## 🚀 Installation and Setup



The following commands use Windows PowerShell.



\### 1. Clone the Repository



```powershell

git clone https://github.com/rishiagnihotri2006-jpg/DocuMindAI.git

cd DocuMindAI

```



\### 2. Create a Virtual Environment



```powershell

python -m venv .venv

```



Activate it in PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



If PowerShell blocks script activation, you can use the virtual environment's Python executable directly instead.



\### 3. Install Dependencies



```powershell

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

```



If you did not activate the environment, run:



```powershell

.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



\### 4. Install and Configure Ollama



Install Ollama on your computer.



Pull the model used by the application:



```powershell

ollama pull llama3.2:3b

```



Verify that the model is installed:



```powershell

ollama list

```



Confirm that the Ollama API is responding:



```powershell

Invoke-RestMethod -Uri "http://localhost:11434/api/tags"

```



The application expects Ollama to be accessible locally. If the API is unavailable, start Ollama using its normal application or service startup procedure.



\### 5. Run DocuMindAI



From the project directory:



```powershell

streamlit run app.py

```



If the virtual environment is not activated, use:



```powershell

.\\.venv\\Scripts\\python.exe -m streamlit run app.py

```



Open the local address displayed in the terminal by Streamlit.



You can now upload a PDF, process it, and ask questions about its contents.



\## 🧪 Running Tests



DocuMindAI includes automated tests for document processing, chunking, retrieval, and Ollama integration.



Run the complete test suite:



```powershell

python -m pytest -v

```



Alternatively, use the virtual environment's Python executable:



```powershell

.\\.venv\\Scripts\\python.exe -m pytest -v

```



\### Test Results



The current development version passed \*\*11 automated tests\*\*.



| Component | Tests Passed |

|---|---:|

| Text chunking | 4 |

| Ollama answer generation | 1 |

| PDF text extraction | 3 |

| Document retrieval | 3 |

| \*\*Total\*\* | \*\*11\*\* |



The application was also manually tested for:



\- PDF upload and processing.

\- Question answering and source references.

\- Handling questions not answered by the uploaded document.

\- Duplicate document detection.

\- Index persistence after restarting the application.

\- Individual document deletion.



All seven manual checks passed in the development environment.



These results describe the tested development version and do not guarantee that every PDF, machine, or question will produce the same results.



\## 📁 Project Structure



```text

DocuMindAI/

│

├── app.py

├── requirements.txt

├── README.md

├── .gitignore

│

├── src/

│   ├── answer\_generator.py

│   ├── chunker.py

│   ├── pdf\_loader.py

│   ├── retriever.py

│   └── index\_store.py

│

├── tests/

│   ├── test\_chunker.py

│   ├── test\_ollama.py

│   ├── test\_pdf\_loader.py

│   └── test\_retriever.py

│

├── sample\_docs/

├── .streamlit/

└── storage/

```



The structure above illustrates the principal project files. Some directories are created or populated locally during application use.



\### Important Directories



\- `src/` — Core application modules.

\- `tests/` — Automated tests.

\- `sample\_docs/` — Directory for permitted sample documents.

\- `.streamlit/` — Streamlit configuration.

\- `storage/` — Local persistent index and related application data.



Generated indexes, local document data, virtual environments, and Python cache files are excluded from version control where configured in `.gitignore`.



\## 🔒 Privacy and Data Handling



DocuMindAI uses Ollama to run the configured language model locally.



The application's PDF processing, embedding generation, and retrieval workflow run on the user's computer in the tested configuration.



Keep in mind:



\- The language model and embedding models must be installed locally.

\- Uploaded documents and persistent index files may remain on your computer.

\- The GitHub repository does not include the local `storage/` index.

\- Local model inference does not automatically mean every dependency or application component is guaranteed to operate offline.

\- Avoid uploading confidential documents to any external service unless you understand its data-handling practices.



\## ⚠️ Current Limitations



\- Answer quality depends on document quality, retrieval relevance, and language-model performance.

\- Scanned PDFs may require OCR if they do not contain extractable text.

\- Large documents can require additional processing time and memory.

\- Generated answers may contain inaccuracies, even when relevant passages are retrieved.

\- The application requires a working local Ollama installation and the configured model.

\- A newly cloned

