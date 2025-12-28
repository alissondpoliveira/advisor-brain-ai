import google.generativeai as genai

# Sua chave (colocada aqui apenas para este teste rápido)
CHAVE = "AIzaSyAfFLAgDbIkWF6oW6XqG6H-bcjmxEoorsA"

genai.configure(api_key=CHAVE)

print("--- BUSCANDO MODELOS DISPONÍVEIS ---")
try:
    # Lista todos os modelos disponíveis para sua chave
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nome encontrado: {m.name}")
            
except Exception as e:
    print(f"Erro ao listar: {e}")

print("--------------------------------------")