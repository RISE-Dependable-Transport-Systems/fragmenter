#!/bin/bash
set -e  # Exit on any error

#
# Steady State Hypothesis
#

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <experiment_id>"
  exit 1
fi

EXPERIMENT_ID="$1"

PROJECT_ROOT_DIR="$(pwd)"
EXP_DIR="$PROJECT_ROOT_DIR/examples/waywise/experiments"
SOURCE_CODE_DIR="$EXP_DIR/../data/code/precise-truck"
TARGET_CODE_DIR="$EXP_DIR/src/precise-truck"
CONTROLTOWER_DIR="$EXP_DIR/visualization/ControlTower"
LOGS_DIR="$EXP_DIR/../sce_db/logs"

RUN_LOGS_DIR="$LOGS_DIR/$EXPERIMENT_ID"
RCTRUCK_CONSOLE_LOG="$RUN_LOGS_DIR/steady-state_rctruck_console.log"
RCTRUCK_APP_LOG="$RUN_LOGS_DIR/steady-state_rctruck.log"

echo "==> Preparing experiment directories"
mkdir -p "$EXP_DIR/src"
mkdir -p "$RUN_LOGS_DIR"

echo "==> Experiment ID : $EXPERIMENT_ID"
echo "==> Logs directory: $RUN_LOGS_DIR"

#
# Copy precise-truck into ./src (overwrite if exists)
#
if [ -d "$TARGET_CODE_DIR" ]; then
  echo "==> Removing existing precise-truck in src/"
  rm -rf "$TARGET_CODE_DIR"
fi

echo "==> Copying precise-truck from $SOURCE_CODE_DIR to $TARGET_CODE_DIR"
cp -r "$SOURCE_CODE_DIR" "$TARGET_CODE_DIR"

#
# Build RCTruck
#
cd "$TARGET_CODE_DIR"

echo "==> Building precise-truck (RCTruck)"
mkdir -p build
cd build
cmake ..
make -j

#
# Build ControlTower
#
if [ ! -x "$CONTROLTOWER_DIR/build/ControlTower" ]; then
  echo "==> ControlTower binary not found, building"

  cd "$CONTROLTOWER_DIR"
  mkdir -p build
  cd build
  cmake ..
  make -j
else
  echo "==> ControlTower already built, skipping build"
fi

#
# Run both applications
#
echo "==> Running ControlTower and RCTruck"

# Run ControlTower
cd "$CONTROLTOWER_DIR/build"
./ControlTower &
CONTROLTOWER_PID=$!

# Run RCTruck
cd "$TARGET_CODE_DIR/build"
./RCTruck --config ../config/truck1.json \
  > "$RCTRUCK_CONSOLE_LOG" 2>&1 &
TRUCK_PID=$!

# Let them run for 25 seconds
sleep 25

#
# Shutdown
#
echo "==> Stopping applications"

kill "$CONTROLTOWER_PID" 2>/dev/null || true
kill "$TRUCK_PID" 2>/dev/null || true
sleep 1
kill -9 "$CONTROLTOWER_PID" 2>/dev/null || true
kill -9 "$TRUCK_PID" 2>/dev/null || true

#
# Collect and move logs
#
echo "==> Collecting logs"

RCTRUCK_LOG=$(find "$TARGET_CODE_DIR/log" -name "Log *.log" -type f -printf '%T@ %p\n' \
  | sort -rn | head -1 | cut -d' ' -f2-)

if [ -n "$RCTRUCK_LOG" ]; then
    mv "$RCTRUCK_LOG" "$RCTRUCK_APP_LOG"
    echo "Moved RCTruck log to $RCTRUCK_APP_LOG"
fi

echo "✔ Steady-state experiment completed successfully"
exit 0
