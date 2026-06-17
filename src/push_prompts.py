"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Construir o ChatPromptTemplate a partir do system_prompt e user_prompt
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")
        
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        
        prompt_object = ChatPromptTemplate.from_messages(messages)
        
        description = prompt_data.get("description", "Prompt otimizado para Bug to User Story")
        tags = prompt_data.get("tags", ["bug-analysis", "user-story"])
        
        print(f"Enviando prompt '{prompt_name}' ao LangSmith Hub...")
        
        hub.push(
            repo_full_name=prompt_name,
            object=prompt_object,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags
        )
        
        print(f"[SUCESSO] Push realizado com sucesso no repositório: https://smith.langchain.com/hub/{prompt_name}")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao fazer push do prompt para o LangSmith Hub: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH PROMPTS TO LANGSMITH HUB")
    
    # Verificar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        print("[ERRO] Faltam variáveis de ambiente no .env")
        return 1
        
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    
    # Carregar prompt otimizado
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    print(f"Carregando prompt de '{yaml_path}'...")
    yaml_data = load_yaml(yaml_path)
    
    if not yaml_data or "bug_to_user_story_v2" not in yaml_data:
        print(f"[ERRO] Erro: Chave 'bug_to_user_story_v2' não encontrada em {yaml_path}")
        return 1
        
    prompt_data = yaml_data["bug_to_user_story_v2"]
    
    # Validar
    print("Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("[ERRO] Erros de validação encontrados:")
        for error in errors:
            print(f"   - {error}")
        return 1
    print("[SUCESSO] Estrutura do prompt válida!")
    
    # Executar push
    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
