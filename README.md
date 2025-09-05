# 🎧 Local PDF-to-Audiobook (Kokoro TTS)

Convert any PDF into a **structured audiobook** locally using [Kokoro TTS](https://github.com/hexgrad/kokoro).
This pipeline extracts clean text from a PDF, splits it into manageable **chunks**, and then synthesizes natural-sounding audio for each chunk.

No cloud calls — everything runs **entirely offline**.

---

## ✨ Features

* 📄 Extracts raw text from PDFs
* 🧹 Cleans and normalizes text (fixes line breaks, punctuation, spacing)
* ✂️ Splits text into sentence-based chunks for smoother TTS
* 🔊 Generates `.wav` files using Kokoro TTS locally
* 🗂️ Produces structured JSON mapping chapters → chunks → audio

---

## 📂 Project Structure

```
.
├─ Preprocess.py         # Extract + clean PDF → JSON chunks
├─ Tts.py                # Convert JSON chunks → audio files
├─ models/               # Local Kokoro model + voice files
│   ├─ kokoro-v1_0.pth
│   └─ voices/
│       └─ bf_isabella.pt
├─ a.pdf                 # Example input book
├─ a.json                # Extracted raw PDF text
├─ atomic-habits-chunks.json # Example preprocessed chunked JSON
├─ output_audio/         # Final generated audio files
└─ temp_audio/           # Test runs / individual chunks
```

---

## 🛠️ Requirements

* Python **3.9+**
* [kokoro](https://pypi.org/project/kokoro/)
* **PyTorch** (for loading `.pth` models)
* **soundfile** (for writing `.wav`)
* **pdfplumber** (for PDF text extraction)
* **nltk** (sentence tokenization)
* **wordninja** (optional word splitting for merged tokens)

---

## ⚙️ Installation

```bash
# Clone this repo
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# Create environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install torch kokoro soundfile pdfplumber nltk wordninja numpy
```

Also download **NLTK punkt tokenizer** (done automatically in `Preprocess.py`, but you can pre-run it):

```python
import nltk
nltk.download("punkt")
```

## 🔧 Model Setup (Local Only)

This project **does not auto-download Kokoro models**.
Instead, we use the copy that Kokoro normally caches from Hugging Face.

1. Install `kokoro` once to let it download the model:

   ```bash
   pip install kokoro
   ```

   This will place files in your Hugging Face cache (e.g. `~/.cache/huggingface/`).

2. Copy the model + voice files from the cache into your repo, for example:

   ```
   models--hexgrad--Kokoro-82M/
   └─ snapshots/
      └─ <hash>/
          ├─ kokoro-v1_0.pth          # model
          └─ voices/
              ├─ bf_isabella.pt
              └─ ...
   ```

3. In `Tts.py`, the pipeline is created with:

   ```python
   # create empty pipeline so it doesn’t try to download
   quie_pl = KPipeline(lang_code="a", model=False)

   # then explicitly load local model
   pipeline = KPipeline(
       lang_code="a",
       model="models--hexgrad--Kokoro-82M/snapshots/<hash>/kokoro-v1_0.pth"
   )

   voice_path = "models--hexgrad--Kokoro-82M/snapshots/<hash>/voices/bf_isabella.pt"
   ```

This ensures the program always uses **your local copy** of the model and voices, with **no network access** required.

---

## 🚀 Usage

### 1. Convert PDF → raw JSON

Extracts page text into a JSON array:

```bash
python Preprocess.py
```

By default, it runs:

```python
pdf_to_json("a.pdf", "a.json")
```

---

### 2. Preprocess JSON → chapter chunks

Clean the raw text and split into 2-sentence chunks:

```python
from Preprocess import preprocess_book_into_chunks

preprocess_book_into_chunks("a.json", "atomic-habits-chunks.json", sentences_per_chunk=2)
```

---

### 3. Generate audiobook chunks

Convert the chunked JSON into `.wav` files:

```python
from Tts import chunk_tts_from_json, pipeline, voice_path

chunk_tts_from_json(
    "atomic-habits-chunks.json",
    pipeline,
    voice_path,
    output_dir="output_audio"
)
```

Each chunk is saved as a `.wav` file, named according to its chunk ID (e.g., `ch1_001.wav`).

---

### 4. Test with a single chunk

```python
from Tts import generate_individual_chunk

generate_individual_chunk(
    "test.wav",
    "This is a quick test of Kokoro TTS running locally."
)
```

---

## 🧪 Example Workflow

```bash
# 1. Extract PDF pages → JSON
python Preprocess.py

# 2. (Optional) Clean and chunk the text
python -c "from Preprocess import preprocess_book_into_chunks; preprocess_book_into_chunks('a.json', 'atomic-habits-chunks.json', 2)"

# 3. Convert chunks → audio
python -c "from Tts import chunk_tts_from_json, pipeline, voice_path; chunk_tts_from_json('atomic-habits-chunks.json', pipeline, voice_path, 'output_audio')"
```

---

## 📜 JSON Format

The preprocessed JSON has a **chapter → chunk** hierarchy:

```json
{
  "chapter_1": {
    "chunk_1": {
      "id": "ch1_001",
      "text": "The first two sentences of the chapter.",
      "wav_audio": "ch1_001.wav"
    },
    "chunk_2": {
      "id": "ch1_002",
      "text": "The next two sentences...",
      "wav_audio": "ch1_002.wav"
    }
  },
  "chapter_2": { ... }
}
```

---

## 🎧 Output

* Clean `.wav` files per chunk stored in `output_audio/`
* Can be concatenated or played sequentially to form a full audiobook

---

## 🔒 Privacy

* Everything runs **locally**.
* No internet access is required after downloading the Kokoro model & voices.

---

## 🗺️ Roadmap

* [ ] Support EPUB and DOCX input
* [ ] Concatenate all chapter audio into a single audiobook file
* [ ] Add CLI for one-command PDF → audiobook
* [ ] Support more voices & multi-language

---

## 🙏 Acknowledgements

* [Kokoro TTS](https://github.com/hexgrad/kokoro) for the TTS models
* [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF parsing
* [nltk](https://www.nltk.org/) for sentence tokenization
