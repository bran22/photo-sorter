from pathlib import Path
from datetime import datetime
from operator import itemgetter
import click
import time
from photo_sorter.exif_utils import get_exif_date_taken
from photo_sorter.directory_utils import unnest_directory

def getPhotosAndDates(sourcePath: Path):
  photoList = []
  uniqueDates = []
  skippedPhotos = []
  # loop through all photos
  for pathName in sourcePath.iterdir():
    # if file, add pathname and date to to the dictionary list
    if pathName.is_file():
      photoDate = get_exif_date_taken(pathName)
      # print(f'path: {pathName}')
      if photoDate is not None:
        # don't add to the photo list if exif photo taken data is missing
        photoList.append({
          'path': pathName,
          'date': photoDate
        })
        # add date to list of unique dates, only if it doesn't already exist
        photoDateOnly = datetime.date(photoDate)
        # if not uniqueDates:
        #   uniqueDates.append(photoDateOnly)
        if photoDateOnly not in uniqueDates:
          uniqueDates.append(photoDateOnly)
      else:
        skippedPhotos.append(str(pathName.resolve()))
  # sort by date ascending
  sortedPhotoList = sorted(photoList, key=lambda photo: photo['date'])
  sortedUniqueDates = sorted(uniqueDates)
  return sortedPhotoList, sortedUniqueDates, skippedPhotos



def folderizeByDate(photos, dates, threshold, destinationPath):
  daysCreated = 0 # counter of folders created to sort photos into it
  daysSkipped = [] # list of specific days skipped due to threshold
  photosSorted = 0

  # for each unique date, get the list of photos that were taken on that date
  for date in dates:
    photosTakenOnDate = list(filter(lambda photo: datetime.date(photo['date']) == date, photos))
    # print(photosTakenOnDate)
    # if the number of photos taken on that date is greater than a threshold, make a folder with that date name
    if len(photosTakenOnDate) >= threshold:
      dateAsString = date.strftime('%Y-%m-%d')
      newFolder = destinationPath / dateAsString
      newFolder.mkdir(parents=False, exist_ok=False)
      daysCreated += 1
      # move photos with matching date into that folder
      for photo in photosTakenOnDate:
        destination = photo['path'].parent / dateAsString / photo['path'].name
        photo['path'].rename(destination)
        photosSorted += 1
    else:
      daysSkipped.append(str(date))
  return daysCreated, photosSorted, daysSkipped,

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
def main(path, threshold):
  """
  Sorts photos from the specified directory PATH into date-named subdirectories based on the Date Taken EXIF tag embedded in the photos.
  """
  print('---begin photo sorting---')
  startTime = time.process_time()
  if not path.is_dir():
    print('file path does not exist, quitting...')
    quit()
  counters = unnest_directory(path)
  moved_files, deleted_folders, failed_moves, failed_deletes = itemgetter('moved', 'deleted', 'failed_move', 'failed_delete')(counters)
  print(f'{moved_files} files un-nested, {deleted_folders} empty folders deleted')
  print(f'{failed_moves} files could not be moved, so {failed_deletes} folders were left unempty')
  print('indexing photos...')
  photos, dates, skippedFiles = getPhotosAndDates(path)
  print(f'{len(photos)} photos found, taken on {len(dates)} different days')
  created, moved, skippedDays = folderizeByDate(photos, dates, threshold, path)
  print(f'{moved} photos sorted into {created} folders')
  print('issues:')
  print(f'- skipped the following days due to having fewer photos than threshold of {threshold}:\n{skippedDays}')
  print(f'- skipped the following files due to missing or bad date format:\n{skippedFiles}')
  endTime = time.process_time()
  print(f'process took {endTime - startTime} seconds')
  print('---end photo sorting---')

if __name__ == "__main__":
  main()
