from pathlib import Path
from operator import itemgetter
import click
import time
from photo_sorter.file_utils import get_photos_and_dates, folderize_by_date
from photo_sorter.unnest_utils import unnest_directory

@click.command()
@click.argument(
  'path',
  type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path)
)
@click.option(
  '--threshold',
  type=int,
  default=3,
  help='Minimum number of photos (taken on the same day) that warrants the creation of a subdirectory.  Default is 3.'
)
def main(path: Path, threshold: int):
  """
  Sorts photos from the specified directory PATH into date-named subdirectories based on the Date Taken EXIF tag embedded in the photos.
  """
  print('---begin photo sorting---')
  start_time = time.process_time()
  counters = unnest_directory(path)
  moved_files, deleted_folders, failed_moves, failed_deletes = itemgetter('moved', 'deleted', 'failed_move', 'failed_delete')(counters)
  print(f'{moved_files} files un-nested, {deleted_folders} empty folders deleted')
  print(f'{failed_moves} files could not be moved, so {failed_deletes} folders were left unempty')
  print('indexing photos...')
  photos_by_date, valid_files, skipped_files = get_photos_and_dates(path)
  print(f'{len(valid_files)} photos found, taken on {len(photos_by_date)} different days')
  created_dates, skipped_dates = folderize_by_date(photos_by_date, threshold, path)
  rename_count = sum([count for date, count in created_dates])
  print(f'moved {rename_count} photos into {len(created_dates)} folders')
  if len(skipped_dates) > 0:
    print(f'NOTE: skipped the following days due to having fewer photos than threshold of {threshold}:')
    for date, count in skipped_dates:
      print(f'  {date}, number of photos: {count}')
  if len(skipped_files) > 0:
    print(f'NOTE: skipped the following files due to missing or bad date format:')
    for file in skipped_files:
      print(f'  {str(file.resolve())}')
  end_time = time.process_time()
  print(f'process took {end_time - start_time} seconds')
  print('---end photo sorting---')

if __name__ == "__main__":
  main()
