"""Serve only this delivery folder, with byte ranges for video seeking."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.remaining=None
        path=Path(self.translate_path(self.path)).resolve()
        if not path.is_relative_to(ROOT):
            self.send_error(403);return None
        value=self.headers.get('Range')
        if value and path.is_file():
            size=path.stat().st_size
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',value.strip())
            if not match or not any(match.groups()):
                self.send_error(416);return None
            first,last=match.groups()
            start=int(first) if first else max(0,size-int(last))
            end=min(int(last),size-1) if first and last else size-1
            if start>=size or start>end:
                self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
            self.send_response(206)
            self.send_header('Content-Type',self.guess_type(str(path)))
            self.send_header('Content-Length',str(end-start+1))
            self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.send_header('Accept-Ranges','bytes');self.end_headers()
            self.remaining=end-start+1
            f=path.open('rb');f.seek(start);return f
        return super().send_head()
    def copyfile(self,source,outputfile):
        if self.remaining is None:return super().copyfile(source,outputfile)
        while self.remaining>0:
            data=source.read(min(1024*1024,self.remaining))
            if not data:break
            outputfile.write(data);self.remaining-=len(data)
if __name__=='__main__':
    print('Budgetly reel room: listening on 0.0.0.0:3000',flush=True)
    ThreadingHTTPServer(('0.0.0.0',3000),Handler).serve_forever()
