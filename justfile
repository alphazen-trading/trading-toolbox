set dotenv-load

default:
	just --list --unsorted

# ============================================= #
# Dev Section
# ============================================= #
install:
  #!/usr/bin/env bash
  rye sync
  rye run pre-commit install --hook-type pre-push --hook-type commit-msg
  if [ ! -d "/opt/logs" ]; then
    sudo mkdir /opt/logs
  fi
  sudo chown -R $USER:$USER /opt/logs

cz:
  rye run cz commit --write-message-to-file /tmp/msg

czr:
  rye run cz commit --write-message-to-file /tmp/msg --retry

cleanup:
  rm -f /tmp/msg

local_docker:
  #!/usr/bin/env bash
  docker stop $(docker ps -aq)
  sudo chown -R 472:472 ./docker/grafana_data
  sudo chown -R 472:472 ./docker/provisioning
  docker compose --env-file .env -f docker/docker-compose.yml up 


pub:
  #!/usr/bin/env bash
  rye version -b minor
  rye build --clean
  rye build --all --out target 
  git add .
  git commit -m "build: automatic rye bump of project version"
  git push
  rye publish --yes
  just pub-docs

pub-docs:
  rye run mike deploy --update-aliases $(rye version) latest
  rye run mike set-default --push latest

# ============================================= #
# Code Section
# ============================================= #
pre-commit-test:
  rye run pre-commit run

dev:
  nodemon -e py --exec rye run dev

rs_dev:
  #!/usr/bin/env bash
  cd rs
  nodemon -w rs -e rs --exec maturin develop --skip-install -r --uv

# ============================================= #
# Docs
# ============================================= #
docs:
  rye run mike serve

docs-build:
  rye run mkdocs build


# ============================================= #
# Custom Section
# ============================================= #
custom:
  echo "Do whatever you want here"
