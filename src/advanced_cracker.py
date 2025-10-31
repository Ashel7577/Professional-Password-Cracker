#!/usr/bin/env python3
"""
Advanced Password Cracker with real rule-based and brute force engines
"""

import hashlib
import itertools
import time
import os

class ProPasswordCracker:
    def __init__(self, target_hash, hash_type='md5'):
        self.target_hash = target_hash
        self.hash_type = hash_type.lower()
        self.found = False
        self.result = None
        self.attempts = 0
        self.rate = 0
        self.start_time = None
        
    def hash_password(self, password):
        """Hash password using specified algorithm"""
        if self.hash_type == 'md5':
            return hashlib.md5(password.encode()).hexdigest()
        elif self.hash_type == 'sha1':
            return hashlib.sha1(password.encode()).hexdigest()
        elif self.hash_type == 'sha256':
            return hashlib.sha256(password.encode()).hexdigest()
        elif self.hash_type == 'ntlm':
            # Simple NTLM simulation
            return hashlib.md5(password.encode()).hexdigest()[:32]
        else:
            return hashlib.md5(password.encode()).hexdigest()
    
    def dictionary_attack(self, wordlist_path, rules=False):
        """Dictionary attack with optional rule application"""
        self.start_time = time.time()
        
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[!] Wordlist not found: {wordlist_path}")
            return
        
        if rules:
            # Apply rules to each word
            for base_word in words:
                variations = self._apply_rules(base_word)
                for variation in variations:
                    if self.found:
                        return
                    
                    hashed = self.hash_password(variation)
                    self.attempts += 1
                    self._update_rate()
                    
                    if hashed == self.target_hash:
                        self.result = variation
                        self.found = True
                        return
        else:
            # Simple dictionary attack
            for word in words:
                if self.found:
                    return
                
                hashed = self.hash_password(word)
                self.attempts += 1
                self._update_rate()
                
                if hashed == self.target_hash:
                    self.result = word
                    self.found = True
                    return
    
    def _apply_rules(self, base_word):
        """Apply common password rules to generate variations"""
        variations = set()
        
        # Original word
        variations.add(base_word)
        
        # Capitalization variations
        variations.add(base_word.capitalize())
        variations.add(base_word.upper())
        
        # Common substitutions
        substitution_rules = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 
            'o': ['0'], 's': ['5', '$'], 't': ['7']
        }
        
        for char, replacements in substitution_rules.items():
            if char in base_word.lower():
                for replacement in replacements:
                    variations.add(base_word.replace(char, replacement))
                    variations.add(base_word.replace(char.upper(), replacement))
        
        # Append numbers (0-99)
        for i in range(100):
            variations.add(base_word + str(i))
            if i < 10:
                variations.add(base_word + '0' + str(i))
        
        # Prepend numbers (0-9)
        for i in range(10):
            variations.add(str(i) + base_word)
        
        # Common patterns
        variations.add(base_word + '123')
        variations.add(base_word + '!')
        
        return list(variations)
    
    def brute_force_attack(self, charset_pattern, min_length=1, max_length=6):
        """Brute force attack with configurable charset"""
        self.start_time = time.time()
        
        # Expand mask pattern
        charset = self._expand_mask(charset_pattern)
        
        total_combinations = sum(len(charset) ** i for i in range(min_length, max_length + 1))
        
        for length in range(min_length, max_length + 1):
            for combination in itertools.product(charset, repeat=length):
                if self.found:
                    return
                
                password = ''.join(combination)
                hashed = self.hash_password(password)
                self.attempts += 1
                
                if self.attempts % 1000 == 0:
                    self._update_rate()
                
                if hashed == self.target_hash:
                    self.result = password
                    self.found = True
                    return
    
    def _expand_mask(self, mask):
        """Expand mask pattern to character set"""
        charsets = {
            '?l': 'abcdefghijklmnopqrstuvwxyz',
            '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?d': '0123456789',
            '?s': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            '?a': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
        
        result = ''
        i = 0
        while i < len(mask):
            if mask[i] == '?' and i+1 < len(mask):
                char_type = mask[i+1]
                if char_type in charsets:
                    result += charsets[char_type]
                    i += 2
                else:
                    result += mask[i]
                    i += 1
            else:
                result += mask[i]
                i += 1
        return result
    
    def mask_attack(self, mask):
        """Mask attack using specified pattern"""
        self.start_time = time.time()
        
        # For now, treat mask as charset for brute force
        charset = self._expand_mask(mask)
        
        # Generate passwords of mask length
        length = len(mask)
        
        for combination in itertools.product(charset, repeat=length):
            if self.found:
                return
            
            password = ''.join(combination)
            hashed = self.hash_password(password)
            self.attempts += 1
            
            if self.attempts % 1000 == 0:
                self._update_rate()
            
            if hashed == self.target_hash:
                self.result = password
                self.found = True
                return
    
    def _update_rate(self):
        """Update cracking rate"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.rate = self.attempts / elapsed if elapsed > 0 else 0
    
    def get_stats(self):
        """Get current cracking statistics"""
        return {
            'attempts': self.attempts,
            'rate': self.rate,
            'found': self.found,
            'result': self.result
        }

if __name__ == '__main__':
    # Test the cracker
    test_hash = hashlib.md5('password123'.encode()).hexdigest()
    cracker = ProPasswordCracker(test_hash, 'md5')
    cracker.dictionary_attack('wordlists/common.txt', rules=True)
    print(f"Stats: {cracker.get_stats()}")
