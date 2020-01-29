# Photo-Sorter

This is a personal project for un-nesting photos, and sorting them into folders by-date based on their EXIF tag data.

## Usage

```python

# photo-sorter takes 2 arguments:
# path - file path to the directory you want to sort
# threshold - the minimum number of photos taken on the same day that warrants the creation of a new folder (default, 3)

py photo-sorter.py 'C:\photos', 2
```