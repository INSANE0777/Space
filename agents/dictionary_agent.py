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
    definition_result = get_word_definition(goal)
    
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
    Extract the word to define from the input text.
    """
    # Clean the text
    text = text.lower().strip()
    
    # Remove trigger words and common phrases
    trigger_patterns = [
        r'\b(define|definition|meaning|what\s+is|what\s+does|what\s+means?)\b',
        r'\b(tell\s+me\s+about|explain|describe)\b',
        r'\b(the\s+word|the\s+term)\b',
        r'\b(mean\s*\??)\b'
    ]
    
    for pattern in trigger_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up extra spaces and punctuation
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    
    # Extract the word - take the first meaningful word
    words = text.split()
    
    # Filter out common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    for word in words:
        if word not in stop_words and len(word) > 1:
            return word
    
    # If all words are stop words, return the first one anyway
    return words[0] if words else ""

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
