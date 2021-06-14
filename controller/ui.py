from datetime import datetime, date


def user_menu(packages_hash):
    """
    The user interface of the program.

    Time Complexity: O(1)
    Space Complexity: O(1)

    :param packages_hash:
    """
    exit_words = ['exit', 'x', 'close', 'bye', 'end']

    print('{:*^50}'.format('Welcome to WGUPS'))
    print()
    print('1. See Each Packages Status at a Chosen Time')
    print('2. See Package Status by Package ID')
    print('3. Quit')
    print()
    user_input = input('Please choose a menu item: ')

    if user_input == '1':
        search_by_time(packages_hash, exit_words)
    elif user_input == '2':
        search_by_id(packages_hash, exit_words)
    elif user_input == '3' or user_input in exit_words:
        print('Goodbye.')
        return


def search_by_time(packages_hash, exit_words):
    """
    Prompts user for time input and returns status of all packages at the given time.

    Time Complexity: O(1)  Loops through all package ids (constant), and looks them up in the hash table (constant)
    Space Complexity: O(1)

    :param packages_hash:
    :param exit_words:
    """
    try:
        time_input = input('Enter desired time: ')
    except ValueError:
        time_input = input('Please enter a valid time')
        if time_input.lower() in exit_words:
            print('Goodbye.')
            return

    if len(time_input) > 5:  # 12 hr clock
        try:
            user_time = datetime.strptime(time_input, "%I:%M %p").time()
        except ValueError:
            time_input = time_input[:-3] + time_input[-2:]
            user_time = datetime.strptime(time_input, "%I:%M%p").time()
        except ValueError:
            print('Please enter a valid time.')
            return search_by_time(packages_hash, exit_words)

        user_datetime = datetime.combine(date.today(), user_time)
        for i in range(1, 41):
            package = packages_hash.search(i)
            if package.timestamp < user_datetime:
                print(package)
            else:
                print(package.id_, '\b,', package.address, '\b,', package.city, '\b,', package.state, '\b,',
                      package.zip_, '\b,', package.notes, '\b, ', 'Package Not Yet Delivered')
        return user_menu(packages_hash)
    else:  # 24 hr clock
        try:
            user_time = datetime.strptime(time_input, "%H:%M").time()
        except ValueError:
            print('Please enter a valid time.')
            return search_by_time(packages_hash, exit_words)
        user_datetime = datetime.combine(date.today(), user_time)
        for i in range(1, 41):
            package = packages_hash.search(i)
            if package.timestamp < user_datetime:
                print(package)
            else:
                print(package.id_, '\b,', package.address, '\b,', package.city, '\b,', package.state, '\b,',
                      package.zip_, '\b,', package.notes, '\b, ', 'Package Not Yet Delivered')
        return user_menu(packages_hash)


def search_by_id(packages_hash, exit_words):
    """
    Prompts user for a Package ID, and returns the time it was delivered.

    Time Complexity: O(1)
    Space Complexity: O(1)

    :param packages_hash:
    :param exit_words:
    """
    search_id = input('Enter the package ID for lookup, or type Exit to exit: ')

    if search_id.lower() in exit_words:
        print('Goodbye.')
        return

    try:
        search_id = int(search_id)
        item = packages_hash.search(search_id)
        if item is not None:
            print(item)
            print()
            user_menu(packages_hash)
        else:
            print('Could not Find Package: ' + str(search_id))
            print()
            user_menu(packages_hash)
    except ValueError:
        print('Could Not Find Package: ' + search_id)
        print()
        user_menu(packages_hash)
