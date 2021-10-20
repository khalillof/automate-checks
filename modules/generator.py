#!/usr/bin/env python3
import random
import secrets
import string
import uuid


def get_random_string(length: int):
    # choose from all lowercase letter
    result_str = ''.join(random.choice(string.ascii_lowercase)
                         for i in range(length))
    return result_str


    # usage get_random_string(8)
"""
def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    print(result_str)
    # string of length 8
"""
""" Random string of specific letters """


def random_specific_letters():
    # Random string of length 5
    result_str = ''.join((random.choice('abcdxyzpqr') for i in range(5)))
    return result_str


""" Create Random Password with Special characters, letters, and digits """


def password1():
    # get random password pf length 8 with letters, digits, and symbols
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(8))
    print("Random password is:", password)


"""Random password with a fixed count of letters, digits, and symbols"""


def get_random_password():
    random_source = string.ascii_letters + string.digits + string.punctuation
    # select 1 lowercase
    password = random.choice(string.ascii_lowercase)
    # select 1 uppercase
    password += random.choice(string.ascii_uppercase)
    # select 1 digit
    password += random.choice(string.digits)
    # select 1 special symbol
    password += random.choice(string.punctuation)

    # generate other characters
    for i in range(6):
        password += random.choice(random_source)

    password_list = list(password)
    # shuffle all characters
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password


"""Generate a random alphanumeric string of letters and digits"""


def get_alphanumeric_letters_digits():
    # get random string of letters and digits
    source = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(source) for i in range(8)))
    print(result_str)
    # Output vZkOkL97


"""Random alphanumeric string with a fixed count of letters and digits"""


def get_string(letters_count, digits_count):
    letters = ''.join((random.choice(string.ascii_letters)
                      for i in range(letters_count)))
    digits = ''.join((random.choice(string.digits)
                     for i in range(digits_count)))

    # Convert resultant string to list and shuffle it to mix letters and digits
    sample_list = list(letters + digits)
    random.shuffle(sample_list)
    # convert list to string
    final_string = ''.join(sample_list)
    print('Random string with', letters_count, 'letters',
          'and', digits_count, 'digits', 'is:', final_string)


""" Generate a secure random string and password #========================================================================
Above all, examples are not cryptographically secure. The cryptographically secure random generator generates random data using synchronization methods to ensure that no two processes can obtain the same data simultaneously.
If you are producing random passwords or strings for a security-sensitive application, then you must use this approach.
"""


def secure_random_password():
    # secure random string
    secure_str = ''.join((secrets.choice(string.ascii_letters)
                         for i in range(8)))
    print(secure_str)
    # Output QQkABLyK

    # secure password
    password = ''.join((secrets.choice(
        string.ascii_letters + string.digits + string.punctuation) for i in range(8)))
    print(password)
    # output 4x]>@;4)


"""Generate a random string token"""


def get_token():
    return secrets.token_hex(32)
# Secure hexadecimal string token 25cd4dd7bedd7dfb1261e2dc1489bc2f046c70f986841d3cb3d59a9626e0d802


"""Generate universally unique secure random string Id"""


def get_uuid():
    return uuid.uuid4()
# Output 0682042d-318e-45bf-8a16-6cc763dc8806
