#!/bin/bash
set -e  # Exit on any error

#
# Arguments
#
if [ "$#" -lt 2 ]; then
    echo "Error: experiment_id and at least one patch_id required"
    echo "Usage: $0 <experiment_id> <patch_id_1> [patch_id_2 ...]"
    exit 1
fi

EXPERIMENT_ID="$1"
shift
PATCH_IDS=("$@")

PROJECT_ROOT_DIR="$(pwd)"
EXP_DIR="$PROJECT_ROOT_DIR/examples/waywise/experiments"
SOURCE_CODE_DIR="$EXP_DIR/../data/code/precise-truck"
TARGET_CODE_DIR="$EXP_DIR/src/precise-truck"
CONTROLTOWER_DIR="$EXP_DIR/visualization/ControlTower"
SCE_DB_DIR="$EXP_DIR/../sce_db"
LOGS_DIR="$EXP_DIR/../sce_db/logs"

RUN_LOGS_DIR="$LOGS_DIR/$EXPERIMENT_ID"

RCTRUCK_CONSOLE_LOG="$RUN_LOGS_DIR/${EXPERIMENT_ID}_rctruck_console.log"
RCTRUCK_APP_LOG="$RUN_LOGS_DIR/${EXPERIMENT_ID}_rctruck.log"

mkdir -p "$RUN_LOGS_DIR"

echo "==> Experiment ID : $EXPERIMENT_ID"
echo "==> Patch IDs     : ${PATCH_IDS[*]}"
echo "==> Run logs dir  : $RUN_LOGS_DIR"

#
# Prepare source directory
#
echo "==> Preparing source directory"
mkdir -p "$EXP_DIR/src"

if [ -d "$TARGET_CODE_DIR" ]; then
  echo "==> Removing existing precise-truck"
  rm -rf "$TARGET_CODE_DIR"
fi

cp -r "$SOURCE_CODE_DIR" "$TARGET_CODE_DIR"

#
# Apply all patches BEFORE build
#
cd "$TARGET_CODE_DIR"

for PATCH_ID in "${PATCH_IDS[@]}"; do
  PATCH_FILE="$SCE_DB_DIR/patches/${PATCH_ID}.patch"

  if [ ! -f "$PATCH_FILE" ]; then
    echo "Error: Patch file not found: $PATCH_FILE"
    exit 1
  fi

  echo "==> Applying patch: $PATCH_ID"
  git apply "$PATCH_FILE"
done

#
# Build precise-truck (once)
#
mkdir -p build
cd build
cmake ..
make -j

#
# Run both applications
#
echo "==> Running ControlTower and RCTruck"

cd "$CONTROLTOWER_DIR/build"
./ControlTower &
CONTROLTOWER_PID=$!

cd "$TARGET_CODE_DIR/build"
./RCTruck --config ../config/truck1.json \
  > "$RCTRUCK_CONSOLE_LOG" 2>&1 &
TRUCK_PID=$!

sleep 25

#
# Shutdown
#
echo "==> Stopping applications"

kill "$CONTROLTOWER_PID" "$TRUCK_PID" 2>/dev/null || true
sleep 1
kill -9 "$CONTROLTOWER_PID" "$TRUCK_PID" 2>/dev/null || true
sleep 1

#
# Collect and move exploit log
#
RCTRUCK_LOG=$(find "$TARGET_CODE_DIR/log" -name "Log *.log" -type f -printf '%T@ %p\n' \
  | sort -rn | head -1 | cut -d' ' -f2-)

if [ -n "$RCTRUCK_LOG" ]; then
    mv "$RCTRUCK_LOG" "$RCTRUCK_APP_LOG"
    echo "Moved RCTruck exploit log to $RCTRUCK_APP_LOG"
fi

echo "✔ Experiment ${EXPERIMENT_ID} completed successfully"
exit 0
