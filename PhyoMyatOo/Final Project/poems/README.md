# Burmese Poem Classification Project

This project implements a deep learning-based classification system for Burmese poems, capable of distinguishing between modern poems, traditional poems, and traditional songs. For traditional poems, it also analyzes their structural characteristics like rhyme schemes, line numbers, and stanzas.

## Project Overview

The project uses a combination of OCR, AI-assisted extraction (using Gemini), manual editing tools, and deep learning models to process and classify Burmese poems.

### Classification Pipeline

1. **Data Extraction (OCR)**
   - Extract raw text from Burmese poem books using OCR technology (https://github.com/PhilixTheExplorer/ocr_text_extractor)
   - Source poems are stored in the `PoemSource` directory

2. **Poem Extraction with Gemini**
   - Process the OCR output using Gemini to accurately identify and extract poems
   - Results are stored in JSON format in `PoemJsonFiles`

3. **Manual Editing**
   - Use the custom `poem_editor.py` tool for manual verification and correction
   - Edited poems are saved in `Poem_Editor/EditedPoems`

4. **Model Training**
   - Train deep learning models to classify poems into three categories:
     - Modern poems
     - Traditional poems
     - Traditional songs
     
   - Two approaches implemented:
     - Character-based tokenization (`burmese_poem_classifier_dl_Char_tokenizer.ipynb`)
     - Syllable-based tokenization (`burmese_poem_classifier_dl_with_Syllable_tokenizer.ipynb`)

5. **Traditional Poem Analysis**
   For poems classified as traditional:
   - Extract rhyme schemes
   - Count line numbers
   - Analyze stanza structure
   - Compare against rule-based library for verification

## Project Structure

```
poems/
├── Poem_Editor/                  # Manual poem editing tool
│   ├── EditedPoems/             # Storage for manually verified poems
│   ├── poem_editor.py           # Editor implementation
│   └── poem_editor_settings.json # Editor configuration
├── PoemJsonFiles/               # Extracted and processed poems in JSON format
├── PoemSource/                  # Original source poems
├── Rule_based/                  # Rule-based analysis notebooks
│   ├── Custom_tokenization_for_Poem.ipynb
│   ├── RhymeChainExtraction.ipynb
│   └── ThanBouk.ipynb
├── burmese_poem_classifier_dl_Char_tokenizer.ipynb    # Character-based model
└── burmese_poem_classifier_dl_with_Syllable_tokenizer.ipynb  # Syllable-based model
```

## Setup and Installation

1. **Environment Setup**
   ```bash
   # Using pipenv
   pipenv install
   pipenv shell
   ```

2. **Dependencies**
   The project uses Pipenv for dependency management. Key dependencies are listed in `Pipfile`.

## Usage

1. **Poem Editor**
   ```bash
   python Poem_Editor/poem_editor.py
   ```

2. **Model Training**
   - Open and run either of the classifier notebooks:
     - `burmese_poem_classifier_dl_Char_tokenizer.ipynb`
     - `burmese_poem_classifier_dl_with_Syllable_tokenizer.ipynb`

3. **Rule-based Analysis**
   - Notebooks in the `Rule_based` directory provide tools for analyzing traditional poem structures

## Data

The project includes various Burmese poem collections in JSON format, stored in `PoemJsonFiles/`. These include:
- Modern poetry collections
- Traditional poetry collections
- Folk songs and traditional songs
- Children's poems
- Love poems
- Various themed collections

# Future Work
1. Adding more poem collections
2. Improving the classification models
3. Enhancing the rule-based analysis
4. Optimizing the poem editor


