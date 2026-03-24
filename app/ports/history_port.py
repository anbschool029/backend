from abc import ABC, abstractmethod

class HistoryPort(ABC):
    """
    Port (Interface) handling persistence of App History.
    Now updated to support project-level and file-level management flows.
    """
    
    @abstractmethod
    async def create_generate_docs_history(self, code: str, styles: str, custom_style: str, result: str, user_id: str, project_id: str = None, file_id: str = None) -> str:
        """Saves GenDocs payload and returns the UUID."""
        raise NotImplementedError
        
    @abstractmethod
    async def create_explain_history(self, code: str, styles: str, custom_style: str, result: str, user_id: str, project_id: str = None, file_id: str = None) -> str:
        """Saves Explain payload and returns the UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_docs_history(self, history_id: str) -> dict | None:
        """Retrieves a specific documentation generation record by UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_explain_history(self, history_id: str) -> dict | None:
        """Retrieves a specific explanation generation record by UUID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_docs_history(self, user_id: str, file_id: str = None) -> list:
        """Retrieves all docs history concisely mapped, optionally filtered by file."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_explain_history(self, user_id: str, file_id: str = None) -> list:
        """Retrieves all explain history concisely mapped, optionally filtered by file."""
        raise NotImplementedError

    @abstractmethod
    async def clear_all_history(self) -> dict:
        """Deletes all database persistent records securely allowing fresh state."""
        raise NotImplementedError

    @abstractmethod
    async def delete_docs_history(self, history_id: str) -> bool:
        """Deletes precisely one generating history record safely by mapping UUID."""
        raise NotImplementedError

    @abstractmethod
    async def delete_explain_history(self, history_id: str) -> bool:
        """Deletes precisely one explanation history record securely by UUID."""
        raise NotImplementedError
