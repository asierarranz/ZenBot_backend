# ZenBot Backend

ZenBot is an AI-driven application designed to generate Yoga Nidra meditations with background GenAI music and a calming AI-generated human voice. This README provides a guide to set up the backend of ZenBot, including installation instructions, main functionalities, and file structure.

## Installation

Follow these steps to set up the backend environment:

1. **Create a Conda Environment**

    ```bash
    conda create -n ZenBot_Backend python=3.12
    conda activate ZenBot_Backend
    ```

2. **Clone the Project Repository**

    ```bash
    git clone <repository-url>
    cd ZenBot_Backend
    ```

3. **Install the Required Packages**

    Make sure you have a `requirements.txt` file in the project directory with the necessary dependencies. Then, run:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a `.env` file in the project directory with the following content:

    ```env
    GPT_API_KEY=your_openai_api_key
    ELEVEN_LABS_API_KEY=your_eleven_labs_api_key
    TEST_MODE=False
    ```

## File Structure

The project structure is as follows:

```plaintext
ZenBot_Backend/
├── static/
│   ├── (provisions for genai_music files)
├── templates/
│   └── index.html
├── app.py
├── utils.py
├── requirements.txt
└── .env
```

## Main Flask Files and Functions

### `app.py`

- **Purpose**: Initializes the Flask app, handles routes, and manages session data.
- **Key Functions**:
  - `index()`: Renders the main form for input, processes form submissions, and displays generated meditations.
  - `generate_meditation()`: API endpoint to handle meditation generation requests via POST.

### `utils.py`

- **Purpose**: Contains utility functions for generating meditation scripts and audio files.
- **Key Functions**:
  - `generate_meditation_script(prompt)`: Sends a request to OpenAI's GPT-4 to generate a meditation script based on the input prompt.
  - `generate_audio(script, prompt)`: Sends the generated script to Eleven Labs to create an audio file mimicking a calming human voice.
  - `mix_with_background_music(audio_path, output_dir, filename)`: Mixes the generated audio with a randomly selected background music file. (This will be connected to the Suno API in next iterations)


## Running the Application

1. **Start the Flask App**

    In the project directory, run:

    ```bash
    python app.py
    ```

2. **Access the Application**

    Open your web browser and navigate to `http://localhost:5000` to access the ZenBot application.

3. **Breathe and Meditate**

    Take a deep breath, relax, and let ZenBot guide you through a personalized Yoga Nidra meditation experience. Enjoy the soothing combination of AI-generated scripts and calming background music!
