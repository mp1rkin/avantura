def greet(name):
    """Простая функция приветствия"""
    return f"Привет, {name}! Добро пожаловать в проект Avantura!"

def main():
    print(greet("Мир"))
    print("Это тестовый коммит для проверки работы с Git")

    # Небольшая демонстрация
    names = ["Никита", "Друг", "Команда"]
    for name in names:
        print(greet(name))

if __name__ == "__main__":
    main()
