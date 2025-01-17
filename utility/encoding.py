# import string

# # Base62 character set (digits + uppercase + lowercase)
# BASE62_ALPHABET = string.digits + string.ascii_letters
# BASE = len(BASE62_ALPHABET)

# def generate_filename_from_url(url: str) -> str:
#     """Encodes a URL into a Base62 representation (filename-safe)."""
#     num = int.from_bytes(url.encode(), 'big')
#     base62 = []
#     while num:
#         num, rem = divmod(num, BASE)
#         base62.append(BASE62_ALPHABET[rem])
#     return ''.join(reversed(base62))

# def decode_url_base62(encoded_str: str) -> str:
#     """Decodes a Base62 string back to the original URL."""
#     num = 0
#     for char in encoded_str:
#         num = num * BASE + BASE62_ALPHABET.index(char)
#     return num.to_bytes((num.bit_length() + 7) // 8, 'big').decode()

# # Example Usage
# url = "https://chatgpt.com/c/6789ed88-898c-800f-bdc7-0effec931dc5"
# encoded = generate_filename_from_url(url)
# # decoded = decode_url_base62('iOni0HT3ZgApYyMlxefKW9MkEOq0lPZdEAJPCgiJP9InYquRPlow6tcqDx4CND9aC7AWwZj38UXd8F')

# # print("Base62 Encoded:", encoded)  # Safe for filenames
# print("Decoded URL:", encoded)  # Should match the original URL


from hashids import Hashids

hashids = Hashids(salt="your_secret_salt", min_length=10)
slug = "009h-8989-3434-hkdfd-sfsdfdsf"
slug_int = sum(ord(c) for c in slug)  # Convert to an integer

encoded_slug = hashids.encode(slug_int)
decoded_slug_int = hashids.decode(encoded_slug)

print("Encoded:", encoded_slug)  # Example: "x1Yb3XzPq"
print("Decoded (Int):", decoded_slug_int)  # Convert back to original if needed
