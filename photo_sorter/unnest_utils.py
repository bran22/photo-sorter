from pathlib import Path

def move_file_up_one_level(file: Path) -> bool:
  """Returns True if moving the specified file up one level was successful"""
  destination = file.parents[1] / file.name
  try:
    file.rename(destination)
    return True
  except:
    return False

def is_directory_empty(directory: Path) -> bool:
  """Returns True if specified directory is empty"""
  has_contents = next(directory.iterdir(), None)
  return has_contents is None

def update_counters(counter: dict[str, int], new_counts: dict[str, int]) -> dict[str, int]:
  """Updates COUNTER based on counts from matching keys contained in NEW_DATA"""
  for (name, count) in new_counts.items():
    counter[name] += count
  return counter

def unnest_directory(source_path: Path) -> dict[str, int]:
  """Recursively un-nests all files in SOURCE_PATH """
  counter = {
    'moved': 0,
    'deleted': 0,
    'failed_move': 0,
    'failed_delete': 0
  }
  # loop through everything in the source directory
  for path in source_path.iterdir():
    if path.is_dir():
      new_counts = unnest_directory(path)  # recurse!
      counter = update_counters(counter, new_counts)
      for file in path.iterdir():
        is_successful = move_file_up_one_level(file)
        if is_successful:
          counter['moved'] += 1
        else:
          counter['failed_move'] += 1
      # delete empty directories
      if is_directory_empty(path):
        path.rmdir()
        counter['deleted'] += 1
      else:
        counter['failed_delete'] += 1
  return counter
