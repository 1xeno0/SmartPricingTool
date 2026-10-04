import csv
import chardet

def detect_file_properties(file_path, sample_size=1024):
    """Определяет кодировку и разделитель для CSV файла."""
    with open(file_path, 'rb') as file:
        raw_data = file.read(sample_size)
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        try:
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(raw_data.decode(encoding)).delimiter
        except Exception:
            delimiter = ','  # Установка значения по умолчанию, если определение не удалось

    return delimiter, encoding