# Простой скрипт для просмотра данных
import pandas as pd
import matplotlib.pyplot as plt

print("=" * 60)
print("ЛАБОРАТОРНА РОБОТА #1 - ПЕРЕВІРКА ДАНИХ")
print("=" * 60)

# Загрузка всех выборок
print("\n1. Вибірка 1 (2D лінійно-сепарабельна):")
df1 = pd.read_csv('sample1_normalized.csv')
print(f"   Розмір: {len(df1)} елементів")
print(f"   Кластери: {df1['cluster'].nunique()}")
print(df1.head())

print("\n2. Вибірка 2 (3D нормальний розподіл):")
df2 = pd.read_csv('sample2_normalized.csv')
print(f"   Розмір: {len(df2)} елементів")
print(f"   Кластери: {df2['cluster'].nunique()}")
print(df2.head())

print("\n3. Вибірка 3 (Іриси Фішера):")
df3 = pd.read_csv('sample3_iris_normalized.csv')
print(f"   Розмір: {len(df3)} елементів")
print(f"   Класи: {df3['species'].nunique()}")
print(df3.head())

print("\n4. Вибірка 4 (Mall Customer Segmentation):")
df4 = pd.read_csv('sample4_mall_normalized.csv')
print(f"   Розмір: {len(df4)} елементів")
print(f"   Сегменти: {df4['Segment'].nunique()}")
print(df4.head())

print("\n" + "=" * 60)
print("ВСІ ВИБІРКИ ЗАВАНТАЖЕНІ УСПІШНО!")
print("=" * 60)

# Быстрая визуализация Вибірки 1
plt.figure(figsize=(10, 6))
plt.scatter(df1['x'], df1['y'], c=df1['cluster'], cmap='viridis', s=30, alpha=0.6)
plt.xlabel('X (normalized)')
plt.ylabel('Y (normalized)')
plt.title('Вибірка 1: Швидкий перегляд')
plt.colorbar(label='Cluster')
plt.savefig('quick_view.png', dpi=150)
print("\nГрафік збережено: quick_view.png")
print("Відкрийте його, щоб побачити вибірку 1")
