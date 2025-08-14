
# Solkit

Solfacil Python Package with Resusable Code.

## Installation

### With `pip`

```bash
# from branch
pip install git+https://git@github.com/solfacil/ccoe.sup.solkit.git#main

# from release

# with extras
```

### With `Poetry`

```bash
# from branch
poetry add 'solkit@git+https://git@github.com/solfacil/ccoe.sup.solkit.git#main'

# from release

# with extras
```

> [!IMPORTANT]
> Avaliable paackge extras:
> `cache`, `broker`, `all`

## Development

### Setup

```bash
# update package manager
pip install --upgrade pip wheels virtualenv

# create witrualenv
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
