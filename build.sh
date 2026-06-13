#!/usr/bin/env bash
set -e

ROOT_DIR="$(pwd)"
EXTERNAL_DIR="$ROOT_DIR/external"
ANTLR_JAR="antlr-4.13.2-complete.jar"
BUILD_DIR="$ROOT_DIR/build"
GRAMMAR_DIR="$ROOT_DIR/src/grammar"

mkdir -p "$BUILD_DIR"
cp "$GRAMMAR_DIR/lexererr.py" "$BUILD_DIR/lexererr.py"

echo -e "\033[33mCompiling ANTLR grammar files...\033[0m"
gfiles=( "$GRAMMAR_DIR"/*.g4 )
java -jar "$EXTERNAL_DIR/$ANTLR_JAR" \
    -Dlanguage=Python3 \
    -visitor \
    -no-listener \
    -o "$BUILD_DIR" \
    "${gfiles[@]}"

echo -e "\033[32mANTLR grammar files compiled to $BUILD_DIR\033[0m"
