import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

from pathlib import Path
from flask import Flask, request, jsonify

from common.prompt_manager import prompt_manager

app = Flask(__name__)


# Маршрут для чтения файла
@app.get("/prompt")
def read_prompt():
    try:
        content = prompt_manager.get_system_prompt()
        return jsonify({"prompt": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Маршрут для записи в файл
@app.post("/prompt")
def write_prompt():
    try:
        new_prompt = request.json.get("prompt", "")
        if not new_prompt:
            return jsonify({"error": "No text provided"}), 400

        prompt_manager.edit_system_prompt(new_prompt)

        return jsonify({"message": "File updated successfully", "prompt": new_prompt})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
