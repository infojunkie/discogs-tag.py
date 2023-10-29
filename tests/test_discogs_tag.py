from discogs_tag.cli import apply_metadata

def test_apply_metadata():
  audio = {}
  apply_metadata({
    'title': 'Title',
    'artists': [{
      'anv': 'Artist 1'
    }, {
      'name': 'Artist 2'
    }],
    'position': '1-02',
    'extraartists': [{
      'role': 'Guitar',
      'name': 'Guitarist'
    }, {
      'role': 'Written-By',
      'name': 'Composer'
    }]
  }, audio)
  assert audio['title'] == 'Title'
  assert audio['artist'] == 'Artist 1, Artist 2'
  assert audio['discnumber'] == '1'
  assert audio['tracknumber'] == '02'
  assert audio['composer'] == 'Composer'
