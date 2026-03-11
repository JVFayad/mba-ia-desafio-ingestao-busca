from search import search_prompt

def main():
    while True:
        question = input("Faça sua pergunta (ou 'sair' para encerrar): ")
        if question.lower() == "sair":
            print("Encerrando o chat. Até mais!")
            break

        chain = search_prompt(question)

        if not chain:
            print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            return

        print(f"\nPERGUNTA: {question}")
        print(f"RESPOSTA: {chain.content}\n")


if __name__ == "__main__":
    main()