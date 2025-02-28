#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cctype>
#include <cmath>

using namespace std;

// ----------------------------------------------------
// Substitution cipher cryptoanalysis using frequency mapping
// ----------------------------------------------------
string substitutionCryptoanalysis(const string &cipherText) {
    // Count frequency of each letter (ignoring case)
    unordered_map<char, int> freq;
    for (char c : cipherText) {
        if (isalpha(c)) {
            char up = toupper(c);
            freq[up]++;
        }
    }

    // Create a vector from the frequency map and sort it in descending order
    vector<pair<char, int>> freqVec(freq.begin(), freq.end());
    sort(freqVec.begin(), freqVec.end(), [](auto &p1, auto &p2) {
        return p1.second > p2.second;
    });

    // Standard English letter frequency (from most frequent to least frequent)
    string engFreq = "ETAOINSHRDLCUMWFGYPBVKJXQZ";

    // Build a mapping based on the sorted frequency order.
    unordered_map<char, char> mapping;
    for (size_t i = 0; i < freqVec.size() && i < engFreq.size(); i++) {
        mapping[freqVec[i].first] = engFreq[i];
    }

    // Decrypt the cipher text using the mapping.
    string decrypted;
    for (char c : cipherText) {
        if (isalpha(c)) {
            char up = toupper(c);
            char decChar = mapping.count(up) ? mapping[up] : c;
            decrypted.push_back(decChar);
        } else {
            decrypted.push_back(c);
        }
    }
    return decrypted;
}

// ----------------------------------------------------
// Helper functions for Vigenère cryptoanalysis.
// Compute the index of coincidence (IC) for a text segment.
// ----------------------------------------------------
double computeIC(const string &text) {
    vector<int> counts(26, 0);
    int total = 0;
    for (char c : text) {
        if (isalpha(c)) {
            counts[toupper(c) - 'A']++;
            total++;
        }
    }
    if (total <= 1)
        return 0.0;
    double ic = 0.0;
    for (int count : counts) {
        ic += count * (count - 1);
    }
    ic /= (total * (total - 1));
    return ic;
}

// ----------------------------------------------------
// Chi-squared statistic computed using expected English letter frequencies.
// ----------------------------------------------------
double chiSquared(const vector<int> &counts, int total) {
    static double expected[26] = {
        8.167, 1.492, 2.782, 4.253, 12.702, 2.228,
        2.015, 6.094, 6.966, 0.153, 0.772, 4.025,
        2.406, 6.749, 7.507, 1.929, 0.095, 5.987,
        6.327, 9.056, 2.758, 0.978, 2.360, 0.150,
        1.974, 0.074
    };

    double chi2 = 0.0;
    for (int i = 0; i < 26; i++) {
        double observed = counts[i];
        double expCount = total * (expected[i] / 100.0);
        double diff = observed - expCount;
        chi2 += (diff * diff) / (expCount + 1e-6); // adding a tiny value to prevent division by zero
    }
    return chi2;
}

// ----------------------------------------------------
// Given a column of text (letters from positions modulo key length),
// try all shifts and return the shift (0-25) that minimizes the chi-squared statistic.
// ----------------------------------------------------
int guess_shift(const string &column) {
    int bestShift = 0;
    double bestChi = 1e9;
    for (int shift = 0; shift < 26; shift++) {
        vector<int> counts(26, 0);
        int total = 0;
        for (char c : column) {
            if (isalpha(c)) {
                char up = toupper(c);
                // Apply shift (simulate Caesar decryption)
                int value = (up - 'A' - shift + 26) % 26;
                counts[value]++;
                total++;
            }
        }
        if (total == 0)
            continue;
        double chi = chiSquared(counts, total);
        if (chi < bestChi) {
            bestChi = chi;
            bestShift = shift;
        }
    }
    return bestShift;
}

// ----------------------------------------------------
// Vigenère cipher cryptoanalysis.
// Uses a heuristic to decide on a key length, guesses the key using frequency analysis,
// and decrypts the ciphertext with the derived key.
// ----------------------------------------------------
string vigenereCryptoanalysis(const string &cipherText) {
    // Filter letters only for analysis (convert to uppercase)
    string filtered;
    for (char c : cipherText) {
        if (isalpha(c))
            filtered.push_back(toupper(c));
    }
    if (filtered.empty())
        return "";

    // Determine the most likely key length by selecting the one with the highest average IC.
    int bestKeyLen = 1;
    double bestIC = 0.0;
    int maxKeyLength = min(10, (int)filtered.size());
    for (int kl = 1; kl <= maxKeyLength; kl++) {
        double sumIC = 0.0;
        for (int i = 0; i < kl; i++) {
            string column;
            for (size_t j = i; j < filtered.size(); j += kl) {
                column.push_back(filtered[j]);
            }
            sumIC += computeIC(column);
        }
        double avgIC = sumIC / kl;
        if (avgIC > bestIC) {
            bestIC = avgIC;
            bestKeyLen = kl;
        }
    }

    // Using the chosen key length, guess a key.
    string key;
    key.resize(bestKeyLen);
    for (int i = 0; i < bestKeyLen; i++) {
        string column;
        for (size_t j = i; j < filtered.size(); j += bestKeyLen) {
            column.push_back(filtered[j]);
        }
        int shift = guess_shift(column);
        key[i] = 'A' + shift;
    }
    cout << "Guessed key: " << key << endl;

    // Decrypt the entire ciphertext using the recovered key.
    string plaintext;
    int keyIndex = 0;
    for (char c : cipherText) {
        if (isalpha(c)) {
            char up = toupper(c);
            int shift = key[keyIndex % key.size()] - 'A';
            int decVal = (up - 'A' - shift + 26) % 26;
            plaintext.push_back('A' + decVal);
            keyIndex++;
        } else {
            plaintext.push_back(c);
        }
    }
    return plaintext;
}

// ----------------------------------------------------
// Main function demonstrating both cryptoanalysis approaches.
// ----------------------------------------------------
int main() {
    string cipherSubstitution = "UIF RVJDL CSPXO GPy OFX BOTX"; // Example substitution ciphertext
    string cipherVigenere = "WMCEEIKLGRPIFVMEUGXQPWQVIOIAVEYXUEKFKBTALVXTGAFXYEVKPAGY"; // Example Vigenère ciphertext

    cout << "Substitution Cipher Analysis:" << endl;
    string decryptedSub = substitutionCryptoanalysis(cipherSubstitution);
    cout << "Decrypted text: " << decryptedSub << endl << endl;

    cout << "Vigenère Cipher Cryptoanalysis:" << endl;
    string decryptedVigenere = vigenereCryptoanalysis(cipherVigenere);
    cout << "Decrypted text: " << decryptedVigenere << endl;

    return 0;
}
