from pathlib import Path
from datetime import datetime
from photo_sorter.exif_utils import get_exif_date_taken

def is_path_a_file(path: Path) -> bool:
  """Returns True if path is a file"""
  return path.is_file()

def find_files_with_date(date: datetime, files: list[Path]) -> list[Path]:
  return [file for file in files if get_exif_date_taken(file).date() == date]

def move_files_to_folder(files: list[Path], destination: Path) -> int:
  """Move a list of filepaths to a destination path (using the same filename)"""
  for file in files:
    file.rename(destination / file.name)
  return len(files)

def get_photos_and_dates(directory: Path):
  """
  From all files in a flat directory, build a list of (date, list(Path)), one tuple per unique date.
  Inner list contains list of all files with the same date in its EXIF Date Taken tag
  """
  # filter for filepaths that are files (not directories)
  files = [file for file in directory.iterdir() if is_path_a_file(file)]

  # skip files that do not have a valid EXIF date
  skipped_files = [file for file in files if get_exif_date_taken(file) is None]
  valid_files = [file for file in files if get_exif_date_taken(file) is not None]

  # build list( (date, list(Path)) ), one outer list per unique date
  unique_dates = set([datetime.date(get_exif_date_taken(file)) for file in valid_files])
  photos_by_date = [ (date, find_files_with_date(date, valid_files)) for date in unique_dates]
  return photos_by_date, valid_files, skipped_files

def folderize_by_date(photos_by_date: list[tuple[datetime, list[Path]]], threshold: int, destination_path: Path) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
  """
  From a list of (date, list(Path)), create a new folder for each date and move all files in the matching list into that folder
  """
  folders_created = []
  dates_skipped = []

  for (date, photo_paths) in photos_by_date:
    if len(photo_paths) >= threshold:
      date_as_string = date.strftime('%Y-%m-%d')
      new_folder = destination_path / date_as_string
      new_folder.mkdir(parents=False, exist_ok=False)
      files_moved = move_files_to_folder(photo_paths, new_folder)
      folders_created.append((
        str(date),
        files_moved
      ))
    else:
      dates_skipped.append((
        str(date),
        len(photo_paths)
      ))

  return folders_created, dates_skipped
