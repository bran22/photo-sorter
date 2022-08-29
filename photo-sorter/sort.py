from pathlib import Path
from datetime import datetime
import argparse
import exifread
import time

def unNestPhotos(sourcePath: Path):
  movedFileCount = 0
  deletedFolderCount = 0
  failedMoveCount = 0
  failedDeleteCount = 0
  # loop through everything in the source directory
  for pathName in sourcePath.iterdir():
    if pathName.is_dir():
      # recursively un-nest any subdirectories first
      movedFiles, deletedFolders, failedMoves, failedDeletes = unNestPhotos(pathName)
      movedFileCount += movedFiles
      deletedFolderCount += deletedFolders
      failedMoveCount += failedMoves
      failedDeleteCount += failedDeletes
      # for all files in a directory, move all its contents up a level
      for file in pathName.iterdir():
        destination = file.parents[1] / file.name
        try:
          file.rename(destination)
          movedFileCount += 1 # count how many files were moved
        except:
          failedMoveCount += 1 # count failures too
      # check if directory is empty. if so, delete it
      if isDirectoryEmpty(pathName):
        pathName.rmdir()
        deletedFolderCount += 1 # count how many directories were deleted
      else:
        failedDeleteCount += 1
  return movedFileCount, deletedFolderCount, failedMoveCount, failedDeleteCount

def isDirectoryEmpty(sourcePath: Path):
  # check if a directory is empty, returning boolean
  hasNext = next(sourcePath.iterdir(), None)
  if hasNext is None:
    return True
  else:
    return False

def getPhotosAndDates(sourcePath: Path):
  photoList = []
  uniqueDates = []
  skippedPhotos = []
  # loop through all photos
  for pathName in sourcePath.iterdir():
    # if file, add pathname and date to to the dictionary list
    if pathName.is_file():
      photoDate = getPhotoTakenDate(pathName)
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

def getPhotoTakenDate(imgPath: Path):
  img = open(imgPath, 'rb')
  tags = exifread.process_file(img)
  # need to cast tag data to string, since it's a funky format
  dateTakenTag = str(tags.get("EXIF DateTimeOriginal"))
  try:
    return datetime.strptime(dateTakenTag, '%Y:%m:%d %H:%M:%S')
  except:
    return None # if exif tag data is missing, don't return a date

def getPhotoExifData(imgPath: Path):
  # reads out all the non-gigantic tags so you know what those keys will be called
  img = open(imgPath, 'rb')
  tags = exifread.process_file(img)
  for tag in tags.keys():
    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        print("Key: %s, value %s" % (tag, tags[tag]))

def folderizeByDate(photos, dates, threshold, destinationPath):
  daysCreated = 0 # counter of folders created to sort photos into it
  daysSkipped = [] # list of specific days skipped due to threshold
  photosSorted = 0

  # for each unique date, get the list of photos that were taken on that date
  for date in dates:
    photosTakenOnDate = list(filter(lambda photo: datetime.date(photo['date']) == date, photos))
    # print(photosTakenOnDate)
    # if the number of photos taken on that date is greater than a threshold, make a folder with that date name
    if len(photosTakenOnDate) > threshold:
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

def main():
  # set up CLI argument parser
  parser = argparse.ArgumentParser(description='Un-nests all photos in a directory, and sorts them into new directories based on the Date Taken EXIF tag.')
  parser.add_argument('path', type=str, help='File path to a directory of unsorted photos')
  parser.add_argument('threshold', nargs='?', type=int, default=3, help='Minimum number of photos (taken on the same day) that warrants the creation of a folder.  Default is 3.')
  args = parser.parse_args()

  # get settings from arguments
  source = Path(args.path)
  threshold = args.threshold

  # run
  print('---begin photo sorting---')
  startTime = time.process_time()
  if not source.is_dir():
    print('file path does not exist, quitting...')
    quit()
  movedFiles, deletedFolders, failedMoves, failedDeletes = unNestPhotos(source)
  print(f'{movedFiles} files un-nested, {deletedFolders} empty folders deleted')
  print(f'{failedMoves} files could not be moved, so {failedDeletes} folders were left unempty')
  print('indexing photos...')
  photos, dates, skippedFiles = getPhotosAndDates(source)
  print(f'{len(photos)} photos found, taken on {len(dates)} different days')
  created, moved, skippedDays = folderizeByDate(photos, dates, threshold, source)
  print(f'{moved} photos sorted into {created} folders')
  print('issues:')
  print(f'- skipped the following days due to having fewer photos than threshold of {threshold}:\n{skippedDays}')
  print(f'- skipped the following files due to missing or bad date format:\n{skippedFiles}')
  endTime = time.process_time()
  print(f'process took {endTime - startTime} seconds')
  print('---end photo sorting---')

if __name__ == "__main__":
  main()
