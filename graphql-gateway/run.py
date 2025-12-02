import os
import logging
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.schema import schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Blog API GraphQL Gateway",
    description="GraphQL gateway for Blog REST API",
    version="1.0.0"
)

# Create GraphQL router
graphql_router = GraphQLRouter(schema, path="/graphql")

# Include GraphQL router
app.include_router(graphql_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "GraphQL Gateway",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "graphql-gateway"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('GRAPHQL_PORT', 4000))
    uvicorn.run(app, host="0.0.0.0", port=port)
