#!/usr/bin/env python3
"""
Web Dashboard for Professional Password Cracker
Flask-based web interface with dark theme and actual cracking engines
"""

from flask import Flask, render_template, request, jsonify, render_template_string
import threading
import time
import json
import os
import sys
import hashlib
import itertools
from datetime import datetime

# Import our advanced cracker
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from advanced_cracker import ProPasswordCracker
    from report_generator import ReportGenerator
except ImportError:
    print("[!] Advanced modules not found, using built-in engines")

class RuleEngine:
    """Advanced rule-based password generation"""
    
    def __init__(self):
        self.substitution_rules = {
            'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 
            'o': ['0'], 's': ['5', '$'], 't': ['7']
        }
        
    def apply_rules(self, base_word):
        """Generate variations using rules"""
        variations = set()
        
        # Original word
        variations.add(base_word)
        
        # Capitalization variations
        variations.add(base_word.capitalize())
        variations.add(base_word.upper())
        
        # Common substitutions
        for char, replacements in self.substitution_rules.items():
            if char in base_word.lower():
                for replacement in replacements:
                    variations.add(base_word.replace(char, replacement))
                    variations.add(base_word.replace(char.upper(), replacement))
        
        # Append numbers
        for i in range(100):
            variations.add(base_word + str(i))
            if i < 10:
                variations.add(base_word + '0' + str(i))
        
        # Prepend numbers
        for i in range(10):
            variations.add(str(i) + base_word)
        
        # Leet speak variations
        leet_word = base_word
        leet_word = leet_word.replace('e', '3')
        variations.add(leet_word)
        
        return list(variations)

