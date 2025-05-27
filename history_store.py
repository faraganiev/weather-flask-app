from collections import defaultdict

# Общая статистика по всем
global_city_log = defaultdict(int)

# Персональные истории: user_id -> {город -> количество}
user_city_log = defaultdict(lambda: defaultdict(int))

def log_city_search(city_name, user_id):
    city = city_name.lower()
    global_city_log[city] += 1
    user_city_log[user_id][city] += 1

def get_city_stats():
    return dict(global_city_log)

def get_user_stats(user_id):
    return dict(user_city_log[user_id])
