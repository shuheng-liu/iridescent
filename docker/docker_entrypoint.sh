#!/bin/bash

RED="\033[0;31m"
GREEN="\033[0;32m"
RESET="\033[0m"

echo -e "${GREEN}Starting IRIS instance $IRIS_INSTANCE...${RESET}"
iris start "$IRIS_INSTANCE" || (
  echo -e "${RED}Failed to start IRIS instance $IRIS_INSTANCE{$RESET}"
  exit 1
)

echo -e "${GREEN}Entering iridescent shell...${RESET}"
iridescent \
  && echo -e "\n${GREEN}Exited iridescent shell successfully. Resuming bash.${RESET}" \
  || echo -e "\n${RED}Something crashed in iridescent shell${RESET}. Switching to bash."

echo -e "${GREEN}Use command \`iridescent\` to enter iridescent shell again${RESET}"

bash