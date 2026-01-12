#!/bin/bash

# LaTeX Agent - Production Setup Script
# This script helps set up environment files for production deployment

set -e

echo "🚀 LaTeX Agent - Production Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env files exist
echo "📋 Checking environment files..."

if [ -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  backend/.env already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping backend/.env"
    else
        cp backend/.env.example backend/.env
        echo -e "${GREEN}✅ Created backend/.env from template${NC}"
    fi
else
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✅ Created backend/.env from template${NC}"
fi

if [ -f "frontend/.env.local" ]; then
    echo -e "${YELLOW}⚠️  frontend/.env.local already exists${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping frontend/.env.local"
    else
        cp frontend/.env.local.example frontend/.env.local
        echo -e "${GREEN}✅ Created frontend/.env.local from template${NC}"
    fi
else
    cp frontend/.env.local.example frontend/.env.local
    echo -e "${GREEN}✅ Created frontend/.env.local from template${NC}"
fi

echo ""
echo "🔑 Generating secure JWT secret..."
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
echo "Generated: $JWT_SECRET"
echo ""

echo "📝 Next steps:"
echo "1. Edit backend/.env and update:"
echo "   - GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3"
echo "   - GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET"
echo "   - GITHUB_CALLBACK_URL (your production domain)"
echo "   - JWT_SECRET (use the generated one above: $JWT_SECRET)"
echo ""
echo "2. Edit frontend/.env.local and update:"
echo "   - NEXT_PUBLIC_API_URL (your backend URL)"
echo "   - NEXT_PUBLIC_APP_URL (your frontend URL)"
echo "   - NEXT_PUBLIC_GITHUB_CLIENT_ID"
echo ""
echo "3. Update GitHub OAuth App settings:"
echo "   - Go to: https://github.com/settings/developers"
echo "   - Update Homepage URL to your production domain"
echo "   - Update Authorization callback URL"
echo ""
echo "4. Test locally:"
echo "   docker-compose up --build"
echo ""
echo "5. Deploy to your hosting platform (Railway recommended)"
echo ""
echo -e "${GREEN}Setup complete! Review the DEPLOYMENT_GUIDE.md for detailed instructions.${NC}"
