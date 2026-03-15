#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_conda() {
    print_info "Checking if Conda is installed..."
    if ! command -v conda &> /dev/null; then
        print_error "Conda is not installed! Please install Miniconda or Anaconda first."
        print_info "Install command: brew install --cask miniconda"
        exit 1
    fi
    print_success "Conda is installed"
}

init_conda() {
    if [ -f "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" ]; then
        source "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh"
    elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    fi
}

setup_environment() {
    local ENV_NAME="automation-test"
    
    print_info "Checking conda environment..."
    
    if conda env list | grep -q "^${ENV_NAME} "; then
        print_warning "Environment '${ENV_NAME}' already exists"
        read -p "Update environment? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Updating conda environment..."
            conda env update -f environment.yml --prune
        fi
    else
        print_info "Creating new conda environment: ${ENV_NAME}"
        conda env create -f environment.yml
    fi
    
    print_success "Conda environment setup complete"
}

install_playwright_browsers() {
    print_info "Installing Playwright browsers..."
    conda activate automation-test
    playwright install chromium
    print_success "Playwright browsers installed"
}

setup_env_file() {
    local ENV_FILE="src/.env"
    
    if [ ! -f "$ENV_FILE" ]; then
        print_info "Creating .env file..."
        cat > "$ENV_FILE" << EOF
BASE_URL=https://dev.mrsplitter.com
API_BASE_URL=https://dev.mrsplitter.com/api
AUTH_TOKEN=
HEADLESS=true
SLOW_MO=0
BROWSER=chromium
EOF
        print_success ".env file created. Please edit src/.env to add required settings"
    else
        print_info ".env file exists, skipping"
    fi
}

show_usage() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}Setup Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "Usage:"
    echo ""
    echo "  1. Activate environment:"
    echo -e "     ${YELLOW}conda activate automation-test${NC}"
    echo ""
    echo "  2. Run all tests:"
    echo -e "     ${YELLOW}cd src && pytest${NC}"
    echo ""
    echo "  3. Run specific test types:"
    echo -e "     ${YELLOW}pytest -m smoke${NC}         # Smoke tests"
    echo -e "     ${YELLOW}pytest -m auth${NC}          # Auth tests"
    echo -e "     ${YELLOW}pytest -m groups${NC}        # Group tests"
    echo -e "     ${YELLOW}pytest -m transactions${NC}  # Transaction tests"
    echo -e "     ${YELLOW}pytest -m profile${NC}       # Profile tests"
    echo ""
    echo "  4. Run tests with Allure report:"
    echo -e "     ${YELLOW}pytest --alluredir=allure-results${NC}"
    echo -e "     ${YELLOW}allure serve allure-results${NC}"
    echo ""
    echo "  5. Run with headed mode (visible browser):"
    echo -e "     ${YELLOW}HEADLESS=false pytest${NC}"
    echo ""
    echo "=========================================="
}

main() {
    echo ""
    echo "=========================================="
    echo "  Automation Test Project - Setup"
    echo "=========================================="
    echo ""
    
    cd "$(dirname "$0")"
    
    init_conda
    check_conda
    setup_environment
    install_playwright_browsers
    setup_env_file
    show_usage
}

main
