
# 🧰 Solkit

This package was developed to provide simple and fast dependencies instrumentation, 
as a handy SDK for the developer’s daily work.

## Installation

### CI/CD Requirements

Your image build must have access to SSH to authenticate with GitHub.

```dockerfile
# Dockerfile

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl git ssh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p -m 0600 ~/.ssh \
    && echo "Host *" >> ~/.ssh/config \
    && echo "   StrictHostKeyChecking no" >> ~/.ssh/config \
    && ssh-keyscan github.com >> ~/.ssh/known_hosts
```

> [!WARNING]
> Always use multi-stage docker when using the SSH Agent or remove it before the image build ends, it's a security breach

### With `pip`

```bash
# from branch
pip install git+https://git@github.com/solfacil/ccoe.sup.solkit.git@main

# from release

# with extras
pip install git+https://git@github.com/solfacil/ccoe.sup.solkit.git@main#egg=solkit[all]
```

### With `poetry`

```bash
# from branch
poetry add 'solkit@git+https://git@github.com/solfacil/ccoe.sup.solkit.git#main'

# from release

# with extras
poetry add 'solkit[all]@git+https://git@github.com/solfacil/ccoe.sup.solkit.git#main'
```

> [!IMPORTANT]
> Avaliable packge extras:
> `cache`, `broker`, `postgres`, `all`

## Uninstall

```bash
# pip
pip uninstall solkit

# poetry
poetry remove solkit
```

## Development

### Setup

```bash
# update package manager
pip install --upgrade pip wheels virtualenv

# create virtual environment
virtualenv .venv

# enable virtualenv
.venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements/development.txt
```

### Run tests

```bash
pytest tests
```
