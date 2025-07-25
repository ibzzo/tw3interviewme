#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Afficher les infos au démarrage si c'est runserver
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        print("\n" + "="*50)
        print("🚀 CHATBOT IA - Backend Django")
        print("="*50)
        print("💡 Modes disponibles:")
        print("   - vLLM Local (Phi-3) sur http://localhost:8080")
        print("   - OpenRouter Cloud (Qwen)")
        print("🔄 Changez de mode dans l'interface web")
        print("="*50 + "\n")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
