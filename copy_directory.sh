#!/bin/bash

# Check if source and destination directories are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' does not exist"
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy contents recursively
cp -r "$SOURCE_DIR"/* "$DEST_DIR"

# Check if copy was successful
if [ $? -eq 0 ]; then
    echo "Contents successfully copied from $SOURCE_DIR to $DEST_DIR"
else
    echo "Error: Failed to copy contents"
    exit 1
fi