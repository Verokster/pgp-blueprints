import pgpy

key_file = "key.txt"
src = "test.py"
dst = "test.py"

"""
Opens key from file.
"""
fkey = open(key_file, "r")
data_key = fkey.read()
fkey.close()
key = pgpy.PGPKey()
key.parse(data_key)

"""
Encrypts the content of a file.
"""
fin = open(src, "rb")
data = fin.read()
fin.close()

message = pgpy.PGPMessage.new(data)
enc_message = key.pubkey.encrypt(message)

fout = open(dst + ".pgp", "wb")
fout.write(bytes(enc_message))
fout.close()

print("Task complete.")