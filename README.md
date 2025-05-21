# 🛡️ Cryptography Course Assignments

Hi! This repository contains my work on the four major assignments from our Cryptography course. Each assignment involved a different set of cryptographic techniques—from classical ciphers and pseudorandom generators to modern encryption attacks and hands-on cryptanalysis challenges. Below, I’ve described what each assignment included and how I approached solving them.

---

## 🔐 Assignment 1: Classical Cipher Decryption

For this assignment, I was given two ciphertext files based on my serial number from the attendance sheet:
- A **substitution cipher** file: `ciphertext_test_XX.txt`
- A **Vigenère cipher** file: `v_ciphertext_XX.txt`

I first identified my corresponding files and began analyzing the ciphertexts.

### ✅ What I did:
- For the **substitution cipher**, I manually analyzed frequency patterns and decrypted the text. After decryption, I searched for and extracted the **random string** that was injected into the original plaintext.
- For the **Vigenère cipher**, I used frequency analysis and Kasiski examination to **guess the key length**, then **recover the key**, decrypt the text, and again identify the inserted **random string**.

It was really interesting to see how small variations and injected strings can still be isolated even when classical ciphers are used.

---

## 🔁 Assignment 2: Written Cryptographic Theory

This assignment had four problems, each focused on understanding theoretical foundations of encryption schemes and pseudorandom generators.

### Problem 1: Multi-Time XOR
I decrypted a ciphertext that was encrypted using a reused key (a Vigenère-like OTP using XOR). I:
- Guessed the key length,
- Recovered the key,
- Decrypted the ciphertext, and
- Extracted a 25-character **random string** from the end of the plaintext.

I submitted my answers through the provided Google Form.

### Problems 2–4: Handwritten Submissions
These were to be written and submitted physically:
- In **Problem 2**, I constructed and analyzed encryption schemes based on **perfect secrecy**.
- In **Problem 3**, I studied five constructions of **PRGs** and evaluated their security.
- In **Problem 4**, I described how to securely transmit messages using a **deck of cards** and proved why 49-bit messages can’t be securely sent in that model.

These problems deepened my understanding of formal cryptographic definitions and constraints.

---

## 💻 Assignment 3: Cryptanalysis Projects (Coding Based)

This assignment was all about breaking cryptographic systems practically. There were three main problems.

### Problem 1: Triple DES Analysis
I was given a faulty implementation of **Triple DES** in `problem1.py`, along with `string.txt`. I:
- Reverse engineered the flow of encryption,
- Created `mySerialNo_solution1.py` to interact with the script as if it were a remote service,
- Successfully recovered `string.txt` by simulating oracle-like queries.

### Problem 2: Image Encryption
Here, many `.png` images were encrypted using an unknown method. I:
- Analyzed multiple encrypted images,
- Recovered the key or reverse-engineered the encryption logic from `problem2.py`,
- Successfully **recovered all original images**, and from them reconstructed a **hidden random string**, saved as `mySerialNo_randomstring2.txt`.

### Problem 3: AES Command Oracle Attack
This was the toughest. I studied `problem3.py` which used AES via an external executable and allowed controlled encryption of commands. I:
- Treated the AES interface as an **encryption oracle**,
- Crafted inputs to leak info and bypass checks,
- Extracted the **random string in the secret folder**,
- Implemented everything in `mySerialNo_solution3.py`.

---

## 💻 Assignment 4: CryptoHack Challenges

Finally, I practiced solving real-world cryptographic puzzles on [CryptoHack](https://cryptohack.org/).

### Sections I solved:
- **Maths**
- **Diffie-Hellman**
- **Hash Functions**
- **RSA**

Each challenge gave me hands-on experience with number theory, modular arithmetic, discrete logs, and hash properties. I documented important observations and scripts in the respective folders.
