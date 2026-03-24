from pydantic import BaseModel
from typing import List, Dict, Any

class DocumentationRequest(BaseModel):
    """
    Domain Schema: Validates the incoming JSON data from the React frontend for Code Docs
    """
    code: str
    styles: List[str] = []
    custom_style: str = ""
    mode: str = "code_docs"
    user_id: str
    project_id: str = None
    file_id: str = None

class ChatRequest(BaseModel):
    """
    Domain Schema: Validates incoming Chat arrays.
    """
    messages: List[Dict[str, Any]]

class LoginRequest(BaseModel):
    """
    Domain Schema: Validates the incoming login data.
    """
    username: str
    secret_key: str
