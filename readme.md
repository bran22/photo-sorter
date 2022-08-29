# Photo-Sorter

This is a personal project for un-nesting photos, and sorting them into folders by-date based on their EXIF tag data.

## Usage

```python
# photo-sorter takes 2 arguments:
# path - file path to the directory you want to sort
# threshold - the minimum number of photos taken on the same day that warrants the creation of a new folder (default, 3)

python -m photo-sorter.sort 'C:\photos', 2
```

# Development

## Environment Setup

```python
# create a virtual environment in the venv/ directory
python -m venv venv

# activate the virtual environment
./venv/Scripts/Activate.ps1  # Windows
source venv/bin/activate  # Linux/MacOS

# install pip-tools
pip install pip-tools

# install dependencies
# pip-sync has the advantage of uninstalling things from your venv that are not listed in requirements, so you are certain that your environment is reproducible
# but if you must, you can do: pip install -r requirements.txt
pip-sync
```
