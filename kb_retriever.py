from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import os

class KnowledgebaseRetriever:
    def __init__(self, knowledgebase_path: str):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.knowledgebase_path = knowledgebase_path
        self.sections = self._load_and_split_kb()
        self.embeddings = self._create_embeddings()

    def _load_and_split_kb(self) -> List[str]:
        """Load and split the knowledgebase into sections"""
        with open(self.knowledgebase_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by main sections (##) and subsections (###)
        sections = []
        current_section = []
        
        for line in content.split('\n'):
            if line.startswith('##') or line.startswith('###'):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections

    def _create_embeddings(self) -> np.ndarray:
        """Create embeddings for all sections"""
        return self.model.encode(self.sections)

    def retrieve_relevant_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve the most relevant sections for a given query"""
        # Create query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Get relevant sections
        relevant_sections = [self.sections[i] for i in top_indices]
        
        # Join sections with clear separators
        context = "\n\n---\n\n".join(relevant_sections)
        
        return context
