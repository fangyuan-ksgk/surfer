# 🌊 Surfer

Voice Interface on Web Browsing

Input what you would like to do with your browser, you'd be surprised ;>

WebVoyaer in-place. Terminal Command-line Input Accepted to automate web-search.
TBD:

- Whisper Voice input instead

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
```

## Running it

```bash
make run
```
