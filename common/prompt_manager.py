from pathlib import Path

from . import crud


class PromptManager:
    def __init__(
        self,
        base_dir: Path,
    ):
        self.data_dir = base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.PROMPTS_DIR = base_dir / "tg_bot" / "prompts"

    def _get_init_file(self, file_name: str) -> str:
        file_path: Path = self.data_dir / file_name
        try:
            data = file_path.read_text("utf-8")
        except:
            init_file_path = self.PROMPTS_DIR / file_name
            file_path.write_text(init_file_path.read_text("utf-8"), "utf-8")
            data = file_path.read_text("utf-8")
        return data

    def get_core_prompt(self) -> str:
        core_prompt = self._get_init_file("system_prompt.txt")
        return core_prompt

    def get_system_prompt(self) -> str:
        core_prompt = self.get_core_prompt()
        pipelines = crud.get_pipeline_names()
        statuses = crud.get_status_names()
        system_prompt = f"{core_prompt}\n\nИнформация из БД:\nВоронки: {pipelines}\nЭтапы: {statuses}"
        return system_prompt

    def edit_core_prompt(self, new_prompt: str) -> Path:
        self.get_core_prompt()
        file_path: Path = self.data_dir / "system_prompt.txt"
        file_path.write_text(new_prompt, "utf-8")
        return file_path


BASEDIR = Path(__file__).parent.parent
prompt_manager = PromptManager(BASEDIR)
