import string
import random
from werkzeug.security import generate_password_hash

class LicencePasswordService:
    
    def generate_password(length):
        # Define the character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = string.punctuation

        # Combine all character sets
        all_chars = lowercase + uppercase + digits + special_chars

        # Ensure the password contains at least one character from each set
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special_chars)
        ]

        # Fill the rest of the password length with random characters
        for _ in range(length - 4):
            password.append(random.choice(all_chars))

        # Shuffle the password to make it more random
        random.shuffle(password)

        # Convert the list of characters to a string
        return ''.join(password)

    def hash_password(password, method='pbkdf2:sha256', salt_length=8):
        """
        Generate a salted hash for the given password using Werkzeug.

        :param password: The password to hash
        :param method: The hashing method to use (default is 'pbkdf2:sha256')
        :param salt_length: The length of the salt (default is 8)
        :return: A salted hash of the password
        """
        return generate_password_hash(password, method=method, salt_length=salt_length)
      



    