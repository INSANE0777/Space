# agents/dictionary_agent.py

import requests
import re

def run(previous_data: dict) -> dict:
    """
    Dictionary agent that provides word definitions, synonyms, and language information.
    Uses the Free Dictionary API for comprehensive word information.
    """
    goal = previous_data.get("goal", "")
    
    # Extract word(s) to define from the goal
    # Handle multiple words (e.g., "apogee" and "perigee")
    words_to_define = extract_words_to_define(goal)
    
    if not words_to_define:
        definition_result = {
            "success": False,
            "error": "No words found to define. Please specify words in quotes like 'apogee' or use 'define X' format.",
            "input": goal
        }
    elif len(words_to_define) == 1:
        # Single word
        definition_result = get_word_definition(words_to_define[0])
    else:
        # Multiple words - get definitions for all
        all_definitions = []
        for word in words_to_define:
            def_result = get_word_definition(word)
            if def_result.get("success"):
                all_definitions.append(def_result)
        
        if all_definitions:
            definition_result = {
                "success": True,
                "words": words_to_define,
                "definitions": all_definitions,
                "input": goal
            }
        else:
            definition_result = {
                "success": False,
                "error": f"Could not find definitions for: {', '.join(words_to_define)}",
                "words": words_to_define,
                "input": goal
            }
    
    # Add definition result to the data
    previous_data.update({"definition": definition_result})
    return previous_data

def get_word_definition(text: str) -> dict:
    """
    Get word definition and related information from text input.
    """
    try:
        # Extract the word to define
        word = extract_word_to_define(text)
        
        if not word:
            return {
                "success": False,
                "error": "No word found to define",
                "input": text
            }
        
        # Get definition from Free Dictionary API
        definition_data = fetch_definition(word)
        
        if definition_data:
            return {
                "success": True,
                "word": word,
                "definitions": definition_data,
                "input": text
            }
        else:
            return {
                "success": False,
                "error": f"No definition found for '{word}'",
                "word": word,
                "input": text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Dictionary error: {str(e)}",
            "input": text
        }

def extract_word_to_define(text: str) -> str:
    """
    Extract the word or phrase to define from the input text.
    """
    original_text = text
    text = text.lower().strip()
    
    # First, look for quoted words/phrases (e.g., "apogee", "perigee")
    quoted_pattern = r'["\']([^"\']+)["\']'
    quoted_matches = re.findall(quoted_pattern, original_text, re.IGNORECASE)
    if quoted_matches:
        # Return the first quoted phrase, or if multiple, try to find space-related terms
        for match in quoted_matches:
            match_clean = match.strip()
            if len(match_clean) > 2 and len(match_clean.split()) <= 3:
                return match_clean
    
    # Look for patterns like "define X", "what is X", "X means", etc.
    patterns = [
        r'define\s+(?:the\s+)?(?:words?\s+)?["\']?([^"\']+?)["\']?(?:\s+and\s+["\']?([^"\']+?)["\']?)?(?:\s+means?|\s*[,.]|$)',
        r'what\s+is\s+(?:the\s+)?(?:meaning\s+of\s+)?["\']?([^"\']+?)["\']?(?:\s+means?|\s*[,.]|$)',
        r'what\s+does\s+(?:the\s+)?["\']?([^"\']+?)["\']?(?:\s+means?|\s*[,.]|$)',
        r'["\']?([^"\']+?)["\']?\s+means?',
        r'explain\s+(?:what\s+)?["\']?([^"\']+?)["\']?(?:\s+is|\s*[,.]|$)',
        r'describe\s+(?:what\s+)?["\']?([^"\']+?)["\']?(?:\s+is|\s*[,.]|$)',
        r'look\s+up\s+(?:the\s+)?(?:definition\s+of\s+)?["\']?([^"\']+?)["\']?',
        r'definition\s+of\s+["\']?([^"\']+?)["\']?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            # Clean up the extracted phrase
            extracted = re.sub(r'[^\w\s]', '', extracted)
            extracted = ' '.join(extracted.split())
            
            # Filter out common stop words at the start
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'space', 'terms', 'terminology'}
            words = extracted.split()
            filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
            
            if filtered_words:
                # Try to return up to 3 words (for phrases like "orbital mechanics")
                phrase = ' '.join(filtered_words[:3])
                if len(phrase) > 2:
                    return phrase
    
    # Fallback: remove trigger words and take first meaningful words
    trigger_patterns = [
        r'\b(define|definition|meaning|what\s+is|what\s+does|what\s+means?)\b',
        r'\b(tell\s+me\s+about|explain|describe)\b',
        r'\b(the\s+word|the\s+term)\b',
        r'\b(mean\s*\??)\b'
    ]
    
    for pattern in trigger_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    words = text.split()
    
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    filtered = [w for w in words if w not in stop_words and len(w) > 1]
    if filtered:
        # Return up to 3 words for phrases
        return ' '.join(filtered[:3])
    
    return words[0] if words else ""


