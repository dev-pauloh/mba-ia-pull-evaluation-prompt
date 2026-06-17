"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @property
    def prompt_data(self):
        file_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        data = load_prompts(str(file_path))
        if not data or "bug_to_user_story_v2" not in data:
            raise KeyError("Chave 'bug_to_user_story_v2' não encontrada no arquivo YAML.")
        return data["bug_to_user_story_v2"]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        data = self.prompt_data
        assert "system_prompt" in data
        assert data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        data = self.prompt_data
        system_prompt = data["system_prompt"].lower()
        role_indicators = ["product manager", "product owner", "você é um", "você é uma", "persona", "cargo", "papel", "analista de negócios", "business analyst"]
        assert any(indicator in system_prompt for indicator in role_indicators), "Persona/Role não definida no system_prompt"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        data = self.prompt_data
        system_prompt = data["system_prompt"].lower()
        format_indicators = ["markdown", "como um", "eu quero", "para que", "critérios de aceitação", "criterios de aceitacao", "user story"]
        assert any(indicator in system_prompt for indicator in format_indicators), "Exigência de formato Markdown ou User Story não encontrada"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        data = self.prompt_data
        system_prompt = data["system_prompt"].lower()
        few_shot_indicators = ["exemplo", "few-shot", "few shot", "entrada", "saída", "saida", "caso de teste", "caso", "exemplo de entrada"]
        assert any(indicator in system_prompt for indicator in few_shot_indicators), "Exemplos de poucas tentativas (Few-shot) não encontrados"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        data = self.prompt_data
        system_prompt = data["system_prompt"]
        assert "TODO" not in system_prompt
        assert "[TODO]" not in system_prompt

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        data = self.prompt_data
        techniques = data.get("techniques_applied", [])
        assert len(techniques) >= 2, f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])