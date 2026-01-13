#!/bin/bash
set -e

echo "=============================================="
echo "Setting up CANOPI Dev Container with Claude Code"
echo "=============================================="

# Install bubblewrap for sandboxing
echo ""
echo "[1/6] Installing bubblewrap for OS-level sandboxing..."
sudo apt-get update -qq
sudo apt-get install -y -qq bubblewrap curl

# Install Claude Code CLI
echo ""
echo "[2/6] Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

# Set up Claude Code settings with sandboxing enabled
echo ""
echo "[3/6] Configuring Claude Code with sandboxing..."
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "network": {
      "allowLocalBinding": true
    }
  },
  "permissions": {
    "allow": [
      "Bash(cd:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Bash(wc:*)",
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(pip:*)",
      "Bash(pip3:*)",
      "Bash(node:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(git:*)",
      "Bash(curl:*)",
      "Bash(wget:*)",
      "Bash(docker:*)",
      "Bash(docker-compose:*)",
      "Bash(uvicorn:*)",
      "Bash(pytest:*)",
      "Bash(make:*)",
      "Bash(mkdir:*)",
      "Bash(rm:*)",
      "Bash(cp:*)",
      "Bash(mv:*)",
      "Bash(touch:*)",
      "Bash(chmod:*)",
      "Bash(echo:*)",
      "Bash(source:*)",
      "Bash(./backend/venv/bin/python:*)",
      "Bash(./backend/venv/bin/pip:*)"
    ]
  }
}
EOF

# Set up backend Python environment
echo ""
echo "[4/6] Setting up backend Python environment..."
cd /workspaces/canopi
if [ -d "backend" ]; then
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip -q
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
  fi
  # Install common packages
  pip install fastapi uvicorn pydantic requests numpy gurobipy networkx pyshp -q
  cd ..
fi

# Set up frontend
echo ""
echo "[5/6] Setting up frontend..."
if [ -d "frontend" ]; then
  cd frontend
  npm install --silent
  cd ..
fi

# Copy Gurobi license if it exists on Windows side
echo ""
echo "[6/6] Checking for Gurobi license..."
if [ -f "/workspaces/canopi/gurobi.lic" ]; then
  echo "  Found gurobi.lic in project root"
elif [ -n "$GRB_LICENSE_FILE" ]; then
  echo "  GRB_LICENSE_FILE is set to: $GRB_LICENSE_FILE"
else
  echo "  Note: Copy your gurobi.lic to project root for Gurobi optimization"
fi

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Claude Code is installed with OS-level sandboxing enabled."
echo ""
echo "To start Claude Code, run:"
echo "  claude"
echo ""
echo "To start the backend:"
echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8002"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm start"
echo ""
echo "Sandboxing is ENABLED - commands run in isolated environment."
echo "=============================================="
