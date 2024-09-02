# 🌊 Surfer

Voice Interface on Web Browsing [Automating Entertainment | Work] | Collaborator: @AaronGrainer

Input what you would like to do with your browser, you'd be surprised ;>

WebVoyaer in-place. Terminal Command-line Input Accepted to automate web-search.

TBD:
- Chain-up commands for self-debugging
- Chain-up commands for web-browsing and self-assignment


## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         temus_linguaforge_surfer and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src                         <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------


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
