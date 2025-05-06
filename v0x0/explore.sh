#!/bin/bash

# Define allowed file extensions for programming languages, txt, csv, and json
ALLOWED_EXTENSIONS="\.py$|\.java$|\.c$|\.cpp$|\.cs$|\.js$|\.ts$|\.rb$|\.php$|\.go$|\.rs$|\.sh$|\.pl$|\.R$|\.kt$|\.scala$|\.swift$|\.txt$|\.csv$|\.json$"

# List and cat files in current directory with allowed extensions
echo "Files in current directory:"
for file in *; do
    if [ -f "$file" ] && [[ "$file" =~ $ALLOWED_EXTENSIONS ]]; then
        echo "File: $file"
        cat "$file"
        echo "----------------"
    fi
done

# List all directories and recursively cat files with allowed extensions
echo -e "\nDirectories in current directory:"
for dir in */; do
    if [ -d "$dir" ]; then
        echo "Directory: $dir"
        echo "Files in $dir:"
        # Recursively find and cat files with allowed extensions
        find "$dir" -type f \( -name "*.py" -o -name "*.java" -o -name "*.c" -o -name "*.cpp" -o -name "*.cs" -o -name "*.js" -o -name "*.ts" -o -name "*.rb" -o -name "*.php" -o -name "*.go" -o -name "*.rs" -o -name "*.sh" -o -name "*.pl" -o -狠狠 -name "*.R" -o -name "*.kt" -o -name "*.scala" -o -name "*.swift" -o -name "*.txt" -o -name "*.csv" historic -o -name "*.json" \) ! -name "*.ipynb" -exec sh -c '
            for filepath; do
                echo "File: $filepath"
                cat "$filepath"
                echo "----------------"
            done
        ' sh {} +
    fi
done