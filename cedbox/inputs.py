from datetime import datetime
import pathlib
import re
import email.utils


def string_put(text, max_times=None, times=1, default='') -> str:
    raw_input = input(text)
    if max_times and times == max_times:
        print(f'Exceeded {max_times} Trys, using default Value {default}')
        return default
    else:
        return raw_input


def int_put(text, max_times=None, times=1, default=1, conditions=None) -> int:
    if conditions is None:
        conditions = []

    raw_input = input(text)
    try:
        int_input = int(raw_input)
        for condition in conditions:
            assert condition(int_input)
        return int_input
    except Exception as e:
        print(f'{raw_input} is not valid {e}')
        if max_times and times >= max_times:
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        return int_put(text, max_times=max_times, times=times + 1, default=default, conditions=conditions)


def float_put(text, max_times=None, times=1, default=1.0, conditions=None) -> float:
    if conditions is None:
        conditions = []

    raw_input = input(text)
    try:
        float_input = float(raw_input)
        for condition in conditions:
            assert condition(float_input)
        return float_input
    except Exception as e:
        print(f'{raw_input} is not valid {e}')
        if max_times and times >= max_times:
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        return float_put(text, max_times=max_times, times=times + 1, default=default, conditions=conditions)


def choice_put(text: str, choices: list, max_times=None, times=1, def_choice_by_index=1) -> str:
    raw_input = input(text + f"({'/'.join(choices)})" + ': ')

    if raw_input in choices:
        return raw_input
    else:
        if max_times and times >= max_times:
            default = choices[def_choice_by_index]
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        print(f'{raw_input} is not valid')
        return choice_put(text, choices, max_times=max_times, times=times + 1, def_choice_by_index=def_choice_by_index)


def bool_put(text: str, max_times=None, times=1, default=False) -> bool:
    raw_input = choice_put(text, choices=['y', 'n'])

    match raw_input:
        case 'y':
            return True
        case 'n':
            return False
        case _:

            print(f'{raw_input} is not valid')
            return bool_put(text)


def file_put(text, max_times=None, times=1, default=None):
    raw_input = input(text).strip()

    try:
        path = pathlib.Path(raw_input)
        assert path.exists()
        return path
    except Exception as e:
        print(f'{raw_input} is not a valid Path: {e}')
        if max_times and times >= max_times:
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        return file_put(text, max_times=max_times, times=times + 1, default=default)


def date_put(text, max_times=None, times=1, default=None):
    date_raw = input(f'{text}(YYYY-MM-DD)')

    try:
        date = datetime.strptime(date_raw, '%Y-%m-%d')
    except Exception as e:
        print(f'{date_raw} is not valid', e)
        if max_times and times >= max_times:
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        return date_put(text, max_times=max_times, times=times + 1, default=default)
    return date


def mail_put(text, max_times=None, times=1, default=None):
    email_str = input(text)
    try:
        email_address = email.utils.parseaddr(email_str)[1]
        assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email_address)
        return email_address
    except Exception as e:
        print(f'{email_str} is not valid', e)
        if max_times and times >= max_times:
            print(f'Exceeded {max_times} Trys, using default Value {default}')
            return default
        return mail_put(text, max_times=max_times, times=times + 1, default=default)
