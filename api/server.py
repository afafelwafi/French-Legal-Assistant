# api/server.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import time
from agents.multi_agent import create_multi_agent
from agents.search_agent import create_search_tool
from agents.rag_agent import create_rag_tool
from data.loader import LegalDataLoader
from utils.cache import RedisCache
from utils.logging import app_logger, RequestLogMiddleware

# Create FastAPI app
app = FastAPI(
    title="French Legal Assistant API",
    description="API for answering legal questions in French",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLogMiddleware)

# Create Redis cache
cache = RedisCache(prefix="legal_assistant")


# Define request models
class QueryRequest(BaseModel):
    query: str
    law_codes: List[str] = ["civil", "penal"]
    use_search: bool = True
    use_rag: bool = True
    verbose: bool = False


# Define response models
class QueryResponse(BaseModel):
    query: str
    direct_answer: Optional[str] = None
    multi_agent_answer: Optional[str] = None
    processing_time: float = 0.0
    cached: bool = False


# Store loaded agents
agent_cache = {}


# Define routes
@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest, req: Request):
    """
    Query the legal assistant.
    """
    start_time = time.time()

    # Create cache key parameters
    cache_key = {
        "query": request.query,
        "law_codes": sorted(request.law_codes),
        "use_search": request.use_search,
        "use_rag": request.use_rag,
    }

    # Try to get from cache
    cached_response = cache.get(cache_key)
    if cached_response:
        app_logger.info(f"Cache hit for query: {request.query[:50]}...")
        response_data = json.loads(cached_response)
        response_data["cached"] = True
        response_data["processing_time"] = time.time() - start_time
        return QueryResponse(**response_data)

    app_logger.info(f"Cache miss for query: {request.query[:50]}...")

    try:
        # Initialize tools
        tools = []

        # Add search tool if requested
        if request.use_search:
            tools.append(create_search_tool())

        # Add RAG tools for each law code
        if request.use_rag:
            for law_code in request.law_codes:
                # Load documents if needed
                try:
                    loader = LegalDataLoader(law_code)
                    documents = await loader.load()

                    # Create RAG tool
                    rag_tool = create_rag_tool(law_code, documents)
                    tools.append(rag_tool)
                except Exception as e:
                    app_logger.error(f"Error loading law code {law_code}: {str(e)}")
                    raise HTTPException(
                        status_code=500, detail=f"Error loading law code {law_code}"
                    )

        # Create agent
        agent_key = (
            f"{','.join(request.law_codes)}-{request.use_search}-{request.use_rag}"
        )
        if agent_key not in agent_cache:
            agent_cache[agent_key] = create_multi_agent(tools, request.verbose)

        agent = agent_cache[agent_key]

        # Get direct answer
        direct_answer = None

        from models.llm import GroqLLM

        llm = GroqLLM()
        direct_answer = llm(request.query)

        # Get multi-agent answer
        multi_agent_answer = None
        if tools:
            try:
                multi_agent_answer = agent.run(request.query)
            except Exception as e:
                app_logger.error(f"Error in multi-agent: {str(e)}")
                multi_agent_answer = f"Error: {str(e)}"

        # Create response
        response = QueryResponse(
            query=request.query,
            direct_answer=direct_answer,
            multi_agent_answer=multi_agent_answer,
            processing_time=time.time() - start_time,
            cached=False,
        )

        # Cache the response
        cache.set(cache_key, json.dumps(response.dict()))

        return response

    except Exception as e:
        app_logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok", "timestamp": time.time()}


@app.post("/api/cache/flush")
async def flush_cache():
    """
    Flush the cache.
    """
    count = cache.flush()
    return {"status": "ok", "flushed": count}
