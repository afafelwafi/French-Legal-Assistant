# Project Setup Instructions

## 1. Environment Setup

Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  
```
On Windows: 
```
venv\Scripts\activate
```


Install dependencies:
```
pip install -r requirements.txt
```
Create a .env file with your API keys:
```
SERPAPI_API_KEY=your_serp_api_key
GROQ_API_KEY=your_groq_api_key
PISTE_API_CLIENT_ID=your_piste_api_client_id
PISTE_API_CLIENT_SECRET=your_piste_api_client_secret
HOST=your_host_for_fast_api_server
PORT= your_port_for_fast_api_server
```

## 2. Initial Commands

Extract codes and articles using pylegifrance 
```
python extractor.py
```

List available law codes:
```
python main.py --mode list-codes
```
Build indices (stored in data/indices) for all available law codes:
```
python main.py --mode build-indices
```
Or for specific law codes:
```
python main.py --mode build-indices --law-codes civil penal
```

## 3. Running the System

Start the API server:
```
python main.py --mode api
```
In a separate terminal, start the UI:
```
python main.py --mode ui
```
Open your browser and navigate to the URL shown in the terminal (typically http://localhost:7860)

## 4. Data Format Expectations
The loader expects each law code JSON file in data/legifrance/ to contain an array of legal article objects, each with at least these fields:

id: Article identifier
content: Article text content
title: Article title (optional)

Example JSON structure:
```
json[
  {
    "id": "ARTICLE_123",
    "title": "Article relatif au divorce",
    "content": "Le divorce peut être prononcé en cas..."
  },
  {
    "id": "ARTICLE_124",
    "title": "Effets du divorce",
    "content": "Le divorce a pour effet de dissoudre..."
  }
]
```
This structure allows the system to properly index and retrieve relevant legal articles for each query.