# 🌊 Surfer

Voice Interface on Web Browsing [Automating Entertainment | Work] | Collaborator: @AaronGrainer

Input what you would like to do with your browser, you'd be surprised ;>

WebVoyaer in-place. Terminal Command-line Input Accepted to automate web-search.

TBD:
- Chain-up commands for self-debugging
- Chain-up commands for web-browsing and self-assignment


## Setup & Installation

1. Sign up and get API Keys from LangSmith, OpenAI and Gladia

   - https://smith.langchain.com/
   - https://platform.openai.com/
   - https://app.gladia.io/

2. Create a `.env` file and populate:

```.env
LANGCHAIN_API_KEY="ls__xxx"
OPENAI_API_KEY="sk-xxx"
GLADIA_API_KEY="xxx-xxx"
```

3. Create environment and install neccesary packages

```bash
make install
pip install -r requirements.txt
```

## Running it 

```bash
python surf.py
```
