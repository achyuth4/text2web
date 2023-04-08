"""Website generator using OpenAI's API. http://localhost:3998/"""

import os
import uuid
import flask
import openai

from dotenv import load_dotenv
load_dotenv()

app = flask.Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

BASE_PROMPT = """The following is a AI website generator.
The human will input a prompt, and the AI will generate a website based entirely based on HTML,
with style and script tags for including JS and CSS.
The AI should make sure the text color is white on dark mode websites, and the opposite for light mode websites.
Additionally, the AI should produce minified HTML, CSS, and JS code.
Also make sure the same font is used on all elements throughout the website, unless the human specifies otherwise.
Use transitions, round corners, and shadows, but don't overdo it.
When corners etc. are rounded, make sure all corners are rounded by the same amount and so on.
Make sure the website is responsive and supports dark mode using the media query.
Don't add any gradients, unless the human specifies otherwise.
Add as many elements as it makes sense to, but don't overdo it.
Make sure all elements are aligned and centered properly.

The AI makes sure all wishes of the human are fulfilled, and the website looks very nice and modern.

***

Human: simple link tree - my IG, Twitter, YT are all @neonblade7, my github is nbl8. The background is https://cdn.pixabay.com/photo/2017/01/25/10/39/ninja-2007576_1280.jpg. The font can be modern. add a red gradient. also show the song https://open.spotify.com/track/0iUrxveyNUBfj0cqjYEijt?si=16c441eaf7424a9d
AI: LINKTREE
Human: cool and simple dark mode homepage in a cyberpunk/hacker style. Make it link my github @aldecaldos as well.  
AI: HOMEPAGE
Human: a simple search engine called searchie. make it dark mode and very very clean and modern with a purple gradient.
AI: SEARCH
Human: """

for demo in ['linktree', 'homepage', 'search']:
    BASE_PROMPT = BASE_PROMPT.replace(demo.upper(), open(f'training/{demo}.html', encoding='utf8').read())

END_PROMPT = '\nAI: '

def respond(prompt):
    """Use AI to generate a possible solution."""

    full_prompt = BASE_PROMPT + prompt + END_PROMPT
    try:
        response = openai.Completion.create(
            model='text-davinci-003',
            n=1,
            prompt=full_prompt,
            temperature=0,
            max_tokens=1024,
            #top_p=1,
            # frequency_penalty=0,
            # presence_penalty=0.6,
            stop=None#[' Human:', ' AI:']
        )
    except Exception as error:
        return f'<span color="red">{error}</span>'

    response = response.choices[0].text or '<span color="red">No response.</span>'

    return f'<script>console.info("{prompt}")</script>{response}'

@app.route('/')
def index():
    """Home page."""
    return flask.render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate a page from a prompt."""
    prompt = flask.request.get_json()['input']
    html = respond(prompt)
    page_id = uuid.uuid4().hex

    with open(f'generated/{page_id}.html', 'w', encoding='utf8') as f:
        f.write(html)

    return page_id

@app.route('/view/<page_id>')
def view_page(page_id):
    """View a generated page."""
    if page_id == 'empty':
        return '<span style="font-family: Arial, Helvetica, sans-serif;">Type a prompt to generate a website above and press the button to get started.</span>'

    if page_id == 'loading':
        return '<img style="height:50px;width:50px;" src="/static/loading.svg" alt="Loading..."/>'

    try:
        return open(f'generated/{page_id}.html', 'r', encoding='utf8').read()
    except KeyError:
        return '<span color="red">Invalid page ID.</span>'

app.run(port=3998, debug=True)
