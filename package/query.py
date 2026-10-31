"""Emit the simulation provider's landscape contract for a longitude/latitude."""
import argparse
import json
from context import Atlas, SourceReader, local_context, write_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--longitude',type=float,required=True);p.add_argument('--latitude',type=float,required=True)
    p.add_argument('--bundle',help='Directory containing manifest.json and conus_context.npz')
    p.add_argument('--local',action='store_true',help='Read a local native-resolution patch; requires source rasters')
    p.add_argument('--sources',help='JSON source-path overrides for local mode')
    p.add_argument('--width-m',type=int,default=3000);p.add_argument('--output')
    a=p.parse_args()
    if a.local:
        reader=SourceReader(json.load(open(a.sources)) if a.sources else None)
        try:result=local_context(reader,a.longitude,a.latitude,a.width_m)
        finally:reader.close()
    elif a.bundle:result=Atlas(a.bundle).query(a.longitude,a.latitude)
    else:p.error('Choose --bundle or --local')
    if a.output:write_json(a.output,result)
    else:print(json.dumps(result,indent=2,allow_nan=False))

if __name__=='__main__':main()
