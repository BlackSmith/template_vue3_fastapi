#!/usr/bin/env bash
set -e

# VSCode appearance
git config --replace-all devcontainers-theme.show-dirty 1

# Aliasy
echo "alias ll='ls -la'" >> ~/.bashrc
echo -e "pip() { \n pushd /workspace/backend/ > /dev/null && pdm run pip \"\$@\" && popd > /dev/null \n}" >> ~/.bashrc
echo -e "python() { \n pushd /workspace/backend/ > /dev/null && pdm run python \"\$@\" && popd > /dev/null \n}" >> ~/.bashrc

# Docker group
sudo groupadd -g 975 -f docker
sudo usermod -aG docker vscode

# PDM konfigurace a instalace
cd ./backend
pdm install -G:all