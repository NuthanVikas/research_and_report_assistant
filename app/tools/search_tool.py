import os

from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from pydantic import SecretStr

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise RuntimeError(
        "TAVILY_API_KEY is not set. Add it to your .env file to enable the Tavily search tool."
    )

api_wrapper = TavilySearchAPIWrapper(tavily_api_key=SecretStr(TAVILY_API_KEY))
search_tool = TavilySearchResults(api_wrapper=api_wrapper)
