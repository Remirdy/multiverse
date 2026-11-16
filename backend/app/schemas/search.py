from pydantic import BaseModel

class WebSearchResultItem(BaseModel):
    title: str
    link: str
    snippet: str
