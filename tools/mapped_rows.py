"""Pure file-mapping equivalence; never repins or reads processes/files.

Only adjacent ranges with identical permissions/device/inode/path and linear
file offsets coalesce. All mapped bytes and attributes remain in the result.
"""
import re
_ROW=re.compile(r'([0-9a-f]+)-([0-9a-f]+)[ \t]+([r-][w-][x-][ps])[ \t]+([0-9a-f]+)[ \t]+([0-9a-f]+:[0-9a-f]+)[ \t]+([0-9]+)[ \t]+(/[^\r\n]+)')

def canonical_mapped_rows(rows):
 if not isinstance(rows,(list,tuple)) or not 0<len(rows)<=4096:
  raise ValueError('nonempty bounded mapped rows required')
 out=[]
 for row in rows:
  if not isinstance(row,str) or len(row)>16384:
   raise ValueError('invalid mapped row type/length')
  match=_ROW.fullmatch(row)
  if not match:raise ValueError('malformed file-backed mapped row')
  start,end,perms,offset,device,inode,path=match.groups()
  start,end,offset=int(start,16),int(end,16),int(offset,16)
  if not 0<=start<end<=2**64 or not 0<=offset<2**64 or offset+(end-start)>2**64:
   raise ValueError('mapped address/offset bounds')
  if out and start<out[-1][1]:raise ValueError('mapped rows overlap or are out of order')
  current=(start,end,perms,offset,device,inode,path)
  if out:
   previous=out[-1]
   if previous[1]==start and previous[2]==perms and previous[4:]==current[4:] and previous[3]+previous[1]-previous[0]==offset:
    out[-1]=(previous[0],end,perms,previous[3],device,inode,path)
    continue
  out.append(current)
 return tuple(out)
