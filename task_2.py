import csv
import timeit
from BTrees.OOBTree import OOBTree

def read_items(file_path):
    items = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            items.append({
                'ID': row['ID'],
                'Name': row['Name'],
                'Category': row['Category'],
                'Price': float(row['Price'])
            })
    return items

def create_price_tree(items):
    """
    Створює дерево OOBTree, індексоване за ціною.
    Для обробки можливих дублікатів цін, зберігає список товарів для кожної ціни.
    """
    price_tree = OOBTree()
    for item in items:
        price = item['Price']
        if price in price_tree:
            price_tree[price].append(item)
        else:
            price_tree[price] = [item]
    return price_tree

def add_item_to_tree(tree, item):
    """
    Додає товар до дерева OOBTree, використовуючи ціну як ключ
    """
    price = item['Price']
    if price in tree:
        tree[price].append(item)
    else:
        tree[price] = [item]

def add_item_to_dict(dct, item):
    """
    Додає товар до словника, використовуючи ID як ключ
    """
    dct[item['ID']] = item

def range_query_tree(tree, min_price, max_price):
    """
    Оптимізований пошук діапазону для OOBTree,
    використовує вбудований метод iteritems для ефективного пошуку
    """
    result = []
    # iteritems ефективно повертає тільки елементи в заданому діапазоні
    for price, items in tree.iteritems(min_price, max_price):
        result.extend(items)
    return result

def range_query_dict(dct, min_price, max_price):
    """
    Пошук діапазону для словника (лінійний пошук)
    """
    result = []
    for item in dct.values():
        if min_price <= item['Price'] <= max_price:
            result.append(item)
    return result

def main():
    # Зчитуємо дані
    items = read_items('generated_items_data.csv')
    
    # Ініціалізуємо структури даних
    tree = create_price_tree(items)  # OOBTree тепер індексується за ціною
    dct = {}
    
    # Наповнюємо словник
    for item in items:
        add_item_to_dict(dct, item)
    
    # Вимірюємо час виконання запитів (100 ітерацій)
    tree_time = timeit.timeit(
        lambda: range_query_tree(tree, 50.0, 100.0),
        number=100
    )
    dict_time = timeit.timeit(
        lambda: range_query_dict(dct, 50.0, 100.0),
        number=100
    )
    
    # Виводимо результати
    print(f"Total range_query time for OOBTree: {tree_time:.6f} seconds")
    print(f"Total range_query time for Dict: {dict_time:.6f} seconds")

if __name__ == "__main__":
    main()