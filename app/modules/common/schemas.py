from pydantic import BaseModel, Field

class SearchCompanyKnowledgeInput(BaseModel):
    """Input schema for searching company knowledge."""
    query: str = Field(
        ...,
        description="The search query related to company FAQs, policies, or general knowledge."
    )
