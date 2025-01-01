import random
import string


def mask_sensitive_data(
    value: str, start: int = 3, end: int = -4, mask_char: str = "*"
) -> str:
    """
    隐藏字符串中间的敏感信息（如手机号或身份证号）
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    length = len(value)
    if start >= length or abs(end) >= length or start >= (length + end):
        raise ValueError("Invalid start or end values")

    hidden_part = max(0, length - start - abs(end))
    return value[:start] + (mask_char * hidden_part) + value[end:]


def auto_mask(value: str) -> str:
    if len(value) == 11:  # 手机号
        return mask_sensitive_data(value, start=3, end=-4)
    elif len(value) == 18:  # 身份证号
        return mask_sensitive_data(value, start=6, end=-4)
    else:
        return mask_sensitive_data(value)  # 默认规则


def generate_random_password(
    length=12,
    use_uppercase=True,
    use_digits=True,
    use_special=True,
):
    """
    随机生成密码
    :param length: 密码长度
    :param use_uppercase: 是否包含大写字母
    :param use_digits: 是否包含数字
    :param use_special: 是否包含特殊字符
    :return: 生成的密码
    """
    if length < 6:
        raise ValueError("密码长度不能少于 6 位")

    # 基础字符集合：小写字母
    characters = string.ascii_lowercase

    # 根据需求添加字符集合
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?/"

    # 确保密码至少包含每种类型的字符
    password = []
    if use_uppercase:
        password.append(random.choice(string.ascii_uppercase))  # nosec
    if use_digits:
        password.append(random.choice(string.digits))  # nosec
    if use_special:
        password.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?/"))  # nosec

    # 填充剩余字符
    password += random.choices(characters, k=length - len(password))  # nosec

    # 打乱密码顺序
    random.shuffle(password)

    return "".join(password)
