# mini-Rag

this project can answer user for documents 

## Requirments:

Pyton version: 3.8 or later

install Miniconda

# How to install

open termanl and write:

> conda create -n mini-rag

activate environment:

> conda activate mini-rag

# Installation

> pip install -r requirments.txt

> add file ".env" and copy text from ".env.example" and add your openai key

# Run Reload

uvicorn main:app --reload --host 0.0.0.0 --port 5001
