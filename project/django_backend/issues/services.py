from openai import OpenAI
from django.conf import settings
from PIL import Image
import pytesseract
import os
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)


class AIService:
    """Service for AI-powered text cleanup using OpenAI GPT-4o-mini"""
    
    @staticmethod
    def generate_summary_and_title(description, alarm_code=None, category=None):
        """
        Clean up grammar and generate auto title from raw operator input.
        No new ideas should be added. Only improve sentence structure.
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return description, description[:50] + "..." if len(description) > 50 else description
        
        try:
            # Prompt for sentence cleanup (no summarization!)
            grammar_prompt = f"""
You are a sentence cleanup tool. Do not summarize or add new ideas.

Only correct the grammar and structure of the sentence below, keeping every detail as written.

Use exactly the same meaning, just improve clarity and flow.

Input:
\"\"\"{description}\"\"\"

Output (cleaned sentence):
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a grammar assistant. Do not summarize or add content."},
                    {"role": "user", "content": grammar_prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )

            ai_summary = response.choices[0].message.content.strip()

            # Prompt for title (based on original description and alarm code)
            context_info = ""
            if alarm_code:
                context_info = f"Alarm Code: {alarm_code}\n"
            if category:
                context_info += f"Category: {category}\n"
            
            title_prompt = f"""
Create a short, direct title (max 10 words) based strictly on the information below.

{f"Include the alarm code ({alarm_code}) in the title." if alarm_code else "Do not mention alarm codes since none is provided."}

{context_info}Description: {description}

Title:
"""

            title_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a title generator that does not add extra ideas. Include alarm codes when provided."},
                    {"role": "user", "content": title_prompt}
                ],
                max_tokens=40,
                temperature=0.2
            )

            ai_title = title_response.choices[0].message.content.strip()

            return ai_summary, ai_title

        except Exception as e:
            logger.exception("Error during AI generation")
            return description, description[:50] + "..." if len(description) > 50 else description
    
    @staticmethod
    def improve_remedy_description(description, issue_context=None):
        """
        Improve grammar and clarity of remedy description, with translation to English if needed.
        """
        if not settings.OPENAI_API_KEY or not client:
            logger.warning("OpenAI API key not configured")
            return description
        
        try:
            # Enhanced prompt with translation support
            prompt = f"""
You are a technical writing assistant for machine maintenance documentation.

Your task is to process the following maintenance remedy description:

1. If the text is not in English, translate it to English first
2. Improve grammar, sentence structure, and technical clarity
3. Keep all original details and actions mentioned
4. Use professional maintenance terminology
5. Do not add new steps or suggestions beyond what is written

Input text:
\"\"\"{description}\"\"\"

Output (improved English description):
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a technical writing assistant for machine maintenance. Translate to English if needed and improve technical clarity without adding new content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            improved_description = response.choices[0].message.content.strip()
            return improved_description
            
        except Exception as e:
            logger.error(f"AI remedy improvement error: {str(e)}")
            return description
    
    @staticmethod
    def improve_issue_description(description, alarm_code=None, category=None):
        """
        Improve grammar and clarity of issue description, with translation to English if needed.
        """
        if not settings.OPENAI_API_KEY or not client:
            logger.warning("OpenAI API key not configured")
            return description
        
        try:
            context_info = ""
            if alarm_code:
                context_info += f"Alarm Code: {alarm_code}\n"
            if category:
                context_info += f"Category: {category}\n"
            
            # Enhanced prompt with translation support for issues
            prompt = f"""
You are a technical writing assistant for machine maintenance issue reporting.

Your task is to process the following machine issue description:

1. If the text is not in English, translate it to English first
2. Improve grammar, sentence structure, and technical clarity
3. Keep all original details and symptoms mentioned
4. Use professional maintenance terminology
5. Do not add new information beyond what is described

{context_info}
Input text:
\"\"\"{description}\"\"\"

Output (improved English description):
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a technical writing assistant for machine maintenance. Translate to English if needed and improve technical clarity without adding new content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            improved_description = response.choices[0].message.content.strip()
            return improved_description
            
        except Exception as e:
            logger.error(f"AI issue improvement error: {str(e)}")
            return description


class OCRService:
    """Service for Optical Character Recognition using Tesseract"""
    
    @staticmethod
    def extract_alarm_code_from_image(image_path):
        """
        Extract alarm code or text from an alarm screen image
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Open and process image
            image = Image.open(image_path)
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(
                image,
                config='--psm 6 --oem 3'  # Assume uniform text block
            )
            
            # Clean up extracted text
            cleaned_text = extracted_text.strip()
            
            # Try to extract alarm codes (common patterns)
            alarm_patterns = OCRService._extract_alarm_patterns(cleaned_text)
            
            if alarm_patterns:
                return {
                    'alarm_codes': alarm_patterns,
                    'full_text': cleaned_text
                }
            
            return {
                'alarm_codes': [],
                'full_text': cleaned_text
            }
            
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return None
    
    @staticmethod
    def _extract_alarm_patterns(text):
        """
        Extract common alarm code patterns from OCR text
        """
        import re
        
        alarm_patterns = []
        
        # Common alarm code patterns
        patterns = [
            r'ALARM\s*[\:\-]?\s*(\d+)',  # ALARM: 123 or ALARM-123
            r'ERROR\s*[\:\-]?\s*(\d+)',  # ERROR: 456
            r'(\d{2,4})',  # Any 2-4 digit number
            r'([A-Z]\d{2,3})',  # Letter followed by 2-3 digits (A123)
            r'(\d{1,2}[A-Z]\d{1,2})',  # Digit-Letter-Digit patterns
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            alarm_patterns.extend(matches)
        
        # Remove duplicates and return
        return list(set(alarm_patterns))


class FileService:
    """Service for file handling and validation"""
    
    @staticmethod
    def validate_file_type(file):
        """
        Validate if uploaded file type is allowed
        """
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'video/mp4', 'video/avi', 'video/mov', 'video/wmv'
        ]
        
        return file.content_type in allowed_types
    
    @staticmethod
    def determine_file_type(file):
        """
        Determine if file is image or video
        """
        if file.content_type.startswith('image/'):
            return 'image'
        elif file.content_type.startswith('video/'):
            return 'video'
        else:
            return 'other' 