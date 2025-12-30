"""
Flask Weight Monitor Web Application - Multi-Machine Support
Supports multiple machines with separate weight files
Deploy to Render.com
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================
DATA_DIR = 'machine_data'  # Directory to store weight data for each machine

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# ============================================================================
# Helper Functions
# ============================================================================

def get_machine_file(machine_id):
    """Get the file path for a specific machine."""
    return os.path.join(DATA_DIR, f'machine_{machine_id}.json')

def save_weight_data(machine_id, weight):
    """Save weight data for a specific machine."""
    data = {
        'machine_id': machine_id,
        'weight': weight,
        'timestamp': datetime.now().isoformat(),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        file_path = get_machine_file(machine_id)
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(f"Error saving data for machine {machine_id}: {e}")
        return False

def load_weight_data(machine_id):
    """Load weight data for a specific machine."""
    try:
        file_path = get_machine_file(machine_id)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading data for machine {machine_id}: {e}")
        return None

def get_all_machines():
    """Get list of all machines with data."""
    machines = []
    try:
        for filename in os.listdir(DATA_DIR):
            if filename.startswith('machine_') and filename.endswith('.json'):
                machine_id = filename.replace('machine_', '').replace('.json', '')
                data = load_weight_data(machine_id)
                if data:
                    machines.append({
                        'machine_id': machine_id,
                        'weight': data['weight'],
                        'last_updated': data.get('last_updated', 'Unknown')
                    })
        return machines
    except Exception as e:
        print(f"Error getting machines: {e}")
        return []

# ============================================================================
# HTML Template
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weight Monitor - Multi-Machine</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 480px;
            width: 100%;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        
        .machine-selector {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .machine-label {
            font-size: 12px;
            text-transform: uppercase;
            color: #6c757d;
            letter-spacing: 1px;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .machine-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        
        .machine-btn {
            padding: 12px;
            border: 2px solid #dee2e6;
            background: white;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
            color: #495057;
        }
        
        .machine-btn:hover {
            border-color: #667eea;
            transform: translateY(-2px);
        }
        
        .machine-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .status-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #6c757d;
        }
        
        .status-dot.success {
            background: #28a745;
            animation: pulse 2s infinite;
        }
        
        .status-dot.waiting {
            background: #ffc107;
        }
        
        .status-dot.error {
            background: #dc3545;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .status-text {
            color: #495057;
            font-size: 14px;
            font-weight: 500;
        }
        
        .weight-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 40px 20px;
            text-align: center;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .weight-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.9;
            margin-bottom: 15px;
        }
        
        .weight-value {
            font-size: 64px;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 5px;
        }
        
        .weight-unit {
            font-size: 24px;
            opacity: 0.8;
            margin-left: 5px;
        }
        
        .machine-badge {
            display: inline-block;
            padding: 6px 16px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .timestamp-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
        }
        
        .timestamp-label {
            font-size: 11px;
            text-transform: uppercase;
            color: #6c757d;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        
        .timestamp-value {
            color: #212529;
            font-size: 15px;
            font-weight: 500;
        }
        
        .button-group {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            flex: 1;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e9ecef;
            color: #495057;
        }
        
        .btn-secondary:hover:not(:disabled) {
            background: #dee2e6;
        }
        
        .btn-secondary.active {
            background: #28a745;
            color: white;
        }
        
        .auto-info {
            text-align: center;
            margin-top: 12px;
            font-size: 13px;
            color: #6c757d;
        }
        
        .no-data {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        
        .no-data-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #6c757d;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">⚖️</div>
            <h1>Weight Monitor</h1>
            <p class="subtitle">Multi-Machine Tracking System</p>
        </div>
        
        <div class="machine-selector">
            <div class="machine-label">Select Machine</div>
            <div class="machine-buttons">
                <button class="machine-btn active" onclick="selectMachine('1')">
                    🔧 Machine 1
                </button>
                <button class="machine-btn" onclick="selectMachine('2')">
                    🔧 Machine 2
                </button>
                <button class="machine-btn" onclick="selectMachine('3')">
                    🔧 Machine 3
                </button>
                <button class="machine-btn" onclick="selectMachine('4')">
                    🔧 Machine 4
                </button>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-dot" id="statusDot"></div>
            <span class="status-text" id="statusText">Initializing...</span>
        </div>
        
        <div id="content">
            <div class="loading">
                <div class="spinner"></div>
                <p>Loading weight data...</p>
            </div>
        </div>
        
        <div class="button-group">
            <button class="btn btn-primary" id="getWeightBtn" onclick="getWeight()">
                🔄 Get Weight
            </button>
            <button class="btn btn-secondary" id="autoBtn" onclick="toggleAuto()">
                Auto: OFF
            </button>
        </div>
        
        <div class="auto-info" id="autoInfo"></div>
    </div>

    <script>
        let selectedMachine = '1';
        let autoRefresh = false;
        let autoInterval = null;
        let countdown = 5;
        let countdownInterval = null;

        function selectMachine(machineId) {
            selectedMachine = machineId;
            
            // Update button states
            document.querySelectorAll('.machine-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Load data for selected machine
            getWeight();
        }

        async function getWeight() {
            const btn = document.getElementById('getWeightBtn');
            btn.disabled = true;
            btn.innerHTML = '⏳ Loading...';
            
            updateStatus('loading', `Fetching Machine ${selectedMachine} data...`);
            
            try {
                const response = await fetch(`/api/weight/${selectedMachine}`);
                const data = await response.json();
                displayWeight(data);
            } catch (error) {
                handleError(error);
            }
        }

        function displayWeight(data) {
            const btn = document.getElementById('getWeightBtn');
            btn.disabled = false;
            btn.innerHTML = '🔄 Get Weight';
            
            const contentDiv = document.getElementById('content');
            
            if (data.status === 'success') {
                updateStatus('success', 'Data received');
                
                const date = new Date(data.timestamp);
                const dateStr = date.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                });
                const timeStr = date.toLocaleTimeString('en-US', { 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit'
                });
                
                contentDiv.innerHTML = `
                    <div class="weight-card">
                        <div class="weight-label">Current Weight</div>
                        <div class="weight-value">
                            ${data.weight}
                            <span class="weight-unit">kg</span>
                        </div>
                        <div class="machine-badge">Machine ${data.machine_id}</div>
                    </div>
                    
                    <div class="timestamp-card">
                        <div class="timestamp-label">Last Updated</div>
                        <div class="timestamp-value">${dateStr}</div>
                        <div class="timestamp-value">${timeStr}</div>
                    </div>
                `;
                
                resetCountdown();
            } else if (data.status === 'no_data') {
                updateStatus('waiting', 'Waiting for data');
                
                contentDiv.innerHTML = `
                    <div class="no-data">
                        <div class="no-data-icon">📭</div>
                        <p><strong>No data for Machine ${selectedMachine}</strong></p>
                        <p style="margin-top: 8px; font-size: 13px;">
                            ${data.message}
                        </p>
                    </div>
                `;
            } else {
                handleError(data);
            }
        }

        function handleError(error) {
            const btn = document.getElementById('getWeightBtn');
            btn.disabled = false;
            btn.innerHTML = '🔄 Get Weight';
            
            updateStatus('error', 'Error occurred');
            
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = `
                <div class="no-data">
                    <div class="no-data-icon">⚠️</div>
                    <p><strong>Error loading data</strong></p>
                    <p style="margin-top: 8px; font-size: 13px;">
                        ${error.message || 'Unknown error'}
                    </p>
                </div>
            `;
        }

        function updateStatus(type, text) {
            const dot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            dot.className = 'status-dot';
            if (type === 'success') dot.classList.add('success');
            else if (type === 'waiting') dot.classList.add('waiting');
            else if (type === 'error') dot.classList.add('error');
            
            statusText.textContent = text;
        }

        function toggleAuto() {
            autoRefresh = !autoRefresh;
            const btn = document.getElementById('autoBtn');
            
            if (autoRefresh) {
                btn.textContent = 'Auto: ON';
                btn.classList.add('active');
                startAutoRefresh();
            } else {
                btn.textContent = 'Auto: OFF';
                btn.classList.remove('active');
                stopAutoRefresh();
            }
        }

        function startAutoRefresh() {
            countdown = 5;
            updateAutoInfo();
            
            autoInterval = setInterval(() => {
                getWeight();
            }, 5000);
            
            countdownInterval = setInterval(() => {
                countdown--;
                if (countdown <= 0) countdown = 5;
                updateAutoInfo();
            }, 1000);
        }

        function stopAutoRefresh() {
            if (autoInterval) clearInterval(autoInterval);
            if (countdownInterval) clearInterval(countdownInterval);
            document.getElementById('autoInfo').textContent = '';
        }

        function resetCountdown() {
            if (autoRefresh) {
                countdown = 5;
                updateAutoInfo();
            }
        }

        function updateAutoInfo() {
            if (autoRefresh) {
                document.getElementById('autoInfo').textContent = 
                    `Next refresh in ${countdown} seconds...`;
            }
        }

        window.onload = function() {
            getWeight();
        };
    </script>
</body>
</html>
"""

# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the main web page."""
    return HTML_TEMPLATE

@app.route('/api/weight/<machine_id>')
def get_weight(machine_id):
    """API endpoint to get latest weight for a specific machine."""
    data = load_weight_data(machine_id)
    
    if data:
        return jsonify({
            'status': 'success',
            'machine_id': machine_id,
            'weight': data['weight'],
            'timestamp': data['timestamp']
        })
    
    return jsonify({
        'status': 'no_data',
        'message': f'No weight data available for Machine {machine_id}'
    })

@app.route('/api/update/<machine_id>', methods=['POST'])
def update_weight(machine_id):
    """API endpoint to receive weight updates for a specific machine."""
    try:
        data = request.get_json()
        
        if not data or 'weight' not in data:
            return jsonify({
                'status': 'error',
                'message': 'No weight data provided'
            }), 400
        
        weight = float(data['weight'])
        
        if save_weight_data(machine_id, weight):
            return jsonify({
                'status': 'success',
                'message': f'Weight updated for Machine {machine_id}',
                'machine_id': machine_id,
                'weight': weight,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save weight data'
            }), 500
            
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid weight format'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/machines')
def list_machines():
    """API endpoint to list all machines with data."""
    machines = get_all_machines()
    return jsonify({
        'status': 'success',
        'machines': machines,
        'count': len(machines)
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    machines = get_all_machines()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'machines_count': len(machines)
    })

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
