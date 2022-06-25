# database-backup-aws
Automatic and adjustable backup of the database on AWS

## Requirements
```bash
# create virtual environment
python3.9 -m venv .venv

# active environment
source .venv/bin/activate

# install requirements
pip install -r requirements.txt
```

## Usage
```bash
python3 main.py --action backup --configfile sample.config
```