import re

def parse_question_file(content: str) -> list:
    """
    Парсит текст, извлекает блоки <question>...</question>
    и внутри них варианты <variant>...</variant>.
    Возвращает список словарей: [{'question_text': ..., 'options': [...], 'correct_index': ?}]
    """
    # Находим все блоки вопросов
    question_blocks = re.findall(r'<question>(.*?)</question>', content, re.DOTALL)
    tests = []
    for block in question_blocks:
        # Извлекаем все варианты ответов
        variants = re.findall(r'<variant>(.*?)</variant>', block, re.DOTALL)
        if not variants:
            continue
        # Текст вопроса – это block без тегов вариантов (удаляем все <variant>...</variant>)
        question_text = re.sub(r'<variant>.*?</variant>', '', block, flags=re.DOTALL).strip()
        # Создаём список options
        options = [{'text': v.strip(), 'is_correct': False} for v in variants]
        # По умолчанию правильный ответ не указан – можно добавить логику, если в файле есть маркер
        # Например, если вариант начинается с '*', сделать его правильным
        correct_index = None
        for idx, opt in enumerate(options):
            if opt['text'].startswith('*'):
                options[idx]['text'] = opt['text'][1:].strip()
                options[idx]['is_correct'] = True
                correct_index = idx
                break
        # Если маркеров нет, можно оставить без правильного (админ потом исправит)
        tests.append({
            'question_text': question_text,
            'options': options,
            'correct_index': correct_index  # может быть None
        })
    return tests