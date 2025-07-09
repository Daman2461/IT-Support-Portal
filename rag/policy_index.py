import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

class PolicyRetriever:
    def __init__(self, policy_dir="policies"):
        self.policy_dir = policy_dir
        self.index = None
        self.docs = []
        self._load_and_index()

    def _load_and_index(self):
        # Load all .md files
        for fname in os.listdir(self.policy_dir):
            if fname.endswith(".md"):
                with open(os.path.join(self.policy_dir, fname), "r") as f:
                    content = f.read()
                    self.docs.append(Document(page_content=content, metadata={"source": fname}))
        # Split docs
        splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(self.docs)
        # Embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.index = FAISS.from_documents(split_docs, embeddings)

    def retrieve(self, query, k=2):
        return self.index.similarity_search(query, k=k)
