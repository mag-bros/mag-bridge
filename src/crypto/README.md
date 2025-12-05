# 🔐 Secret data encryption
- use for encoding files or strings like passwords, tokens etc

# 1. Encode Secret Data
```bash
python ./.github/scripts/secrets/encrypt.py --name discord_release_webhook
```
```
Enter/paste your secret below, then press Ctrl+D:
mysuppoerpassword123
Password: 
Confirm password: 
Encrypted -> encrypted_discord_release_webhook.enc
(Cipher: AES-256-GCM, key derived via PBKDF2-HMAC-SHA256)
(Base64-encoded ciphertext)

27PYB5kD+lEY+Rx8H1zTNN1g5Old33nXQklkZht3yM3383xE1AqCmWP/V/52J9lxbmC+Xc6k2kvRmTkuEUZOh48=
```
# 2. Decode Secret Data
## 2.1 Decode using file
```bash
python ./.github/scripts/secrets/decrypt.py encrypted_discord_release_webhook.enc 
```
```bash
Password: 
Decrypted -> decrypted_20251205_040857.dat
Secret content:

mysuppoerpassword123
```

## 2.2 Decode using paste
```bash
python ./.github/scripts/secrets/decrypt.py 
```
```bash
Enter/paste encrypted base64 text below, then press Ctrl+D:
27PYB5kD+lEY+Rx8H1zTNN1g5Old33nXQklkZht3yM3383xE1AqCmWP/V/52J9lxbmC+Xc6k2kvRmTkuEUZOh48=
Password: 
Decrypted -> decrypted_20251205_040825.dat
Secret content:

mysuppoerpassword123
```
