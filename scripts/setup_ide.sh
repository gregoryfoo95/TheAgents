#!/bin/bash

echo "Setting up IDE IntelliSense for Property Marketplace..."

# Backend Python setup
echo "Setting up Python environment..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Add development dependencies for better IntelliSense
pip install mypy pylint flake8 black isort

echo "Python setup complete!"

# Frontend TypeScript setup
echo "Setting up TypeScript environment..."
cd ../frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

# Install additional type definitions
npm install --save-dev @types/node @types/react @types/react-dom

echo "TypeScript setup complete!"

echo ""
echo "IDE Setup Complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Open your IDE in the project root: /home/gregoryfoo95/dev/TheAgents"
echo "2. For VS Code: Install recommended extensions when prompted"
echo "3. For Python: Select interpreter at ./backend/venv/bin/python"
echo "4. For TypeScript: Ensure TypeScript language service is enabled"
echo ""
echo "To activate Python environment manually:"
echo "  cd backend && source venv/bin/activate"
echo ""
echo "To run type checking:"
echo "  Backend: cd backend && mypy ."
echo "  Frontend: cd frontend && npx tsc --noEmit"