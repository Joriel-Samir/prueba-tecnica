import os

import openpyxl
import pytest

from src.analyzer import ExcelSentimentAnalyzer
from src.provider import SentimentProvider


class MockSentimentProvider(SentimentProvider):
    """Doble de prueba para aislar el test de llamadas reales HTTP."""

    def analyze(self, text: str) -> dict[str, float]:
        if "excelente" in text.lower():
            return {"negative": 5.0, "neutral": 10.0, "positive": 85.0}
        if "terrible" in text.lower():
            return {"negative": 90.0, "neutral": 5.0, "positive": 5.0}
        return {"negative": 0.0, "neutral": 0.0, "positive": 0.0}


@pytest.fixture
def dummy_excel(tmp_path):
    file_path = tmp_path / "input_test.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.cell(1, 3).value = "Comentario"
    sheet.cell(2, 3).value = "El producto es excelente"
    sheet.cell(3, 3).value = "La atención fue terrible"
    sheet.cell(4, 3).value = None  # Fila vacía
    workbook.save(file_path)
    return str(file_path)


def test_excel_analyzer_success(dummy_excel, tmp_path):
    output_path = str(tmp_path / "output_test.xlsx")
    provider = MockSentimentProvider()
    analyzer = ExcelSentimentAnalyzer(provider=provider, text_col=3)

    analyzer.process(input_path=dummy_excel, output_path=output_path)

    assert os.path.exists(output_path)

    wb = openpyxl.load_workbook(output_path)
    sheet = wb.active

    # Verificar Encabezados
    assert sheet.cell(1, 4).value == "NEGATIVO"
    assert sheet.cell(1, 5).value == "NEUTRAL"
    assert sheet.cell(1, 6).value == "POSITIVO"

    # Verificar Fila 2 (Excelente -> Positivo)
    assert sheet.cell(2, 6).value == 85.0

    # Verificar Fila 3 (Terrible -> Negativo)
    assert sheet.cell(3, 4).value == 90.0


def test_excel_analyzer_file_not_found(tmp_path):
    provider = MockSentimentProvider()
    analyzer = ExcelSentimentAnalyzer(provider=provider)

    with pytest.raises(FileNotFoundError):
        analyzer.process("archivo_inexistente.xlsx", str(tmp_path / "out.xlsx"))
