import logging
import time
from abc import ABC, abstractmethod

import paralleldots

logger = logging.getLogger(__name__)


class SentimentProvider(ABC):
    """Interfaz abstracta para proveedores de análisis de sentimiento."""

    @abstractmethod
    def analyze(self, text: str) -> dict[str, float]:
        """Analiza el texto y retorna las puntuaciones de sentimiento en porcentaje."""


class ParallelDotsProvider(SentimentProvider):
    """Implementación de SentimentProvider para ParallelDots con Backoff exponencial."""

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("API Key no proporcionada.")
        self.api_key = api_key
        paralleldots.set_api_key(self.api_key)

    def analyze(self, text: str) -> dict[str, float]:
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = paralleldots.sentiment(text)

                if "sentiment" not in response:
                    logger.warning(
                        "Respuesta inesperada de la API en la fila: %s", response
                    )
                    return {"negative": 0.0, "neutral": 0.0, "positive": 0.0}

                sentiments = response["sentiment"]
                return {
                    "negative": round(sentiments.get("negative", 0.0) * 100, 3),
                    "neutral": round(sentiments.get("neutral", 0.0) * 100, 3),
                    "positive": round(sentiments.get("positive", 0.0) * 100, 3),
                }

            except Exception as exc: # noqa: BLE001
                logger.warning(
                    "Error al comunicarse con la API (intento %d/%d): %s",
                    attempt + 1,
                    max_retries,
                    exc,
                )
                if attempt == max_retries - 1:
                    logger.error("Se agotaron los reintentos para el texto actual.")
                    return {"negative": 0.0, "neutral": 0.0, "positive": 0.0}

                sleep_time = base_delay * (2**attempt)
                logger.info("Esperando %d segundos antes de reintentar...", sleep_time)
                time.sleep(sleep_time)

        return {"negative": 0.0, "neutral": 0.0, "positive": 0.0}
