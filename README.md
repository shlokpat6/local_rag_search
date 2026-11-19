# Document Q&A (RAG) App

A small document question-answering app built with Retrieval-Augmented Generation (RAG). Upload your own files, then ask questions in plain English. The app finds the most relevant passages in your documents, sends them to an LLM, and returns an answer along with the source file, page number, and similarity score so you can verify it.

This project started from a LlamaIndex tutorial that answered questions from Wikipedia articles. I extended it to accept user-uploaded files, support multiple file types, and save the index to disk.

## What you need

* Python 3.10 or newer
* An OpenAI API key (https://platform.openai.com/api-keys)
* An internet connection (embeddings and answers are generated through the OpenAI API)
* Some documents to try it on

**Privacy note:** the text of your documents is sent to OpenAI to create embeddings and to answer questions. Do not upload sensitive documents unless you are comfortable with that. LlamaIndex can be configured to use local models instead.

## Setup (Windows)

1. Install Python from https://www.python.org/downloads/ . During installation, check **Add Python to PATH**.
2. Download or clone this repository into a folder you can find, such as `Desktop\DocumentRAG`.
3. Open that folder in File Explorer.
4. Click the address bar, type `cmd`, and press Enter.
5. In the Command Prompt window, run these commands one at a time:

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Create a file named `.env` in the project folder containing your API key:

```
OPENAI_API_KEY=sk-your-key-here
```

7. Start the app:

```
streamlit run main.py
```

## Setup (Mac)

1. Install Python 3.10 or newer from https://www.python.org/downloads/ if you don't already have it.
2. Download or clone this repository.
3. Open Terminal and move into the project folder. For example:

```
cd ~/Desktop/DocumentRAG
```

4. Run:

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Create a `.env` file in the project folder containing your API key:

```
OPENAI_API_KEY=sk-your-key-here
```

6. Start the app:

```
streamlit run main.py
```

## Use it

* Streamlit opens a browser tab, usually at `http://localhost:8501`.
* Use the uploader to select one or more files.
* Click **Add to index** and wait for indexing to finish.
* Type a question in the **Ask a question** box and click **Submit**.
* Review the answer, then check the **Retrieved context** section to see exactly which passages it was based on.
* Click **Add to index** again at any time to add more documents. New files are added to the existing index rather than replacing it.
* Click **Clear index** to delete the saved index and start fresh.

## Supported file types

| Type | Notes |
|---|---|
| `.pdf` | Text-based PDFs only. Each page is indexed separately, so answers can cite page numbers. |
| `.docx` | Word documents |
| `.txt`, `.md` | Plain text and Markdown |
| `.csv` | Each row becomes part of the indexed text |

Files that fail to load (for example, a corrupt file) or contain no extractable text (for example, a scanned PDF) are skipped and reported in the app instead of crashing it.

## How it works

1. **Load:** uploaded files are read with LlamaIndex's `SimpleDirectoryReader`.
2. **Chunk and embed:** each document is split into chunks, and each chunk is converted to a vector with OpenAI's `text-embedding-3-small`.
3. **Store:** the vectors and text are saved to a local index folder so they survive restarts.
4. **Retrieve:** when you ask a question, it is embedded and the 3 most similar chunks are found.
5. **Generate:** those chunks and your question are sent to the LLM, which writes an answer based on them.

## Tech stack

* Python
* LlamaIndex (loading, chunking, indexing, and the query pipeline)
* OpenAI API (LLM and `text-embedding-3-small` embeddings)
* Streamlit (web UI and file uploads)
* pypdf and docx2txt (PDF and Word parsing)
* python-dotenv (API key management)

## Notes

* The index is saved in a folder named `my_docs_index` and is read back automatically the next time you start the app. Delete that folder (or click **Clear index**) if you want a completely fresh index.
* Only the extracted text and embeddings are saved. The original uploaded files are not kept.
* Uploading the same file twice adds its chunks twice, which can fill the top results with duplicate text.
* If you change the embedding model, clear the index and re-upload your files. Vectors from different models are not compatible.
* The saved index is shared by everyone using the same running copy of the app, so this version is intended for local, single-user use.
* The app retrieves only the top 3 chunks per question. It works well for "find the passage that answers this" questions and less well for whole-document questions like "summarize everything."
* Search scores are similarity scores, not probabilities.
* The LLM model name is set in `main.py` and can be changed to any model your OpenAI account supports.
* Keep your `.env` file and index folder out of version control (they are listed in `.gitignore`).
