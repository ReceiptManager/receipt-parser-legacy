def convert_to_float(string_value):
    try:
        float_value = float(string_value)
        return round(float_value, 3)
    except ValueError:
        return None
