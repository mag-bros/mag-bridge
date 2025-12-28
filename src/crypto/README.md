# 🔐 Secret data encryption
- use for encoding files or strings like passwords, tokens etc

# 1. Encode Secret Data
```bash
python src/crypto/crypto.py encrypt --name discord_release_webhook
```
```
Enter/paste your secret below, then press Ctrl+D:
superpassword
Password: 
Repeat for confirmation: 
Encrypted -> encrypted_discord_release_webhook.enc
(Cipher: AES-256-GCM, key derived via PBKDF2-HMAC-SHA256)
(Base64-encoded ciphertext)

9kaGXWZKpc827zoexbPcJY0Ky2gifbjH+pScD9KSFfoCFD2VJ95xL+pLatznlmWY7lzgYrxB2xsYGA==
```
# 2. Decode Secret Data
## 2.1 Decode using file
```bash
python src/crypto/crypto.py decrypt encrypted_discord_release_webhook.enc
```
```bash
Password: 
Decrypted -> decrypted_20251205_060657.dec
Secret content:

superpassword
```

## 2.2 Decode using paste
```bash
python src/crypto/crypto.py decrypt
```
```bash
Enter/paste encrypted base64 text below, then press Ctrl+D:
9kaGXWZKpc827zoexbPcJY0Ky2gifbjH+pScD9KSFfoCFD2VJ95xL+pLatznlmWY7lzgYrxB2xsYGA==
Password: 
Decrypted -> decrypted_20251205_060800.dec
Secret content:

superpassword
```
