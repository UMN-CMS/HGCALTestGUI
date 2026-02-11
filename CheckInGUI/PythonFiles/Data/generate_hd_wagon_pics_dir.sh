#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="./boards"

# board_id  name       modules
BOARDS=(
  "WH21A Avocado 3"
  "WH30A Pineapple 3"
  "WH30B Banana 3"
  "WH30C Pumpkin 3"
  "WH30D Donut 3"
  "WH31A Apple 4"
  "WH31B Cherry 4"
)

for entry in "${BOARDS[@]}"; do
  read -r ID NAME MODULES <<< "$entry"

  for TYPE in T D; do
    BOARD_KEY="$(echo "$ID$TYPE" | tr '[:upper:]' '[:lower:]')"
    BOARD_DIR="$BASE_DIR/$BOARD_KEY"
    ECONS_DIR="$BOARD_DIR/econs"

    echo "Creating $BOARD_DIR ($NAME $TYPE)"

    mkdir -p "$ECONS_DIR"

    # board image
    #touch "$BOARD_DIR/$BOARD_KEY.png"

    ## ECOND modules (always present)
    #for ((i=1; i<=MODULES; i++)); do
    #  touch "$ECONS_DIR/econdm$i.png"
    #done

    ## ECONT modules (T only)
    #if [[ "$TYPE" == "T" ]]; then
    #  for ((i=1; i<=MODULES; i++)); do
    #    touch "$ECONS_DIR/econtm$i.png"
    #  done
    #fi
  done
done

echo "Filesystem layout generation complete"

