import os
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def _DownloadCrxFromCws(ext_id, dst):
  """Downloads CRX specified from Chrome Web Store.
  Retrieves CRX (Chrome extension file) specified by ext_id from Chrome Web
  Store, into directory specified by dst.
  Args:
      ext_id: id of extension to retrieve.
      dst: directory to download CRX into
  Returns:
      Returns local path to downloaded CRX.
      If download fails, return None.
  """
  dst_path = os.path.join(dst, '%s.crx' % ext_id)
  cws_url = ('https://clients2.google.com/service/update2/crx?response='
             'redirect&prodversion=38.0&x=id%%3D%s%%26installsource%%3D'
             'ondemand%%26uc' % ext_id)
  req = urllib.request.urlopen(cws_url)
  res = req.read()
  if req.getcode() != 200:
    return None
#   print(res)
  with open(dst_path, 'wb') as f:
    f.write(res)
  return dst_path

id ='glndpobbpolodbopnhcjhkmhimimecop'
dst='chrome_web_store_crawler/tmp'
_DownloadCrxFromCws(id,dst)