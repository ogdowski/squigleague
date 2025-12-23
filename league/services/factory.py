from typing import Optional
from league.services.base import BaseFormatHandler, BaseScoringSystem
from league.services.formats.group_playoff import GroupPlayoffHandler
from league.services.scoring.aos_differential import AOSDifferentialScoring

class FormatHandlerFactory:
    """
    Factory for creating format handlers.
    Add new formats by registering them in _handlers dict.
    """

    _handlers = {
        "group_playoff": GroupPlayoffHandler,
    }

    @classmethod
    def create(cls, season: dict) -> BaseFormatHandler:
        """
        Create format handler for given season.

        Args:
            season: Season dict from database

        Returns:
            Initialized format handler

        Raises:
            ValueError: If format not registered or config invalid
        """
        handler_class = cls._handlers.get(season['league_format'])

        if not handler_class:
            raise ValueError(
                f"No handler registered for format: {season['league_format']}"
            )

        handler = handler_class(season)

        is_valid, error = handler.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid format config: {error}")

        return handler

    @classmethod
    def register_format(cls, format_type: str, handler_class):
        """
        Register new format handler (for future extensibility).

        Example:
            FormatHandlerFactory.register_format("swiss", SwissHandler)
        """
        cls._handlers[format_type] = handler_class


class ScoringSystemFactory:
    """
    Factory for creating scoring systems.
    Add new systems by registering them in _systems dict.
    """

    _systems = {
        "aos_differential": AOSDifferentialScoring,
    }

    @classmethod
    def create(cls, season: dict) -> BaseScoringSystem:
        """
        Create scoring system for given season.

        Args:
            season: Season dict from database

        Returns:
            Initialized scoring system

        Raises:
            ValueError: If system not registered or config invalid
        """
        system_class = cls._systems.get(season['scoring_system'])

        if not system_class:
            raise ValueError(
                f"No scoring system registered for: {season['scoring_system']}"
            )

        system = system_class(season['scoring_config'])

        is_valid, error = system.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid scoring config: {error}")

        return system

    @classmethod
    def register_system(cls, system_type: str, system_class):
        """
        Register new scoring system (for future extensibility).

        Example:
            ScoringSystemFactory.register_system("win_draw_loss", WDLScoring)
        """
        cls._systems[system_type] = system_class
