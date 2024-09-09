import base64
from Crypto.Cipher import AES, DES
from Crypto.Util.Padding import pad, unpad
from configs import encrypt_key as key, encrypt_method as method


# 辅助函数：调整密钥长度
def adjust_key_length(src_key: str, required_length: int) -> bytes:
    # 将字符串转换为字节串
    src_key = src_key.encode('utf-8')

    if len(src_key) < required_length:
        # 如果密钥长度不足，填充 '0'
        src_key += b'0' * (required_length - len(src_key))
    else:
        # 如果密钥长度过长，截取前 required_length 个字节
        src_key = src_key[:required_length]
    return src_key


# 加密函数
def encrypt(message: str) -> str:
    adjusted_key = adjust_key_length(key, AES.key_size[0])  # 调整密钥长度

    if method == "PLAINTEXT":
        return base64.b64encode(message.encode('utf-8')).decode('utf-8')
    elif method == "AES":
        cipher = AES.new(adjusted_key, AES.MODE_CBC, b'0000000000000000')
        encrypted = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
        return base64.b64encode(encrypted).decode('utf-8')
    elif method == "DES":
        adjusted_key = adjust_key_length(key, DES.key_size)  # 调整密钥长度
        cipher = DES.new(adjusted_key, DES.MODE_CBC, b'00000000')
        encrypted = cipher.encrypt(pad(message.encode('utf-8'), DES.block_size))
        return base64.b64encode(encrypted).decode('utf-8')


# 解密函数
def decrypt(encrypted_message: str) -> str:
    encrypted_bytes = base64.b64decode(encrypted_message)
    adjusted_key = adjust_key_length(key, AES.key_size[0])  # 调整密钥长度

    if method == "PLAINTEXT":
        return base64.b64decode(encrypted_message).decode('utf-8')
    elif method == "AES":
        cipher = AES.new(adjusted_key, AES.MODE_CBC, b'0000000000000000')
        decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted.decode('utf-8')
    elif method == "DES":
        adjusted_key = adjust_key_length(key, DES.key_size)  # 调整密钥长度
        cipher = DES.new(adjusted_key, DES.MODE_CBC, b'00000000')
        decrypted = unpad(cipher.decrypt(encrypted_bytes), DES.block_size)
        return decrypted.decode('utf-8')


# 测试加密和解密
if __name__ == "__main__":
    test_message = "Hello, world!"

    # 测试 AES 加密和解密
    test_encrypted_message = encrypt(test_message)
    test_decrypted_message = decrypt(test_encrypted_message)
    print(f"Original Message: {test_message}")
    print(f"Encrypted Message (Base64): {test_encrypted_message}")
    print(f"Decrypted Message: {test_decrypted_message}")
