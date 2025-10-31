#!/usr/bin/env python3
"""
Professional PDF Reporting System for Password Cracking Results
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_report(self, session_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Generate professional HTML report for cracking session
        
        Args:
            session_data: Dictionary containing session information
            output_file: Path to save HTML file (optional)
            
        Returns:
            Path to generated report
        """
        
        # Default session data if not provided
        if not session_data:
            session_data = {
                'session_id': 'TEST123',
                'target_hash': '5f4dcc3b5aa765d61d8327deb882cf99',
                'hash_type': 'MD5',
                'method': 'Dictionary Attack',
                'wordlist': 'common.txt',
                'result': 'password',
                'attempts': 1250,
                'duration': 0.8,
                'rate': 1562,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat()
            }
        
        # Generate HTML report
        html_content = self._create_html_template(session_data)
        
        # Generate filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"cracking_report_{timestamp}.html")
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[✓] HTML report generated: {output_file}")
        return output_file
    
    def _create_html_template(self, data: Dict[str, Any]) -> str:
        """Create professional HTML template for report"""
        
        # Password strength analysis (if password was found)
        strength_analysis = ""
        if data.get('result') and data.get('result') != 'Not Found':
            strength_analysis = self._analyze_password_strength(data['result'])
        
        html_template = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Password Cracking Assessment Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 40px;
            background: #f9f9f9;
            color: #333;
        }}
        .report-container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .header p {{
            color: #7f8c8d;
            margin: 5px 0 0 0;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #3498db;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .info-item strong {{
            display: block;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            text-align: center;
            background: #3498db;
            color: white;
            padding: 20px;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            display: block;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .finding {{
            background: #e8f4fc;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        .recommendation {{
            background: #fff8e1;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 12px;
        }}
        .disclaimer {{
            background: #fef5e7;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #f39c12;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>🔒 Password Cracking Assessment Report</h1>
            <p>Professional Security Evaluation</p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="section">
            <h2>🎯 Assessment Overview</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Session ID</strong>
                    {data.get('session_id', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Target Hash</strong>
                    {data.get('target_hash', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Hash Type</strong>
                    {data.get('hash_type', 'Unknown').upper() if data.get('hash_type') else 'UNKNOWN'}
                </div>
                <div class="info-item">
                    <strong>Attack Method</strong>
                    {data.get('method', 'Unknown')}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Performance Metrics</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <span class="stat-value">{data.get('attempts', 0):,}</span>
                    <span class="stat-label">Attempts</span>
                </div>
                <div class="stat-box">
                    <span class="stat-value">{data.get('duration', 0):.2f}s</span>
                    <span class="stat-label">Duration</span>
                </div>
                <div class="stat-box">
                    <span class="stat-value">{data.get('rate', 0):,.0f}</span>
                    <span class="stat-label">Pwd/sec</span>
                </div>
                <div class="stat-box">
                    <span class="stat-value">{data.get('result', 'Not Found')}</span>
                    <span class="stat-label">Result</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Key Findings</h2>
            <div class="finding">
                <strong>Password Security Assessment:</strong>
                <p>The target hash was successfully cracked, revealing the password: <strong>{data.get('result', 'Not Found')}</strong></p>
            </div>
            
            {strength_analysis}
        </div>
        
        <div class="section">
            <h2>💡 Security Recommendations</h2>
            <div class="recommendation">
                <strong>Password Policy Enhancements:</strong>
                <ul>
                    <li>Enforce minimum password length of 12+ characters</li>
                    <li>Require complex character combinations (upper, lower, digits, symbols)</li>
                    <li>Implement password expiration policies</li>
                    <li>Use multi-factor authentication for sensitive accounts</li>
                    <li>Deploy password blacklists to prevent common/weak passwords</li>
                </ul>
            </div>
            
            <div class="recommendation">
                <strong>Technical Mitigations:</strong>
                <ul>
                    <li>Use strong, salted password hashing algorithms (bcrypt, Argon2)</li>
                    <li>Implement account lockout mechanisms after failed attempts</li>
                    <li>Monitor for unusual authentication patterns</li>
                    <li>Regularly audit password databases for weak credentials</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Technical Details</h2>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Start Time</td>
                    <td>{data.get('start_time', 'N/A')}</td>
                </tr>
                <tr>
                    <td>End Time</td>
                    <td>{data.get('end_time', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Wordlist Used</td>
                    <td>{data.get('wordlist', 'Default')}</td>
                </tr>
                <tr>
                    <td>Charset/Pattern</td>
                    <td>{data.get('charset', 'N/A')}</td>
                </tr>
            </table>
        </div>
        
        <div class="disclaimer">
            <strong>🛡️ Ethical Usage Notice:</strong>
            <p>This assessment was conducted for authorized penetration testing purposes only.
            All activities were performed within the scope of the engagement with proper written permission.
            Any discovered credentials should be handled according to responsible disclosure guidelines.</p>
        </div>
        
        <div class="footer">
            <p>Professional Password Cracking Assessment Report</p>
            <p>Generated by Advanced Password Security Toolkit</p>
            <p>Confidential - Authorized Personnel Only</p>
        </div>
    </div>
</body>
</html>
        '''
        return html_template
    
    def _analyze_password_strength(self, password: str) -> str:
        """Analyze password strength and generate security insights"""
        if not password or password == 'Not Found':
            return ""
        
        # Basic strength analysis
        score = 0
        feedback = []
        
        # Length scoring
        if len(password) >= 16:
            score += 25
        elif len(password) >= 12:
            score += 20
        elif len(password) >= 8:
            score += 15
        else:
            feedback.append("Password is too short")
            
        # Character variety
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variety_score = sum([has_lower, has_upper, has_digit, has_special])
        score += variety_score * 10
        
        if not has_lower:
            feedback.append("Missing lowercase letters")
        if not has_upper:
            feedback.append("Missing uppercase letters")
        if not has_digit:
            feedback.append("Missing numbers")
        if not has_special:
            feedback.append("Missing special characters")
            
        # Determine strength level
        if score >= 80:
            strength = "Strong"
            color = "#27ae60"
        elif score >= 60:
            strength = "Moderate"
            color = "#f39c12"
        else:
            strength = "Weak"
            color = "#e74c3c"
        
        feedback_html = ""
        if feedback:
            feedback_list = "".join([f"<li>{item}</li>" for item in feedback])
            feedback_html = f'''
            <div class="recommendation">
                <strong>Issues Identified:</strong>
                <ul>{feedback_list}</ul>
            </div>
            '''
        
        analysis_html = f'''
        <div class="finding">
            <strong>Password Strength Analysis:</strong>
            <p>Evaluated password: <strong>{password}</strong></p>
            <p>Security Score: <strong style="color: {color}">{score}/100 ({strength})</strong></p>
        </div>
        {feedback_html}
        '''
        
        return analysis_html
    
    def generate_json_report(self, session_data: Dict[str, Any], output_file: str = None) -> str:
        """Generate JSON report for programmatic use"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"cracking_report_{timestamp}.json")
        
        report_data = {
            'metadata': {
                'report_type': 'password_cracking_assessment',
                'generated_at': datetime.now().isoformat(),
                'tool_version': '3.0'
            },
            'session_data': session_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"[✓] JSON report generated: {output_file}")
        return output_file

# Example usage when running standalone
if __name__ == "__main__":
    generator = ReportGenerator()
    
    # Sample session data for demo
    sample_data = {
        'session_id': 'CRK20250101',
        'target_hash': '5f4dcc3b5aa765d61d8327deb882cf99',
        'hash_type': 'md5',
        'method': 'Dictionary Attack with Mutations',
        'wordlist': 'common.txt',
        'charset': 'N/A',
        'result': 'password',
        'attempts': 2345,
        'duration': 1.2,
        'rate': 1954,
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat()
    }
    
    # Generate both HTML and JSON reports
    html_report = generator.generate_html_report(sample_data)
    json_report = generator.generate_json_report(sample_data)
    
    print(f"[✓] Sample reports generated successfully!")
    print(f"    HTML Report: {html_report}")
    print(f"    JSON Report: {json_report}")
