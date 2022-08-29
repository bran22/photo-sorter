from datetime import datetime
from pathlib import Path
from typing import Union
import exifread

def print_exif_data(img_path: Path) -> None:
  """Print out EXIF tags from an image"""
  unreadable_tags = ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote')
  # reads out all the non-gigantic tags so you know what those keys will be called
  img = open(img_path, 'rb')
  tags = exifread.process_file(img)
  for tag in tags.keys():
    if tag not in unreadable_tags:
      print(f'Key: {tag}, Value: {tags[tag]}')

def get_exif_date_taken(img_path: Path) -> Union[datetime, None]:
  """Return the EXIF DateTimeOriginal tag from an image as datetime.  Returns None if the tag is missing or malformed"""
  img = open(img_path, 'rb')
  tags = exifread.process_file(img)
  # need to cast tag data to string, since it's a funky format
  date_taken = str(tags.get('EXIF DateTimeOriginal'))
  try:
    return datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
  except:
    return None # if exif tag data is missing, don't return a date
