import os
import random

def cats():
    cat_folder = 'cats_images'  # Назва папки з зображеннями котів
    cat_files = os.listdir(cat_folder)  # Отримання списку файлів у папці
    cat_random = random.choice(cat_files)  # Випадковий вибір зображення
    return os.path.join(cat_folder, cat_random)  # Повний шлях до випадкового зображення