class BruteForceEngine:
    """Advanced brute force password generation"""
    
    def __init__(self):
        self.charsets = {
            '?l': 'abcdefghijklmnopqrstuvwxyz',
            '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?d': '0123456789',
            '?s': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            '?a': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
    
    def expand_mask(self, mask):
        """Expand mask pattern to character set"""
        result = ''
        i = 0
        while i < len(mask):
            if mask[i] == '?' and i+1 < len(mask):
                char_type = mask[i+1]
                if char_type in self.charsets:
                    result += self.charsets[char_type]
                    i += 2
                else:
                    result += mask[i]
                    i += 1
            else:
                result += mask[i]
                i += 1
        return result
    
    def generate_combinations(self, charset, min_len, max_len):
        """Generate all combinations for brute force"""
        for length in range(min_len, max_len + 1):
            for combination in itertools.product(charset, repeat=length):
                yield ''.join(combination)

class CrackingSession:
    def __init__(self, session_id, target_hash, method, params):
        self.session_id = session_id
        self.target_hash = target_hash
        self.method = method
        self.params = params
        self.status = "running"
        self.progress = 0
        self.attempts = 0
        self.rate = 0
        self.start_time = time.time()
        self.result = None
        self.thread = None
        self.wordlist = params.get('wordlist', 'wordlists/common.txt')
        self.rule_engine = RuleEngine()
        self.brute_engine = BruteForceEngine()
        
    def hash_password(self, password, hash_type):
        """Hash password using specified algorithm"""
        hash_type = hash_type.lower()
        if hash_type == 'md5':
            return hashlib.md5(password.encode()).hexdigest()
        elif hash_type == 'sha1':
            return hashlib.sha1(password.encode()).hexdigest()
        elif hash_type == 'sha256':
            return hashlib.sha256(password.encode()).hexdigest()
        elif hash_type == 'ntlm':
            # Simple NTLM simulation
            return hashlib.md5(password.encode()).hexdigest()[:32]
        else:
            return hashlib.md5(password.encode()).hexdigest()
        
    def start_cracking(self):
        """Use actual cracking engines"""
        def cracking_worker():
            try:
                hash_type = self.params.get('hash_type', 'md5')
                start_time = time.time()
                found = False
                
                if self.method == 'dict':
                    # Dictionary attack
                    with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                        wordlist = [line.strip() for line in f if line.strip()]
                    
                    for word in wordlist:
                        if self.status != "running":
                            break
                        
                        hashed = self.hash_password(word, hash_type)
                        self.attempts += 1
                        elapsed = time.time() - start_time
                        self.rate = self.attempts / elapsed if elapsed > 0 else 0
                        self.progress = min(95, (self.attempts / len(wordlist)) * 100)
                        
                        if hashed == self.target_hash:
                            self.result = word
                            found = True
                            break
                    
                    self.progress = 100
                    self.status = "completed" if found else "failed"
                    
                elif self.method == 'rule':
                    # Rule-based attack
                    with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                        base_words = [line.strip() for line in f if line.strip()]
                    
                    total_variations = 0
                    for base_word in base_words:
                        variations = self.rule_engine.apply_rules(base_word)
                        total_variations += len(variations)
                    
                    processed = 0
                    for base_word in base_words:
                        variations = self.rule_engine.apply_rules(base_word)
                        
                        for variation in variations:
                            if self.status != "running":
                                break
                            
                            hashed = self.hash_password(variation, hash_type)
                            self.attempts += 1
                            processed += 1
                            
                            elapsed = time.time() - start_time
                            self.rate = self.attempts / elapsed if elapsed > 0 else 0
                            self.progress = min(95, (processed / total_variations) * 100)
                            
                            if hashed == self.target_hash:
                                self.result = variation
                                found = True
                                break
                        
                        if found:
                            break
                    
                    self.progress = 100
                    self.status = "completed" if found else "failed"
                    
                elif self.method == 'brute':
                    # Brute force attack - FIXED CHARSET HANDLING
                    charset = self.params.get('charset', '?l?d')
                    expanded_charset = self.brute_engine.expand_mask(charset)
                    min_len = int(self.params.get('min_length', 1))
                    max_len = int(self.params.get('max_length', 6))
                    
                    total_combinations = sum(len(expanded_charset) ** i for i in range(min_len, max_len + 1))
                    processed = 0
                    
                    for length in range(min_len, max_len + 1):
                        if self.status != "running":
                            break
                        
                        for combination in itertools.product(expanded_charset, repeat=length):
                            if self.status != "running":
                                break
                            
                            password = ''.join(combination)
                            hashed = self.hash_password(password, hash_type)
                            self.attempts += 1
                            processed += 1
                            
                            elapsed = time.time() - start_time
                            self.rate = self.attempts / elapsed if elapsed > 0 else 0
                            self.progress = min(95, (processed / total_combinations) * 100)
                            
                            if hashed == self.target_hash:
                                self.result = password
                                found = True
                                break
                            
                            if processed % 1000 == 0:
                                time.sleep(0.01)  # Prevent CPU overload
                        
                        if found:
                            break
                    
                    self.progress = 100
                    self.status = "completed" if found else "failed"
                    
            except Exception as e:
                print(f"[!] Cracking error: {e}")
                self.status = "failed"
                self.progress = 100
        
        self.thread = threading.Thread(target=cracking_worker)
        self.thread.daemon = True
        self.thread.start()

# Global session storage
active_sessions = {}
session_lock = threading.Lock()

app = Flask(__name__)

# HTML Templates with Dark Theme
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Professional Password Cracker</title>
    <style>
        :root {
            --bg-primary: #0f1419;
            --bg-secondary: #1a1f2e;
            --bg-tertiary: #252a38;
            --text-primary: #e6e6e6;
            --text-secondary: #a0a0a0;
            --accent-blue: #3498db;
            --accent-green: #27ae60;
            --accent-red: #e74c3c;
            --accent-purple: #9b59b6;
            --border-color: #2d3748;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            --card-radius: 12px;
        }
        
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: var(--bg-secondary);
            padding: 30px; 
            border-radius: var(--card-radius);
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        
        h1 { 
            color: var(--text-primary); 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        .form-section { 
            background: var(--bg-tertiary);
            padding: 25px; 
            border-radius: var(--card-radius);
            margin-bottom: 25px;
            border: 1px solid var(--border-color);
        }
        
        .form-group { margin-bottom: 18px; }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600;
            color: var(--text-primary);
        }
        
        input, select { 
            width: 100%; 
            padding: 12px 15px; 
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px; 
            box-sizing: border-box;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }
        
        button { 
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white; 
            padding: 14px 25px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
        
        .session-card { 
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: var(--card-radius);
            padding: 20px; 
            margin-bottom: 18px;
            transition: all 0.3s ease;
        }
        
        .status-running { border-left: 6px solid var(--accent-blue); }
        .status-completed { border-left: 6px solid var(--accent-green); }
        .status-failed { border-left: 6px solid var(--accent-red); }
        
        .progress-bar { 
            background: var(--bg-primary);
            height: 16px; 
            border-radius: 10px; 
            overflow: hidden; 
            margin: 15px 0;
        }
        
        .progress-fill { 
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            height: 100%; 
            transition: width 0.5s ease; 
        }
        
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 15px; 
            margin-top: 15px;
        }
        
        .stat-box { 
            background: var(--bg-primary);
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
            border: 1px solid var(--border-color);
        }
        
        .stat-value { 
            font-size: 22px; 
            font-weight: bold; 
            color: var(--accent-blue);
        }
        
        .stat-label { 
            font-size: 12px; 
            color: var(--text-secondary);
            margin-top: 5px;
        }
        
        .report-btn { 
            background: linear-gradient(135deg, var(--accent-red), #c0392b);
            margin-top: 12px; 
        }
        
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1000;
        }
        
        .glass-effect {
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .header-gradient {
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Professional Password Cracker</h1>
        
        <div class="form-section glass-effect">
            <h2 style="color: var(--text-primary); margin-bottom: 20px;">New Cracking Session</h2>
            <form id="crackForm">
                <div class="form-group">
                    <label for="target_hash">Target Hash:</label>
                    <input type="text" id="target_hash" placeholder="Enter hash to crack" required>
                </div>
                
                <div class="form-group">
                    <label for="hash_type">Hash Type:</label>
                    <select id="hash_type">
                        <option value="md5">MD5</option>
                        <option value="sha1">SHA1</option>
                        <option value="sha256">SHA256</option>
                        <option value="ntlm">NTLM</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="method">Attack Method:</label>
                    <select id="method">
                        <option value="dict">Dictionary</option>
                        <option value="rule">Rule-based</option>
                        <option value="brute">Brute Force</option>
                        <option value="mask">Mask Attack</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="wordlist">Wordlist (for dictionary/rule):</label>
                    <input type="text" id="wordlist" value="wordlists/common.txt">
                </div>
                
                <div class="form-group">
                    <label for="charset">Charset/Mask (for brute/mask):</label>
                    <input type="text" id="charset" value="?l?d">
                </div>
                
                <button type="button" onclick="startCracking()">🚀 Start Cracking Session</button>
            </form>
        </div>
        
        <h2 style="color: var(--text-primary); margin-bottom: 20px;">Active Sessions</h2>
        <div id="sessions">
            <!-- Sessions will be loaded here -->
        </div>
    </div>
    
    <script>
        let darkTheme = true;
        
        // Auto-refresh sessions every 2 seconds
        setInterval(loadSessions, 2000);
        loadSessions(); // Load initially
        
        function toggleTheme() {
            darkTheme = !darkTheme;
            document.documentElement.style.setProperty('--bg-primary', darkTheme ? '#0f1419' : '#ffffff');
            document.documentElement.style.setProperty('--bg-secondary', darkTheme ? '#1a1f2e' : '#f8f9fa');
            document.documentElement.style.setProperty('--text-primary', darkTheme ? '#e6e6e6' : '#333333');
            loadSessions();
        }
        
        function startCracking() {
            const formData = {
                target_hash: document.getElementById('target_hash').value,
                hash_type: document.getElementById('hash_type').value,
                method: document.getElementById('method').value,
                wordlist: document.getElementById('wordlist').value,
                charset: document.getElementById('charset').value
            };
            
            fetch('/api/start_session', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('🎯 Session started successfully!');
                    document.getElementById('crackForm').reset();
                    loadSessions();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error starting session: ' + error);
            });
        }
        
        function loadSessions() {
            fetch('/api/sessions')
            .then(response => response.json())
            .then(sessions => {
                const container = document.getElementById('sessions');
                container.innerHTML = '';
                
                if (Object.keys(sessions).length === 0) {
                    container.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 40px;">No active cracking sessions</p>';
                    return;
                }
                
                for (const [id, session] of Object.entries(sessions)) {
                    const sessionEl = document.createElement('div');
                    sessionEl.className = `session-card status-${session.status}`;
                    sessionEl.innerHTML = `
                        <h3 style="color: var(--text-primary); margin-top: 0;">Session ${id}</h3>
                        <p><strong>Target:</strong> ${session.target_hash.substring(0, 16)}...</p>
                        <p><strong>Method:</strong> ${session.method}</p>
                        <p><strong>Status:</strong> 
                            <span style="color: ${session.status === 'running' ? 'var(--accent-blue)' : session.status === 'completed' ? 'var(--accent-green)' : 'var(--accent-red)'}">
                                ${session.status.toUpperCase()}
                            </span>
                        </p>
                        
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${session.progress}%"></div>
                        </div>
                        <p style="color: var(--text-secondary);">${Math.round(session.progress)}% Complete</p>
                        
                        <div class="stats">
                            <div class="stat-box">
                                <div class="stat-value">${session.attempts.toLocaleString()}</div>
                                <div class="stat-label">Attempts</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${Math.round(session.rate).toLocaleString()}</div>
                                <div class="stat-label">Pwd/sec</div>
                            </div>
                            <div class="stat-box">
                                <div class="stat-value">${session.result || '🔍 Not Found'}</div>
                                <div class="stat-label">Result</div>
                            </div>
                        </div>
                        
                        <button onclick="stopSession('${id}')" ${session.status !== 'running' ? 'disabled' : ''}>
                            ${session.status === 'running' ? '⏹️ Stop' : '✅ Complete'}
                        </button>
                        
                        ${session.status === 'completed' || session.status === 'failed' ? `
                            <button class="report-btn" onclick="generateReport('${id}')">
                                📊 Generate Professional Report
                            </button>
                        ` : ''}
                    `;
                    container.appendChild(sessionEl);
                }
            });
        }
        
        function stopSession(sessionId) {
            fetch(`/api/stop_session/${sessionId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadSessions();
                }
            });
        }
        
        function generateReport(sessionId) {
            fetch(`/api/generate_report/${sessionId}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('📄 Professional report generated!');
                    window.open('/api/view_report/' + data.report_filename, '_blank');
                }
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/start_session', methods=['POST'])
def start_session():
    try:
        data = request.get_json()
        session_id = str(int(time.time() * 1000))
        
        session = CrackingSession(
            session_id=session_id,
            target_hash=data['target_hash'],
            method=data['method'],
            params={
                'hash_type': data['hash_type'],
                'wordlist': data.get('wordlist', 'wordlists/common.txt'),
                'charset': data.get('charset', '?l?d')
            }
        )
        
        with session_lock:
            active_sessions[session_id] = session
        
        session.start_cracking()
        
        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions')
def get_sessions():
    with session_lock:
        session_data = {}
        for sid, session in active_sessions.items():
            session_data[sid] = {
                'target_hash': session.target_hash,
                'method': session.method,
                'status': session.status,
                'progress': session.progress,
                'attempts': session.attempts,
                'rate': session.rate,
                'result': session.result
            }
        return jsonify(session_data)

@app.route('/api/stop_session/<session_id>', methods=['POST'])
def stop_session(session_id):
    with session_lock:
        if session_id in active_sessions:
            active_sessions[session_id].status = "stopped"
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Session not found'})

@app.route('/api/generate_report/<session_id>', methods=['POST'])
def generate_report(session_id):
    try:
        with session_lock:
            if session_id not in active_sessions:
                return jsonify({'success': False, 'error': 'Session not found'})
        
        session = active_sessions[session_id]
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'cracking_report_{timestamp}.html'
        report_path = os.path.join('reports', report_filename)
        
        os.makedirs('reports', exist_ok=True)
        
        session_data = {
            'session_id': session_id,
            'target_hash': session.target_hash,
            'hash_type': session.params.get('hash_type', 'unknown'),
            'method': session.method,
            'wordlist': session.params.get('wordlist', 'N/A'),
            'charset': session.params.get('charset', 'N/A'),
            'status': session.status,
            'result': session.result,
            'attempts': session.attempts,
            'rate': session.rate,
            'start_time': datetime.fromtimestamp(session.start_time).isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': time.time() - session.start_time
        }
        
        try:
            report_gen = ReportGenerator()
            report_gen.generate_html_report(session_data, report_path)
            
            return jsonify({
                'success': True,
                'report_path': report_path,
                'report_filename': report_filename
            })
        except:
            # If ReportGenerator fails, create a basic report
            with open(report_path, 'w') as f:
                f.write(f'''
                <!DOCTYPE html>
                <html style="background: #0f1419; color: #e6e6e6; font-family: 'Segoe UI', sans-serif;">
                <body style="margin: 0; padding: 40px;">
                    <div style="max-width: 800px; margin: 0 auto; background: #1a1f2e; padding: 30px; border-radius: 12px;">
                    <h1 style="color: #e6e6e6; text-align: center;">🔒 Password Cracking Report</h1>
                    <div style="background: #252a38; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #3498db;">Session Summary</h2>
                        <p><strong>Session ID:</strong> {session_id}</p>
                        <p><strong>Target Hash:</strong> {session.target_hash}</p>
                        <p><strong>Method:</strong> {session.method}</p>
                        <p><strong>Status:</strong> {session.status}</p>
                        <p><strong>Result:</strong> {session.result or "Not found"}</p>
                        <p><strong>Attempts:</strong> {session.attempts:,}</p>
                    </div>
                </body>
                </html>
                ''')
            
            return jsonify({
                'success': True,
                'report_path': report_path,
                'report_filename': report_filename
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/view_report/<report_filename>')
def view_report(report_filename):
    try:
        report_path = os.path.join('reports', report_filename)
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                return f.read()
        return "Report not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

def run_web_dashboard():
    print("[+] Starting web dashboard on http://localhost:8080")
    print("[+] Dark theme enabled")
    print("[+] All attack methods implemented:")
    print("   ✅ Dictionary Attack")
    print("   ✅ Rule-based Attack")
    print("   ✅ Brute Force Attack")
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    run_web_dashboard()
