"""
Burmese Rhyme Chain Extractor
==============================

This module extracts rhyme chain schemes from Burmese poems.
Input: Poem string
Output: Top 3 most possible rhyme scheme numbers

Based on RhymeChainExtraction.ipynb
"""

import re
from collections import Counter, defaultdict

# ==============================================================================
# Constants and Core Functions
# ==============================================================================
# A list of all Burmese consonants (including the great 'အ')
# This is used to distinguish consonants from vowels/diacritics.
# --- Constants ---
BURMESE_CONSONANTS = "ကခဂဃငစဆဇဈညဋဌဍဎဏတထဒဓနပဖဗဘမယရလဝသဟဠအ"
# Consonantal medials (part of the onset)
CONSONANTAL_MEDIALS = "ျြှွ" 


RIME_NORMALIZATION_MAP = {
    # -at sound (အက်)
    "တ်": "က်", "ပ်": "က်",  
    # -it sound (အိက်)
    "ိတ်": "ိက်", "ိပ်": "ိက်", "ိစ်": "ိက်",
    # -ut sound (အုတ်)
    "ုတ်": "ုပ်",
    # -et sound (အက်)
    "က်": "က်",
    # -an sound (အန်)
    "မ်": "န်",
    # -in sound (အိန်)
    "ိမ်": "ိန်",
    # -un sound (အုန်)
    "ုန်": "ိန်",
    # Special finals
    "ဉ်": "န်", # Sounds like -an
    "ည်": "ယ်", # Sounds like -ay
    "ယ့်": "ဲ့"
}
def custom_syllable_splitter(text: str) -> list:
    """
    Performs a deep syllable split by breaking down all consonant stacks.
    This function uses a two-step process to achieve the required logic for
    cases like 'နက္ခတ္တ' and 'ဥက္ကဋ္ဌ'.
    """

    
    # --- Step 1: Pre-processing to split stacks using a loop ---
    # This loop is the only reliable way to handle chained stacks.
    stacked_consonant_pattern = r'([က-အ])(်?္)([က-အ])'
    processed_text = text
    while re.search(stacked_consonant_pattern, processed_text):
        processed_text = re.sub(stacked_consonant_pattern, r'\1်'  + r'\3', processed_text)
    processed_text = re.sub(r"(([A-Za-z0-9]+)|[က-အ|ဥ|ဦ](င်္|[က-အ|ဥ][ှ]*[့း]*[်]|္[က-အ]|[ါ-ှႏꩻ][ꩻ]*){0,}|.)",r"\1 ", processed_text)
    
    # Step 2: Tokenization of the processed parts ---
    # The string is now clean of stacks, so we can tokenize it reliably.
    final_list = processed_text.split(" ")
    
    # Filter out empty strings caused by trailing spaces
    final_list = [word for word in final_list if word.strip()]
        
    return final_list


def _get_onset_length(word: str) -> int:
    """Finds the length of the initial consonant cluster (onset)."""
    if not word or word[0] not in BURMESE_CONSONANTS:
        return 0
    
    onset_len = 1
    # Greedily consume any following consonantal medials
    while onset_len < len(word) and word[onset_len] in CONSONANTAL_MEDIALS:
        onset_len += 1
    return onset_len

def get_poetic_rime(word: str) -> str:
    """Extract the phonetically normalized rhyme part of a Burmese word."""
    onset_len = _get_onset_length(word)
    rime = word[onset_len:]
    if not rime:
        return ""
    # Vowel normalization
    rime = rime.replace('ါ', 'ာ')
    # Phonetic normalization
    return RIME_NORMALIZATION_MAP.get(rime, rime)

# ==============================================================================
# Rhyme Scheme Detection Functions
def find_dominant_scheme_in_stanza(stanza_text: str, stanza_number: int = None, verbose: bool = True):
    """
    Analyzes a stanza to find the longest consecutive rhyme chain and reports
    its positional scheme.
    Returns the scheme string or None if no scheme found.
    """
    if verbose and stanza_number:
        print(f"\n--- Stanza {stanza_number} ---")
    
    lines = [line.strip() for line in stanza_text.split('၊') if line.strip()]
    if len(lines) < 2:
        if verbose:
            print("Not enough lines to determine a scheme.")
        return None

    syllables_by_line = [custom_syllable_splitter(line) for line in lines]
    best_chain = []

    # --- Recursive helper function to find the longest path ---
    def find_longest_path_from(line_index, rime_to_match):
        # Base case: if we're past the last line, the path ends.
        if line_index >= len(syllables_by_line):
            return []

        longest_sub_path = []
        # Find all possible next steps in the current line
        for syllable_index, word in enumerate(syllables_by_line[line_index]):
            if get_poetic_rime(word) == rime_to_match:
                # Explore the path from this point onwards
                path = find_longest_path_from(line_index + 1, rime_to_match)
                # If this path is better than what we've found so far for this level, keep it
                if len(path) > len(longest_sub_path):
                    longest_sub_path = path
        
        # Find the position of the best starting point for the longest sub-path
        best_start_pos = -1
        for syllable_index, word in enumerate(syllables_by_line[line_index]):
             if get_poetic_rime(word) == rime_to_match:
                 path = find_longest_path_from(line_index + 1, rime_to_match)
                 if len(path) == len(longest_sub_path):
                     best_start_pos = syllable_index
                     break
        
        if best_start_pos != -1:
            word_info = (syllables_by_line[line_index][best_start_pos], best_start_pos + 1)
            return [word_info] + longest_sub_path
        return []

    # --- Main logic to start the search ---
    # Try starting a chain from every syllable in the first line
    for start_idx, start_word in enumerate(syllables_by_line[0]):
        rime = get_poetic_rime(start_word)
        if not rime:
            continue
        
        # Find the longest possible chain starting with this rime
        path = find_longest_path_from(1, rime)
        
        # Prepend the starting word and its position
        current_chain = [(start_word, start_idx + 1)] + path
        
        # If this chain is the best one found so far, save it
        if len(current_chain) > len(best_chain):
            best_chain = current_chain

    # Report the results
    if len(best_chain) >= 2:
        positions = [pos for word, pos in best_chain]
        words = [word for word, pos in best_chain]
        scheme_str = '-'.join(map(str, positions))
        
        if verbose:
            print(f"✅ Found a rhyme scheme: ({scheme_str})")
            print(f"   - Rime Group: '{get_poetic_rime(words[0])}'")
            print(f"   - Rhyming Words: {', '.join(words)}")
        
        return scheme_str
    else:
        if verbose:
            print("❌ No dominant consecutive rhyme scheme found.")
        return None

