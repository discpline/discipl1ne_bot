import os
import random


def cats() -> str:
    """
    Повертає шлях до випадкового зображення кота.

    Returns:
        str: Повний шлях до випадкового зображення кота.
    """
    cat_folder = 'cats_images'  # Назва папки з зображеннями котів
    cat_files = os.listdir(cat_folder)  # Отримання списку файлів у папці
    cat_random = random.choice(cat_files)  # Випадковий вибір зображення
    return os.path.join(cat_folder, cat_random)  # Повний шлях до випадкового зображення
