from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from utils import generate_meditation_script, generate_audio
from dotenv import load_dotenv
from markupsafe import Markup
import os
import random
import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key

# Define FlaskForm for the meditation input
class MeditationForm(FlaskForm):
    prompt = TextAreaField(
        'Enter the topic for your meditation:',
        validators=[DataRequired()],
        render_kw={"placeholder": "Suggested topics: stressed about your NVIDIA boss, your GPU is not fast enough, debugging CUDA code, optimizing AI models"}
    )
    submit = SubmitField('Generate Meditation')

# List of spiritual quotes to display randomly
spiritual_quotes = [
    "The mind is everything. What you think you become. - Buddha",
    "Peace comes from within. Do not seek it without. - Buddha",
    "What we think, we become. - Buddha",
    "The only real failure in life is not to be true to the best one knows. - Buddha",
    "Health is the greatest gift, contentment the greatest wealth, faithfulness the best relationship. - Buddha",
    "Do not dwell in the past, do not dream of the future, concentrate the mind on the present moment. - Buddha",
    "Three things cannot be long hidden: the sun, the moon, and the truth. - Buddha",
    "Live as if you were to die tomorrow. Learn as if you were to live forever. - Mahatma Gandhi",
    "The best way to find yourself is to lose yourself in the service of others. - Mahatma Gandhi",
    "The weak can never forgive. Forgiveness is the attribute of the strong. - Mahatma Gandhi",
    "An eye for an eye only ends up making the whole world blind. - Mahatma Gandhi",
    "Happiness is when what you think, what you say, and what you do are in harmony. - Mahatma Gandhi",
    "You must be the change you wish to see in the world. - Mahatma Gandhi",
    "Strength does not come from physical capacity. It comes from an indomitable will. - Mahatma Gandhi"
]

# Function to format timestamp
def format_timestamp(timestamp):
    dt = datetime.datetime.strptime(timestamp, "%Y%m%d%H%M")
    return dt.strftime("%B %d, %Y at %I:%M %p")

# Main route to render and process the meditation form
@app.route('/', methods=['GET', 'POST'])
def index():
    form = MeditationForm()
    quote = random.choice(spiritual_quotes)
    if 'previous_generations' not in session:
        session['previous_generations'] = []

    if form.validate_on_submit():
        prompt = form.prompt.data
        gpt_response = generate_meditation_script(prompt)
        if not gpt_response:
            flash('Failed to generate meditation script', 'danger')
            return render_template('index.html', form=form, quote=quote, previous_generations=session['previous_generations'])

        audio_path = generate_audio(gpt_response, prompt)
        if not audio_path:
            flash('Failed to generate audio', 'danger')
            return render_template('index.html', form=form, quote=quote, previous_generations=session['previous_generations'])

        audio_filename = os.path.basename(audio_path)
        first_words = " ".join(audio_filename.split('_')[1:5])
        timestamp = audio_filename.split('_')[-1].split('.')[0]
        formatted_time = format_timestamp(timestamp)

        download_link = url_for('static', filename=audio_filename)
        flash(Markup(f'Meditation generated successfully! <a href="{download_link}" download>Download it from here ({first_words})</a>'), 'success')

        session['previous_generations'].append({'filename': audio_filename, 'first_words': first_words, 'timestamp': formatted_time})
        session.modified = True

        return redirect(url_for('index'))
    
    return render_template('index.html', form=form, quote=quote, previous_generations=session['previous_generations'])

# API endpoint to generate meditation via POST request
@app.route('/generate_meditation', methods=['POST'])
def generate_meditation():
    data = request.json
    prompt = data.get('prompt', '')

    gpt_response = generate_meditation_script(prompt)
    if not gpt_response:
        return jsonify({'error': 'Failed to generate meditation script'}), 500
    
    audio_path = generate_audio(gpt_response, prompt)
    if not audio_path:
        return jsonify({'error': 'Failed to generate audio'}), 500

    audio_filename = os.path.basename(audio_path)
    first_words = " ".join(audio_filename.split('_')[1:5])
    timestamp = audio_filename.split('_')[-1].split('.')[0]
    formatted_time = format_timestamp(timestamp)

    download_link = url_for('static', filename=audio_filename)
    session['previous_generations'].append({'filename': audio_filename, 'first_words': first_words, 'timestamp': formatted_time})
    session.modified = True

    return jsonify({'audio_url': download_link, 'first_words': first_words, 'timestamp': formatted_time})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
