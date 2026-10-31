"""Static landscape data only; no fire model, animation, or live-site writes."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, box, mapping, shape
from shapely.ops import transform, unary_union
from shapely.prepared import prep

VERSION = 'conus-scene-context-v1'
CLASSES = ('forest_woodland', 'shrubland', 'grass_herbaceous', 'agriculture',
           'developed', 'open_water', 'sparse_barren', 'snow_ice')
TAGS = ('riparian_wetland_vegetation', 'desert_named_ecosystem', 'developed_vegetation')
CLASS_LABELS = ('Forest / woodland', 'Shrubland', 'Grass / herbaceous', 'Agriculture',
                'Developed land', 'Open water', 'Sparse / barren land', 'Snow / ice')
TO_XY = Transformer.from_crs(4326, 5070, always_xy=True)
TO_LL = Transformer.from_crs(5070, 4326, always_xy=True)
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = {
    'vegetation': '/path/to/LC20_EVT_220.tif',
    'elevation': '/path/to/LF2020_Elev_CONUS.tif',
    'slope': '/path/to/LF2020_SlpD_CONUS.tif',
    'lookup': '/path/to/LF20_EVT_220.csv',
    'boundary': str(Path(__file__).with_name('lower_48.geojson') if Path(__file__).with_name('lower_48.geojson').exists()
                    else Path(__file__).with_name('data') / 'conus_boundary.geojson'),
}


def write_json(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    tmp.replace(path)


def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def category(row):
    lf, phys = row['EVT_LF'], row['EVT_PHYS']
    if lf == 'NA': return 0
    if phys == 'Agricultural' or lf == 'Agriculture': return 4
    return {'Tree': 1, 'Shrub': 2, 'Herb': 3, 'Developed': 5, 'Water': 6,
            'Sparse': 7, 'Barren': 7, 'Snow-Ice': 8}.get(lf, 0)


def make_lookup(path):
    import re
    with Path(path).open() as f: rows = list(csv.DictReader(f))
    codes = np.zeros(65536, dtype=np.uint8)
    tags = np.zeros((len(TAGS), 65536), dtype=np.uint8)
    records = []
    for r in rows:
        value = int(r['VALUE'])
        if value < 0: continue
        c = category(r)
        if c == 0: raise ValueError('Unmapped positive EVT code: ' + str(value))
        flags = [r['EVT_PHYS'] == 'Riparian',
                 bool(re.search(r'\bdesert\b', r['EVT_NAME'] + ' ' + r['EVT_GP_N'], re.I)),
                 r['EVT_PHYS'] == 'Developed' and r['EVT_LF'] in ('Tree', 'Shrub', 'Herb')]
        codes[value] = c; tags[:, value] = flags
        records.append({'value': value, 'name': r['EVT_NAME'], 'lifeform': r['EVT_LF'],
                        'physiognomy': r['EVT_PHYS'], 'group': r['EVT_GP_N'],
                        'class': CLASSES[c-1], 'tags': [t for t, yes in zip(TAGS, flags) if yes]})
    return codes, tags, records


def boundary(path):
    raw = json.loads(Path(path).read_text())
    ll = unary_union([shape(f['geometry']) for f in raw['features']])
    return ll, transform(TO_XY.transform, ll)


def coordinates(lon, lat):
    if isinstance(lon, bool) or isinstance(lat, bool): raise ValueError('Numeric longitude/latitude required')
    lon, lat = float(lon), float(lat)
    if not math.isfinite(lon) or not math.isfinite(lat) or not -180 <= lon <= 180 or not -90 <= lat <= 90:
        raise ValueError('Invalid longitude/latitude')
    return lon, lat


def terrain_label(mean_slope, relief):
    if mean_slope is None or relief is None: return 'unknown'
    if mean_slope < 3 and relief < 50: return 'flat'
    if mean_slope < 8 and relief < 150: return 'rolling'
    if mean_slope < 18 and relief < 500: return 'hilly'
    return 'rugged'


def bounds_info(x0, y0, width, height):
    xs = [x0, x0+width, x0+width, x0, x0]
    ys = [y0, y0, y0-height, y0-height, y0]
    lons, lats = TO_LL.transform(xs, ys)
    return {'crs': 'EPSG:5070', 'bounds_m': [x0, y0-height, x0+width, y0],
            'size_m': [width, height], 'polygon_wgs84': {'type':'Polygon',
            'coordinates': [[[round(x, 8), round(y, 8)] for x,y in zip(lons,lats)]]},
            'bbox_wgs84': list(TO_LL.transform_bounds(x0,y0-height,x0+width,y0,densify_pts=21))}


def summary(counts, tag_counts, domain_count, total_count, dem_count, dem_sum,
            dem_min, dem_max, slope_count, slope_sum, steep_count):
    covered = int(sum(counts))
    frac = lambda n,d: round(float(n)/d, 8) if d else None
    composition = {k: frac(n, covered) for k,n in zip(CLASSES, counts)}
    ordered = sorted(zip(CLASSES, counts), key=lambda kv: -int(kv[1]))
    components = [k for k,n in ordered if covered and n/covered >= .10]
    dominant = ordered[0][0] if covered else None
    ms = float(slope_sum)/slope_count if slope_count else None
    relief = float(dem_max)-float(dem_min) if dem_count else None
    return {'composition': composition, 'tags': {k:frac(n,covered) for k,n in zip(TAGS,tag_counts)},
      'coverage': {'native_pixel_area_m2':900, 'footprint_area_m2':int(total_count)*900,
        'in_conus_area_m2':int(domain_count)*900, 'mapped_cover_area_m2':covered*900,
        'conus_fraction_of_footprint':frac(domain_count,total_count),
        'cover_fraction_of_conus':frac(covered,domain_count),
        'elevation_fraction_of_conus':frac(dem_count,domain_count),
        'slope_fraction_of_conus':frac(slope_count,domain_count),
        'unknown_cover_area_m2':int(domain_count-covered)*900},
      'terrain': {'descriptor':terrain_label(ms,relief),
        'elevation_mean_m':round(float(dem_sum)/dem_count,2) if dem_count else None,
        'elevation_min_m':float(dem_min) if dem_count else None,
        'elevation_max_m':float(dem_max) if dem_count else None,
        'relief_m':relief, 'slope_mean_degrees':round(ms,3) if ms is not None else None,
        'slope_at_least_15_degrees_fraction':frac(steep_count,slope_count)},
      'scene_components':components, 'dominant_cover':dominant,
      'composition_is_mixed':len(components)>1}


class SourceReader:
    def __init__(self, sources=None):
        import rasterio
        self.paths = sources or DEFAULT_SOURCES
        self.codes,self.tag_lookup,self.mapping = make_lookup(self.paths['lookup'])
        self.ll,self.xy = boundary(self.paths['boundary'])
        self.ll_prepared,self.xy_prepared=prep(self.ll),prep(self.xy)
        self.sources = {k:rasterio.open(self.paths[k]) for k in ('vegetation','elevation','slope')}
        base = self.sources['vegetation'];self.transform = base.transform
        self.offsets = {}
        for name,s in self.sources.items():
            if s.crs.to_epsg()!=5070 or s.res!=(30,30) or s.transform.b or s.transform.d:
                raise ValueError('Expected aligned 30 m EPSG:5070 rasters')
            dc=(base.transform.c-s.transform.c)/30;dr=(s.transform.f-base.transform.f)/30
            if abs(dc-round(dc))>1e-6 or abs(dr-round(dr))>1e-6: raise ValueError('Misaligned inputs')
            self.offsets[name]=(round(dr),round(dc))

    def close(self):
        for s in self.sources.values():s.close()

    def read(self,row,col,height,width):
        from rasterio.windows import Window
        from rasterio.features import rasterize
        t=self.transform * __import__('affine').Affine.translation(col,row)
        extent=box(t.c,t.f-height*30,t.c+width*30,t.f)
        if self.xy_prepared.covers(extent):
            domain=np.ones((height,width),dtype=bool)
        elif not self.xy_prepared.intersects(extent):
            domain=np.zeros((height,width),dtype=bool)
        else:
            clipped=self.xy.intersection(extent)
            domain=rasterize([(mapping(clipped),1)],out_shape=(height,width),transform=t,fill=0,dtype='uint8').astype(bool)
        data={}
        for name,s in self.sources.items():
            dr,dc=self.offsets[name]
            a=s.read(1,window=Window(col+dc,row+dr,width,height),boundless=True,masked=True)
            data[name]=a
        veg=data['vegetation'];safe=np.where(~np.ma.getmaskarray(veg)&(veg.data>=0),veg.data,0).astype('uint16')
        cover=self.codes[safe];cover[~domain]=0
        tags=self.tag_lookup[:,safe];tags[:,~domain]=0
        dem=data['elevation'];dem_ok=domain&~np.ma.getmaskarray(dem)&(dem.data>=-500)&(dem.data<=9000)
        slope=data['slope'];slope_ok=domain&~np.ma.getmaskarray(slope)&(slope.data>=0)&(slope.data<=90)
        return {'cover':cover,'tags':tags,'domain':domain,'elevation':dem.data,'dem_ok':dem_ok,
                'slope':slope.data,'slope_ok':slope_ok,'transform':t}


def aggregate(data, factor):
    h,w=data['domain'].shape
    if h%factor or w%factor: raise ValueError('Grid must be block-aligned')
    def blocks(a): return a.reshape(h//factor,factor,w//factor,factor)
    def total(a): return blocks(a).sum(axis=(1,3))
    cover=data['cover'];d=data['dem_ok'];s=data['slope_ok']
    counts=np.stack([total(cover==i) for i in range(1,9)]).astype('uint16')
    tag_counts=np.stack([total(v) for v in data['tags']]).astype('uint16')
    return {'counts':counts,'tag_counts':tag_counts,'domain_count':total(data['domain']).astype('uint16'),
      'dem_count':total(d).astype('uint16'),'dem_sum':total(np.where(d,data['elevation'],0)).astype('int32'),
      'dem_min':blocks(np.where(d,data['elevation'],32767)).min(axis=(1,3)).astype('int16'),
      'dem_max':blocks(np.where(d,data['elevation'],-32768)).max(axis=(1,3)).astype('int16'),
      'slope_count':total(s).astype('uint16'),'slope_sum':total(np.where(s,data['slope'],0)).astype('uint32'),
      'steep_count':total(s&(data['slope']>=15)).astype('uint16')}


def aggregate_summary(a,row=0,col=0,factor=100):
    return summary(a['counts'][:,row,col],a['tag_counts'][:,row,col],
        int(a['domain_count'][row,col]),factor*factor,
        *[int(a[k][row,col]) for k in ['dem_count','dem_sum','dem_min','dem_max','slope_count','slope_sum','steep_count']])


def envelope(lon,lat,mode):
    return {'schema_version':VERSION,'selection':{'longitude':lon,'latitude':lat},
      'mode':mode, 'status':'ok','source_edition':{'vegetation':2020,'terrain_product':2020},
      'dynamic_inputs_included':False,'layout':None}


def local_context(reader, lon, lat, width_m=3000, max_grid_side=50):
    lon,lat=coordinates(lon,lat);out=envelope(lon,lat,'local_patch')
    if not reader.ll_prepared.covers(Point(lon,lat)):
        return {**out,'status':'outside_conus','reason':'Target is outside the supplied Lower 48 boundary.'}
    if not 300<=width_m<=6000 or not 10<=max_grid_side<=100:raise ValueError('Patch or layout size out of bounds')
    n=int(math.ceil(width_m/30));factor=max(1,int(math.ceil(n/max_grid_side)));n=int(math.ceil(n/factor))*factor
    x,y=TO_XY.transform(lon,lat);col=int(math.floor((x-reader.transform.c)/30-n/2));row=int(math.floor((reader.transform.f-y)/30-n/2))
    d=reader.read(row,col,n,n);a=aggregate(d,n);t=d['transform']
    out.update(aggregate_summary(a,factor=n));out['footprint']=bounds_info(t.c,t.f,n*30,n*30)
    out['requested_width_m']=width_m;out['native_pixel_size_m']=30
    out['lookup_support']='Requested local square, snapped to the native 30 m grid.'
    g=aggregate(d,factor);cover_count=g['counts'].sum(axis=0);dom=g['counts'].argmax(axis=0)+1;dom[cover_count==0]=0
    def div(a,b,precision):
        z=np.full(a.shape,np.nan);np.divide(a,b,out=z,where=b>0)
        return [[None if not np.isfinite(v) else round(float(v),precision) for v in row] for row in z]
    out['layout']={'crs':'EPSG:5070','origin_upper_left_m':[t.c,t.f],
        'axis_order':'row-major; rows southward, columns eastward; projected grid north is up',
        'width':int(n/factor),'height':int(n/factor),'cell_size_m':factor*30,
        'class_codes':{'0':'unknown',**{str(i+1):c for i,c in enumerate(CLASSES)}},
        'dominant_cover':dom.tolist(),
        'cover_fraction':{c:div(g['counts'][i],cover_count,4) for i,c in enumerate(CLASSES)},
        'known_cover_fraction':div(cover_count,np.full(cover_count.shape,factor*factor),4),
        'conus_fraction':div(g['domain_count'],np.full(cover_count.shape,factor*factor),4),
        'elevation_mean_m':div(g['dem_sum'],g['dem_count'],2),
        'slope_mean_degrees':div(g['slope_sum'],g['slope_count'],2)}
    if not cover_count.any():out['status']='no_landcover_data'
    return out


class Atlas:
    def __init__(self,bundle):
        self.root=Path(bundle);self.manifest=json.loads((self.root/'manifest.json').read_text())
        self.data=np.load(self.root/'conus_context.npz',allow_pickle=False)
        self.ll,_=boundary(self.root/'lower_48.geojson')
        self.ll_prepared=prep(self.ll)
        # Load once per process: repeated clicks should not decompress the archive.
        self.arrays={k:self.data[k] for k in self.data.files};self.data.close()

    def query(self,lon,lat):
        lon,lat=coordinates(lon,lat);out=envelope(lon,lat,'national_cell')
        if not self.ll_prepared.covers(Point(lon,lat)):return {**out,'status':'outside_conus','reason':'Target is outside the supplied Lower 48 boundary.'}
        g=self.manifest['grid'];x,y=TO_XY.transform(lon,lat)
        col=int(math.floor((x-g['origin_upper_left_m'][0])/g['cell_size_m']))
        row=int(math.floor((g['origin_upper_left_m'][1]-y)/g['cell_size_m']))
        if not 0<=row<g['height'] or not 0<=col<g['width']:raise ValueError('Coordinate outside atlas grid')
        out.update(aggregate_summary(self.arrays,row,col))
        out['cell_id']=f'c3k-r{row}-c{col}'
        out['footprint']=bounds_info(g['origin_upper_left_m'][0]+col*3000,g['origin_upper_left_m'][1]-row*3000,3000,3000)
        out['lookup_support']='Containing 3 km cell; percentages are regional context, not target-pixel or 200 m scene fractions.'
        out['native_pixel_size_m']=30
        if not self.arrays['counts'][:,row,col].any():out['status']='no_landcover_data'
        return out
