#!/bin/bash

# Auto Applyer Frontend Test Runner
# This script runs all Playwright tests with different configurations

echo "🚀 Starting Auto Applyer Frontend Tests..."

# Check if frontend is running
echo "📋 Checking if frontend is running on localhost:3000..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend not detected on localhost:3000"
    echo "💡 Make sure to run 'npm run dev' in another terminal"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run basic tests
echo "🧪 Running basic tests..."
npm run test

# Run tests with UI (if available)
echo "🎨 Running tests with UI..."
npm run test:ui &

# Run tests in headed mode for debugging
echo "🔍 Running tests in headed mode..."
npm run test:headed

# Generate test report
echo "📊 Generating test report..."
npm run test:report

echo "✅ All tests completed!"
echo "📁 Test reports available in:"
echo "   - HTML Report: playwright-report/index.html"
echo "   - Test Results: .test-results/" 