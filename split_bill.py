
def get_user_expense(items, user):
    total_user_expense = 0.0
    for item in items:
        distribution = item[2]
        if user in distribution:
            total_user_expense += distribution[user]
    return total_user_expense

def cross_check_item_expense(item):
    total_expense = item[1]
    distribution = item[2]
    total_distributed_expense = sum(distribution[k] for k in distribution)
    return abs(total_expense - total_distributed_expense) <= 0.01

def get_check_total_expense(items):
    total_expense = 0.0
    for item in items:
        assert cross_check_item_expense(item) == True, "Something went wrong"
        total_expense += item[1]
    return total_expense

def generate_user_expenses(items, users):
    user_expense = {}
    for user in users:
        user_expense[user] = get_user_expense(items, user)
    total_expense = get_check_total_expense(items)
    assert abs(
        sum(user_expense[k] for k in user_expense) - total_expense) < 0.01
    return user_expense

def main():
    item_list = None
    with open("split.txt", "r") as file:
        item_list = eval(file.readline())
    users = ['V', 'K', 'M', 'S']
    exp = generate_user_expenses(item_list, users)
    print(exp)
    print(get_check_total_expense(item_list))

if __name__ == "__main__":
    main()