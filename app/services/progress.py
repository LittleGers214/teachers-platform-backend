def calculate_score(tests, user_answers):
    if not tests:
        return 100.0  # если нет тестов, считаем успехом
    correct = 0
    for test in tests:
        user_choice = user_answers.get(str(test.id))
        # options формат: [{"text":"A","is_correct":false}, ...]
        if user_choice is not None and 0 <= user_choice < len(test.options):
            if test.options[user_choice].get('is_correct'):
                correct += 1
    return (correct / len(tests)) * 100.0