def analyze_poem_for_scheme(poem_string: str):
    """Main function to analyze a poem's positional rhyme scheme stanza by stanza."""
    print("=" * 50)
    print("📜 Positional Rhyme Scheme Analysis")
    print("=" * 50)
    clean_poem = poem_string.strip()
    stanzas = [s.strip() for s in clean_poem.split('။') if s.strip()]
    for i, stanza_text in enumerate(stanzas):
        find_dominant_scheme_in_stanza(stanza_text, i + 1)
    print("\n" + "=" * 50)

def extract_all_rhyme_schemes(poem_string: str):
    """
    Extract all rhyme schemes from a poem without verbose output.
    
    Args:
        poem_string (str): The input poem text
        
    Returns:
        list: All rhyme schemes found in the poem
    """
    if not poem_string or not poem_string.strip():
        return []
    
    clean_poem = poem_string.strip()
    stanzas = [s.strip() for s in clean_poem.split('။') if s.strip()]
    
    all_schemes = []
    for stanza_text in stanzas:
        scheme = find_dominant_scheme_in_stanza(stanza_text, verbose=False)
        if scheme:
            all_schemes.append(scheme)
    
    return all_schemes

def get_top_3_rhyme_schemes(poem_string: str):
    """
    Get the top 3 most frequent rhyme schemes from a poem.
    
    Args:
        poem_string (str): The input poem text
        
    Returns:
        dict: Contains top_3_schemes, all_schemes, scheme_counts, and statistics
    """
    if not poem_string or not poem_string.strip():
        return {
            'top_3_schemes': [],
            'all_schemes': [],
            'scheme_counts': {},
            'total_stanzas': 0,
            'stanzas_with_schemes': 0
        }
    
    # Extract all schemes
    all_schemes = extract_all_rhyme_schemes(poem_string)
    
    # Count scheme frequencies
    scheme_counts = Counter(all_schemes)
    
    # Get top 3 most common schemes
    top_3_schemes = scheme_counts.most_common(3)
    
    # Calculate statistics
    clean_poem = poem_string.strip()
    total_stanzas = len([s.strip() for s in clean_poem.split('။') if s.strip()])
    
    return {
        'top_3_schemes': top_3_schemes,  # List of (scheme, count) tuples
        'all_schemes': all_schemes,      # All schemes found
        'scheme_counts': dict(scheme_counts),  # All scheme counts as dict
        'total_stanzas': total_stanzas,
        'stanzas_with_schemes': len(all_schemes)
    }

def get_most_likely_rhyme_scheme(poem_string: str):
    """
    Get the single most likely rhyme scheme from a poem.
    
    Args:
        poem_string (str): The input poem text
        
    Returns:
        str: The most frequent rhyme scheme, or "None" if no scheme found
    """
    result = get_top_3_rhyme_schemes(poem_string)
    
    if result['top_3_schemes']:
        return result['top_3_schemes'][0][0]  # Return the most frequent scheme
    else:
        return "None"

def analyze_poem_rhyme_schemes(poem_string: str, verbose: bool = True):
    """
    Complete analysis of rhyme schemes in a poem with top 3 results.
    
    Args:
        poem_string (str): The input poem text
        verbose (bool): Whether to print detailed analysis
        
    Returns:
        dict: Complete analysis results with top 3 schemes
    """
    result = get_top_3_rhyme_schemes(poem_string)
    
    if verbose:
        print("=" * 60)
        print("🎵 Burmese Poem Rhyme Scheme Analysis - Top 3")
        print("=" * 60)
        print(f"📊 Total stanzas: {result['total_stanzas']}")
        print(f"📊 Stanzas with detectable schemes: {result['stanzas_with_schemes']}")
        
        if result['top_3_schemes']:
            print(f"\n🏆 Top 3 Most Common Rhyme Schemes:")
            for i, (scheme, count) in enumerate(result['top_3_schemes'], 1):
                percentage = (count / result['stanzas_with_schemes']) * 100 if result['stanzas_with_schemes'] > 0 else 0
                print(f"  {i}. {scheme} (appears {count} times, {percentage:.1f}%)")
            
            print(f"\n🥇 Most likely scheme: {result['top_3_schemes'][0][0]}")
        else:
            print("\n❌ No rhyme schemes detected in the poem.")
        
        print("\n" + "=" * 60)
    
    return result






