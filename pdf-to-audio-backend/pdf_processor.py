"""
PDF processing utilities for text extraction and chunking
"""

import pdfplumber
import fitz  # PyMuPDF
import re
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handle PDF text extraction and processing"""
    
    def __init__(self, max_chunk_size: int = 2000):
        """
        Initialize PDF processor
        
        Args:
            max_chunk_size: Maximum characters per text chunk for TTS
        """
        self.max_chunk_size = max_chunk_size
    
    async def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using multiple methods for best results
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text_content = ""
        
        try:
            # Try pdfplumber first (better for text-based PDFs)
            text_content = await self._extract_with_pdfplumber(pdf_path)
            
            if not text_content.strip():
                # Fallback to PyMuPDF (better for some PDF types)
                text_content = await self._extract_with_pymupdf(pdf_path)
            
            if not text_content.strip():
                raise Exception("No readable text found in PDF")
            
            # Clean and normalize text
            text_content = self._clean_text(text_content)
            
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    async def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber"""
        text_parts = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"Extracted text from page {page_num + 1}")
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
            return ""
    
    async def _extract_with_pymupdf(self, pdf_path: Path) -> str:
        """Extract text using PyMuPDF as fallback"""
        text_parts = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text_parts.append(page_text)
                    logger.debug(f"Extracted text from page {page_num + 1}")
            
            doc.close()
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text suitable for TTS
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Fix common PDF extraction artifacts
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Missing spaces
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Missing spaces after punctuation
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', text)
        
        # Normalize paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks suitable for TTS processing
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) + 2 > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If paragraph itself is too long, split by sentences
                if len(paragraph) > self.max_chunk_size:
                    sentence_chunks = self._split_by_sentences(paragraph)
                    chunks.extend(sentence_chunks)
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks and merge them
        filtered_chunks = self._merge_short_chunks(chunks)
        
        logger.info(f"Created {len(filtered_chunks)} text chunks")
        return filtered_chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split long text by sentences"""
        # Simple sentence splitting (could be improved with nltk)
        sentences = re.split(r'[.!?]+\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) + 2 > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # If single sentence is too long, force split
                    if len(sentence) > self.max_chunk_size:
                        chunks.extend(self._force_split_text(sentence))
                    else:
                        current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _force_split_text(self, text: str) -> List[str]:
        """Force split very long text"""
        chunks = []
        while len(text) > self.max_chunk_size:
            # Find last space before chunk size limit
            split_pos = text.rfind(' ', 0, self.max_chunk_size)
            if split_pos == -1:
                split_pos = self.max_chunk_size
            
            chunks.append(text[:split_pos].strip())
            text = text[split_pos:].strip()
        
        if text:
            chunks.append(text)
        
        return chunks
    
    def _merge_short_chunks(self, chunks: List[str], min_chunk_size: int = 100) -> List[str]:
        """Merge very short chunks with adjacent chunks"""
        if not chunks:
            return chunks
        
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # If chunk is too short and not the last one, try to merge
            if len(current_chunk) < min_chunk_size and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                
                # If merging doesn't exceed max size, merge
                if len(current_chunk) + len(next_chunk) + 2 <= self.max_chunk_size:
                    merged_chunk = current_chunk + "\n\n" + next_chunk
                    merged_chunks.append(merged_chunk)
                    i += 2  # Skip next chunk as it's been merged
                    continue
            
            merged_chunks.append(current_chunk)
            i += 1
        
        return merged_chunks
