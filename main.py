import os # File system access and environment variables
import shutil # Lets us delete the saved index folder
import tempfile # Temporary folder for uploaded files
from dotenv import load_dotenv

import streamlit as st

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import (
    VectorStoreIndex, StorageContext, SimpleDirectoryReader,
    Settings, load_index_from_storage,
)

load_dotenv()

# Global embedding model, so loading from disk and answering questions use the same one
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

INDEX_DIR = 'my_docs_index' # Where the index is saved on disk

def load_saved_index():
    # Same idea as your original code: if the folder exists, load it instead of rebuilding
    if os.path.isdir(INDEX_DIR):
        storage = StorageContext.from_defaults(persist_dir=INDEX_DIR)
        return load_index_from_storage(storage)
    return None

def read_uploads(uploaded_files):
    # Write the in-memory uploads to a temp folder so SimpleDirectoryReader can read them
    with tempfile.TemporaryDirectory() as tmp_dir:
        paths = []
        for f in uploaded_files:
            path = os.path.join(tmp_dir, os.path.basename(f.name))
            with open(path, 'wb') as out:
                out.write(f.getbuffer())
            paths.append(path)
        return SimpleDirectoryReader(input_files=paths).load_data()

def add_to_index(index, docs):
    if index is None:
        index = VectorStoreIndex.from_documents(docs) # First upload: create the index
    else:
        for doc in docs:
            index.insert(doc) # Later uploads: add to the existing index
    index.storage_context.persist(persist_dir=INDEX_DIR) # Save to disk either way
    return index

def build_query_engine(index):
    llm = OpenAI(model='gpt-5.6-luna', temperature=0)
    return index.as_query_engine(llm=llm, similarity_top_k=3)

def main():
    st.title('Document RAG Application')

    # On the first run of a session, try to load an index saved by a previous run
    if 'index' not in st.session_state:
        st.session_state['index'] = load_saved_index()

    uploaded_files = st.file_uploader(
        'Upload your documents',
        type=['pdf', 'txt', 'md', 'docx', 'csv'],
        accept_multiple_files=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Add to index') and uploaded_files:
            with st.spinner('Reading and indexing documents...'):
                docs = read_uploads(uploaded_files)
                st.session_state['index'] = add_to_index(st.session_state['index'], docs)
            st.success(f'Added {len(uploaded_files)} file(s).')
    with col2:
        if st.button('Clear index'):
            shutil.rmtree(INDEX_DIR, ignore_errors=True)
            st.session_state['index'] = None
            st.success('Index cleared.')

    if st.session_state['index'] is not None:
        question = st.text_input('Ask a question')

        if st.button('Submit') and question:
            with st.spinner('Thinking...'):
                qa = build_query_engine(st.session_state['index'])
                response = qa.query(question)

            st.subheader('Answer')
            st.write(response.response)

            st.subheader('Retrieved context')
            for i, src in enumerate(response.source_nodes, start=1):
                name = src.node.metadata.get('file_name', 'Unknown file')
                page = src.node.metadata.get('page_label')
                label = f'{name} (page {page})' if page else name
                st.markdown(f'**Source {i}: {label}** (similarity: {src.score:.3f})')
                st.write(src.node.get_content())
                st.divider()
    else:
        st.info('Upload files and click "Add to index" to get started.')

if __name__ == '__main__':
    main()