def extract_words_to_define(text: str) -> list:
    """
    Extract multiple words/phrases to define from text.
    Returns a list of words to look up.
    """
    words = []
    
    # Look for quoted words (e.g., "apogee" and "perigee")
    quoted_pattern = r'["\']([^"\']+)["\']'
    quoted_matches = re.findall(quoted_pattern, text, re.IGNORECASE)
    if quoted_matches:
        for match in quoted_matches:
            # Split by "and" or comma to get multiple words
            parts = re.split(r'\s+and\s+|,\s*', match, flags=re.IGNORECASE)
            for part in parts:
                part_clean = part.strip()
                if len(part_clean) > 2:
                    words.append(part_clean)
        if words:
            return words
    
    # Look for "define X and Y" pattern
    define_pattern = r'define\s+(?:the\s+)?(?:words?\s+)?(.+?)(?:\s+means?|\s*[,.]|$)'
    match = re.search(define_pattern, text, re.IGNORECASE)
    if match:
        extracted = match.group(1).strip()
        # Remove quotes if present
        extracted = re.sub(r'["\']', '', extracted)
        # Split by "and" or comma
        parts = re.split(r'\s+and\s+|,\s*', extracted, flags=re.IGNORECASE)
        for part in parts:
            part_clean = part.strip()
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'in', 'space', 'terminology', 'terms'}
            part_words = [w for w in part_clean.split() if w.lower() not in stop_words and len(w) > 2]
            if part_words:
                words.append(' '.join(part_words[:2]))  # Max 2 words per term
    
    # If still no words, try the single word extraction
    if not words:
        single_word = extract_word_to_define(text)
        if single_word:
            words.append(single_word)
    
    return words

def fetch_definition(word: str) -> list:
    """
    Fetch word definition from Free Dictionary API.
    """
    try:
        # Use Free Dictionary API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return parse_definition_data(data)
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching definition: {e}")
        return None

def parse_definition_data(api_data: list) -> list:
    """
    Parse and format definition data from API response.
    """
    definitions = []
    
    try:
        for entry in api_data:
            word_info = {
                "word": entry.get("word", ""),
                "phonetic": entry.get("phonetic", ""),
                "phonetics": [],
                "meanings": []
            }
            
            # Extract phonetics
            for phonetic in entry.get("phonetics", []):
                if phonetic.get("text"):
                    word_info["phonetics"].append({
                        "text": phonetic.get("text", ""),
                        "audio": phonetic.get("audio", "")
                    })
            
            # Extract meanings
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "")
                meaning_info = {
                    "partOfSpeech": part_of_speech,
                    "definitions": [],
                    "synonyms": meaning.get("synonyms", []),
                    "antonyms": meaning.get("antonyms", [])
                }
                
                for definition in meaning.get("definitions", []):
                    def_info = {
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", ""),
                        "synonyms": definition.get("synonyms", []),
                        "antonyms": definition.get("antonyms", [])
                    }
                    meaning_info["definitions"].append(def_info)
                
                word_info["meanings"].append(meaning_info)
            
            definitions.append(word_info)
        
        return definitions
        
    except Exception as e:
        print(f"Error parsing definition data: {e}")
        return []

def format_definition_for_display(definition_data: dict) -> str:
    """
    Format definition data for readable display.
    """
    if not definition_data.get("success"):
        return f"❌ {definition_data.get('error', 'Unknown error')}"
    
    word = definition_data.get("word", "")
    definitions = definition_data.get("definitions", [])
    
    if not definitions:
        return f"❌ No definitions found for '{word}'"
    
    output = f"📖 **{word.upper()}**\n"
    
    for entry in definitions:
        # Add phonetic pronunciation
        if entry.get("phonetic"):
            output += f"🔊 {entry['phonetic']}\n"
        elif entry.get("phonetics"):
            phonetic_text = entry["phonetics"][0].get("text", "")
            if phonetic_text:
                output += f"🔊 {phonetic_text}\n"
        
        output += "\n"
        
        # Add meanings by part of speech
        for meaning in entry.get("meanings", []):
            part_of_speech = meaning.get("partOfSpeech", "")
            if part_of_speech:
                output += f"**{part_of_speech.upper()}**\n"
            
            # Add definitions
            for i, definition in enumerate(meaning.get("definitions", []), 1):
                def_text = definition.get("definition", "")
                example = definition.get("example", "")
                
                output += f"{i}. {def_text}\n"
                if example:
                    output += f"   *Example: {example}*\n"
            
            # Add synonyms
            synonyms = meaning.get("synonyms", [])
            if synonyms:
                output += f"📝 Synonyms: {', '.join(synonyms[:5])}\n"
            
            # Add antonyms
            antonyms = meaning.get("antonyms", [])
            if antonyms:
                output += f"🔄 Antonyms: {', '.join(antonyms[:5])}\n"
            
            output += "\n"
    
    return output.strip()

if __name__ == "__main__":
    # Test the dictionary agent
    test_cases = [
        "define apple",
        "what is the meaning of serendipity",
        "define programming",
        "what does algorithm mean"
    ]
    
    for test in test_cases:
        print(f"\nTest: {test}")
        result = run({"goal": test})
        print(f"Result: {result['definition']}")
        if result['definition'].get('success'):
            print(format_definition_for_display(result['definition']))
