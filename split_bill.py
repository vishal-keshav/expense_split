
import argparse
def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument parser')
    parser.add_argument('--input', type=str, default='split.txt',
                        help='receipt pdf file path')
    parser.add_argument('--participant', type=str, nargs='+',
                        default=['V', 'K', 'M', 'S'],
                        help='split participants')
    args = parser.parse_args()
    return args

args = parse_arguments()

def get_user_expense(items, user):
    """Returns expense per user

    Args:
        items (List[List[str, float, dict]]): Constains the parsed expense
        user (str): User name
    
    Returns:
        Total expense for the user.
    """
    total_user_expense = 0.0
    for item in items:
        distribution = item[2]
        if user in distribution:
            total_user_expense += distribution[user]
    return total_user_expense

def cross_check_item_expense(item):
    """Check the correctness of computation.
    Args:
        items (List[List[str, float, dict]]): Constains the parsed expense
    
    Returns:
        bool: True is computation is valid under some precision
    """
    total_expense = item[1]
    distribution = item[2]
    total_distributed_expense = sum(distribution[k] for k in distribution)
    return abs(total_expense - total_distributed_expense) <= 0.01

def get_check_total_expense(items):
    """Check the correctness of computation and then returns the total expense
    Args:
        items (List[List[str, float, dict]]): Constains the parsed expense
    
    Returns:
        float: Total expense
    """
    total_expense = 0.0
    for item in items:
        assert cross_check_item_expense(item) == True, "Something went wrong"
        total_expense += item[1]
    return total_expense

def generate_user_expenses(items, users):
    """Generates the user expense based on the items data

    Args:
        items (List[List[str, float, dict]]): Constains the parsed expense
        users (List[str]): Participating users.
    
    Returns:
        dict: A dictionary containing per user expense.

    """
    user_expense = {}
    for user in users:
        user_expense[user] = get_user_expense(items, user)
    total_expense = get_check_total_expense(items)
    assert abs(
        sum(user_expense[k] for k in user_expense) - total_expense) < 0.01
    return user_expense

def main():
    item_list = None
    with open(args.input, "r") as file:
        item_list = eval(file.readline())
    users = args.participant
    exp = generate_user_expenses(item_list, users)
    print(exp)
    print(get_check_total_expense(item_list))

if __name__ == "__main__":
    main()