from photo_sorter.exif_utils import get_exif_date_taken
from unittest import mock
import datetime

MOCK_EXIF = {
  'EXIF DateTimeOriginal': '2022:08:29 12:34:56'
}

@mock.patch('builtins.open', return_value=0)
@mock.patch('photo_sorter.exif_utils.exifread.process_file', return_value=MOCK_EXIF)
def test_get_exif_date_taken_has_date(_mock1, _mock2):
  date_taken = get_exif_date_taken('mockpath')
  assert date_taken == datetime.datetime(2022, 8, 29, 12, 34, 56)

@mock.patch('builtins.open', return_value=0)
@mock.patch('photo_sorter.exif_utils.exifread.process_file', return_value=dict())
def test_get_exif_date_taken_has_no_date(_mock1, _mock2):
  date_taken = get_exif_date_taken('mockpath')
  assert date_taken == None
