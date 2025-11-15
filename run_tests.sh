#!/bin/bash
# Test runner script for Obsidian Auto-Linker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Obsidian Auto-Linker Test Suite${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}pytest is not installed. Installing test dependencies...${NC}"
    pip install -r requirements-test.txt
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    "all")
        echo -e "${GREEN}Running all tests with coverage...${NC}"
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
        ;;

    "unit")
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest tests/ -v -m "unit" --cov=. --cov-report=term-missing
        ;;

    "integration")
        echo -e "${GREEN}Running integration tests only...${NC}"
        pytest tests/ -v -m "integration" --cov=. --cov-report=term-missing
        ;;

    "fast")
        echo -e "${GREEN}Running fast tests (excluding slow)...${NC}"
        pytest tests/ -v -m "not slow" --cov=. --cov-report=term-missing
        ;;

    "slow")
        echo -e "${YELLOW}Running slow tests...${NC}"
        pytest tests/ -v -m "slow" --cov=. --cov-report=term-missing
        ;;

    "ai")
        echo -e "${GREEN}Running AI integration tests...${NC}"
        pytest tests/ -v -m "ai" --cov=. --cov-report=term-missing
        ;;

    "cache")
        echo -e "${GREEN}Running cache tests...${NC}"
        pytest tests/ -v -m "cache" --cov=. --cov-report=term-missing
        ;;

    "file")
        echo -e "${GREEN}Running file operation tests...${NC}"
        pytest tests/ -v -m "file_ops" --cov=. --cov-report=term-missing
        ;;

    "coverage")
        echo -e "${GREEN}Running tests and generating detailed coverage report...${NC}"
        pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=json
        echo ""
        echo -e "${BLUE}Coverage report generated in htmlcov/index.html${NC}"

        # Try to open coverage report
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open htmlcov/index.html
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open htmlcov/index.html 2>/dev/null || echo "Coverage report at: htmlcov/index.html"
        fi
        ;;

    "watch")
        echo -e "${YELLOW}Running tests in watch mode...${NC}"
        if command -v pytest-watch &> /dev/null; then
            pytest-watch tests/ -- -v --cov=. --cov-report=term-missing
        else
            echo -e "${RED}pytest-watch not installed. Install with: pip install pytest-watch${NC}"
            exit 1
        fi
        ;;

    "debug")
        echo -e "${YELLOW}Running tests with debugging enabled...${NC}"
        pytest tests/ -v --pdb -x
        ;;

    "specific")
        if [ -z "$2" ]; then
            echo -e "${RED}Please specify test file or pattern${NC}"
            echo "Usage: ./run_tests.sh specific tests/test_cache.py"
            exit 1
        fi
        echo -e "${GREEN}Running specific test: $2${NC}"
        pytest "$2" -v --cov=. --cov-report=term-missing
        ;;

    "help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  all          - Run all tests (default)"
        echo "  unit         - Run unit tests only"
        echo "  integration  - Run integration tests only"
        echo "  fast         - Run fast tests (exclude slow)"
        echo "  slow         - Run slow tests only"
        echo "  ai           - Run AI integration tests"
        echo "  cache        - Run cache tests"
        echo "  file         - Run file operation tests"
        echo "  coverage     - Generate detailed coverage report"
        echo "  watch        - Run tests in watch mode"
        echo "  debug        - Run tests with pdb debugger"
        echo "  specific     - Run specific test file"
        echo "  help         - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh all"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh coverage"
        echo "  ./run_tests.sh specific tests/test_cache.py"
        exit 0
        ;;

    *)
        echo -e "${RED}Unknown option: $TEST_TYPE${NC}"
        echo "Use './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Show test summary
echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}Test run completed!${NC}"
echo -e "${BLUE}=====================================${NC}"
