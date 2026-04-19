from abc import ABC, abstractmethod


class BaseAIProvider(ABC):
    @abstractmethod
    def generate_content(self, topic: str) -> str:
        """Generate a short content script for the given topic.

        Returns a string on success. Should raise an exception on unrecoverable errors.
        """

