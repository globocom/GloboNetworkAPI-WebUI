from whrandom import choice
import string


def GenPasswd():
    newpasswd = ''
    chars = string.letters + string.digits
    for i in range(8):
        newpasswd = newpasswd + choice(chars)
    return newpasswd
