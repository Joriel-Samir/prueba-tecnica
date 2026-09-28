import argparse
import logging
import os
import sys

from src.analyzer import ExcelSentimentAnalyzer
from src.provider import ParallelDotsProvider


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description="Analizador de sentimientos para archivos Excel con ParallelDots."
    )
    parser.add_argument(
        "input_file", type=str, help="Ruta del archivo Excel de entrada."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="sentimentAnalysis.xlsx",
        help="Ruta del archivo de salida.",
    )
    parser.add_argument(
        "--sheet", "-s", type=str, default=None, help="Nombre de la hoja a procesar."
    )
    parser.add_argument(
        "--col",
        "-c",
        type=int,
        default=3,
        help="Número de columna del texto a analizar (1-based).",
    )

    args = parser.parse_args()

    api_key = os.getenv("PARALLELDOTS_API_KEY")
    if not api_key:
        logger.error(
            "Error: La variable de entorno 'PARALLELDOTS_API_KEY' no está configurada."
        )
        sys.exit(1)

    try:
        provider = ParallelDotsProvider(api_key=api_key)
        analyzer = ExcelSentimentAnalyzer(provider=provider, text_col=args.col)
        analyzer.process(
            input_path=args.input_file,
            output_path=args.output,
            sheet_name=args.sheet,
        )
    except Exception as exc: # noqa: BLE001
        logger.error("Error inesperado durante la ejecución: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
