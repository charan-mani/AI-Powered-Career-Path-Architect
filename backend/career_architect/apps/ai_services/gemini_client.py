# backend/career_architect/apps/ai_services/gemini_client.py
import google.generativeai as genai
from django.conf import settings
import json
import logging
import time
import requests
from google.api_core import client_options
from google.api_core import timeout

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-3-flash-preview')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your environment variables.")
        
        # Configure with timeout settings
        genai.configure(api_key=self.api_key)
        
        # Create model with default settings
        self.model = genai.GenerativeModel(self.model_name)
        
    def generate_content(self, prompt, temperature=0.7, max_tokens=4096, retries=2):
        """Generate content using Gemini - returns text only with retry logic"""
        
        for attempt in range(retries + 1):
            try:
                logger.info(f"Sending prompt to Gemini (attempt {attempt + 1}/{retries + 1}, length: {len(prompt)} chars)")
                
                # Create generation config
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=40,
                )
                
                # Generate content without request_options
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                logger.info(f"Successfully generated response ({len(response.text)} chars)")
                
                return {
                    'text': response.text,
                    'structured': None
                }
                
            except Exception as e:
                error_str = str(e)
                logger.error(f"Gemini API error (attempt {attempt + 1}): {error_str}")
                
                # Check for timeout-related errors
                if "deadline" in error_str.lower() or "timeout" in error_str.lower():
                    logger.info("Timeout detected, will retry with exponential backoff")
                
                # If this was the last retry, raise the exception
                if attempt == retries:
                    raise Exception(f"Failed to generate content after {retries + 1} attempts: {error_str}")
                
                # Wait before retrying (exponential backoff)
                wait_time = (attempt + 1) * 2
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    def generate_roadmap(self, data):
        """Generate a career roadmap as text"""
        from .prompt_templates import get_roadmap_text_prompt
        
        prompt = get_roadmap_text_prompt(data)
        response = self.generate_content(prompt, temperature=0.8)
        
        return {
            'description': response['text'],
            'steps': []
        }
    
    def chat(self, message, context=None):
        """Chat with Gemini"""
        context_str = json.dumps(context) if context else ""
        prompt = f"""Context: {context_str}
        
User message: {message}

Provide a helpful, professional response as a career assistant."""
        
        return self.generate_content(prompt, temperature=0.9, max_tokens=1024)