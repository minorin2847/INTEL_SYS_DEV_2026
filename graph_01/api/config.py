"""Settings for the Diabetes KG API (environment variables with local defaults)."""
import os

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "diabetes123")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

DIABETES_TYPES = ["Đái tháo đường", "Đái tháo đường type 1", "Đái tháo đường type 2",
                  "Đái tháo đường thai kỳ", "Tiền đái tháo đường"]
MAX_HOPS = 4            # path finder search depth
MAX_FACTS = 200         # cap on facts returned for one entity
