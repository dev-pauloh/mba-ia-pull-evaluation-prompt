"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith() -> bool:
    """
    Conecta ao LangSmith Hub e faz pull do prompt bug_to_user_story_v1.
    """
    print_section_header("PULL PROMPT FROM LANGSMITH HUB")
    
    # Verificar variáveis necessárias
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        print("[ERRO] Credenciais do LangSmith não configuradas no .env")
        return False

    try:
        prompt_name = "leonanluppi/bug_to_user_story_v1"
        print(f"Puxando prompt do LangSmith Hub: '{prompt_name}'...")
        
        # Puxa o prompt do Hub
        prompt = hub.pull(prompt_name)
        print("[SUCESSO] Prompt carregado do Hub com sucesso!")
        
        # Extrair templates de sistema e usuário de forma resiliente
        system_prompt = ""
        user_prompt = ""
        
        # Acessar os templates
        if hasattr(prompt, "messages") and len(prompt.messages) >= 2:
            msg_sys = prompt.messages[0]
            msg_usr = prompt.messages[1]
            
            # Extrai template do System Message
            if hasattr(msg_sys, "prompt") and hasattr(msg_sys.prompt, "template"):
                system_prompt = msg_sys.prompt.template
            elif hasattr(msg_sys, "content"):
                system_prompt = msg_sys.content
                
            # Extrai template do Human Message
            if hasattr(msg_usr, "prompt") and hasattr(msg_usr.prompt, "template"):
                user_prompt = msg_usr.prompt.template
            elif hasattr(msg_usr, "content"):
                user_prompt = msg_usr.content
        else:
            # Caso não venha no formato ChatPromptTemplate de duas mensagens
            print("[AVISO] Estrutura inesperada do prompt, tentando fallback...")
            system_prompt = str(prompt)
            user_prompt = "{bug_report}"

        # Montar a estrutura no padrão do arquivo YAML
        yaml_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }
        
        output_file = "prompts/bug_to_user_story_v1.yml"
        if save_yaml(yaml_data, output_file):
            print(f"[SUCESSO] Prompt salvo localmente em: {output_file}")
            return True
        else:
            print("[ERRO] Erro ao salvar o prompt em YAML.")
            return False

    except Exception as e:
        print(f"[ERRO] Falha ao realizar pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
