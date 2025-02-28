#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <cctype>
#include <numeric>
using namespace std;
// Function to read a file into a string
string readFile(const string &filePath) {
    ifstream file(filePath);
    if (!file) {
        cerr << "Error: Could not open file " << filePath << endl;
        exit(1);
    }
    string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    return content;
}

// Frequency analysis for substitution cipher
map<char, char> frequencyAnalysis(const string &ciphertext) {
    map<char, int> freq;
    for (char c : ciphertext) {
        if (isalpha(c)) freq[c]++;
    }
    // Sort frequencies in descending order
    vector<pair<char, int>> sortedFreq(freq.begin(), freq.end());
    sort(sortedFreq.begin(), sortedFreq.end(), [](auto &a, auto &b) { return a.second > b.second; });
    // Map ciphertext letters to English letter frequency order
    string englishFreq = "etaoinshrdlcumwfgypbvkjxqz";
    map<char, char> mapping;
    for (size_t i = 0; i < sortedFreq.size() && i < englishFreq.size(); i++) {
        mapping[sortedFreq[i].first] = englishFreq[i];
    }
    return mapping;
}
// Decrypt substitution cipher using the mapping
string decryptSubstitution(const string &ciphertext, const map<char, char> &mapping) {
    string plaintext;
    for (char c : ciphertext) {
        if (mapping.count(c)) {
            plaintext += mapping.at(c);
        } else {
            plaintext += c;
        }
    }
    return plaintext;
}
// Task 1: Identify random string
string findRandomString(const string &decryptedText, const string &referenceText) {
    string randomString;
    size_t refPos = 0;

    for (char c : decryptedText) {
        if (refPos < referenceText.size() && c == referenceText[refPos]) {
            refPos++;
        } else if (isalpha(c)) {
            randomString += c;
        }
    }
    return randomString;
}
// Find the key length using Kasiski examination for Vigenère cipher
int findKeyLength(const string &ciphertext) {
    int keyLength = 1;
    int maxLength = min((int)ciphertext.size(), 20);

    vector<int> coincidences(maxLength, 0);
    for (int shift = 1; shift < maxLength; shift++) {
        for (size_t i = 0; i + shift < ciphertext.size(); i++) {
            if (ciphertext[i] == ciphertext[i + shift]) {
                coincidences[shift]++;
            }
        }
    }
    keyLength = max_element(coincidences.begin(), coincidences.end()) - coincidences.begin();
    return keyLength;
}
// Find the Vigenère cipher key using frequency analysis
string findVigenereKey(const string &ciphertext, int keyLength) {
    string key;
    string englishFreq = "etaoinshrdlcumwfgypbvkjxqz";
    for (int i = 0; i < keyLength; i++) {
        map<char, int> freq;
        for (size_t j = i; j < ciphertext.size(); j += keyLength) {
            freq[ciphertext[j]]++;
        }
        char mostFrequent = max_element(freq.begin(), freq.end(),
                                        [](auto &a, auto &b) { return a.second < b.second; })
                                ->first;

        char keyChar = (mostFrequent - 'A' - ('E' - 'A') + 26) % 26 + 'A';
        key += keyChar;
    }

    return key;
}

// Decrypt Vigenère cipher using the key
string decryptVigenere(const string &ciphertext, const string &key) {
    string plaintext;
    size_t keyLength = key.size();

    for (size_t i = 0; i < ciphertext.size(); i++) {
        if (isalpha(ciphertext[i])) {
            char offset = isupper(ciphertext[i]) ? 'A' : 'a';
            char plainChar = (ciphertext[i] - key[i % keyLength] + 26) % 26 + offset;
            plaintext += plainChar;
        } else {
            plaintext += ciphertext[i];
        }
    }
    return plaintext;
}

// Main function
int main() {
    // File paths
    string substitutionFile = "ciphertext_test_72.txt";
    string vigenereFile = "v_ciphertext_72.txt";
    string referenceFile = "NetworkWorkingGroup.txt"; // Reference text file

    // Task 1: Substitution cipher
    string substitutionCipher = readFile(substitutionFile);
    map<char, char> substitutionMapping = frequencyAnalysis(substitutionCipher);
    string decryptedSubstitution = decryptSubstitution(substitutionCipher, substitutionMapping);
    cout << "Decrypted Substitution Cipher: \n" << decryptedSubstitution << endl;

    // Read reference plaintext from file
    string referenceText = readFile(referenceFile);
    string randomStringSub = findRandomString(decryptedSubstitution, referenceText);
    cout << "Random String (Substitution): " << randomStringSub << endl;

    // Task 2: Vigenère cipher
    string vigenereCipher = readFile(vigenereFile);
    int keyLength = findKeyLength(vigenereCipher);
    string vigenereKey = findVigenereKey(vigenereCipher, keyLength);
    string decryptedVigenere = decryptVigenere(vigenereCipher, vigenereKey);
    cout << "Decrypted Vigenère Cipher: \n" << decryptedVigenere << endl;
    cout << "Key: " << vigenereKey << endl;

    // Identify random string in Vigenère plaintext
    string randomStringVigenere = findRandomString(decryptedVigenere, referenceText);
    cout << "Random String (Vigenère): " << randomStringVigenere << endl;

    return 0;
}