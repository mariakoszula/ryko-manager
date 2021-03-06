def parse_special_string_format_to_set(input: str):
    # 1,2,3,4 or 1-6,14 or 13,1-6, 1-3, 3-4
    list_of_data = list()
    list_parts = input.split(",")
    for part in list_parts:
        if "-" in part:
            new_range = part.split("-")
            list_of_data.extend([i for i in range(int(new_range[0]), int(new_range[1]) + 1)])
        else:
            list_of_data.append(int(part))
    list_of_data.sort()
    return set(list_of_data)


def empty_if_none(value):
    if not value:
        return ""
    return value

