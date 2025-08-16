#!/bin/bash
SITE=${1:-dev3.laksystem.xyz}
CYAN="\033[0;36m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
echo -e "${CYAN}Installing fiveg_wifi_planner on ${SITE}...${NC}"

if bench --site $SITE list-apps | grep -q fiveg_wifi_planner; then
    echo -e "${YELLOW}⚠ App already installed on ${SITE} — continuing${NC}"
else
    bench --site $SITE install-app fiveg_wifi_planner || { echo -e "${RED}✘ install-app failed${NC}"; exit 1; }
fi

echo -e "${CYAN}Running migrate & cache...${NC}"
bench --site $SITE migrate || true
bench --site $SITE clear-cache || true
bench restart || true

echo -e "${GREEN}✓ Done. Open Desk → Workspace: Fiveg Wifi Planner. Check Number Cards & Reports.${NC}"