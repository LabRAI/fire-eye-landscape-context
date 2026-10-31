import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box,mapping
from shapely.ops import transform

from context import (CLASSES, SourceReader, TO_LL, aggregate, aggregate_summary,
                     category, coordinates, local_context, summary, terrain_label)


class ContextTests(unittest.TestCase):
    def test_orchard_is_agriculture_not_natural_forest(self):
        self.assertEqual(category({'EVT_LF':'Tree','EVT_PHYS':'Agricultural'}),4)

    def test_riparian_forest_remains_forest(self):
        self.assertEqual(category({'EVT_LF':'Tree','EVT_PHYS':'Riparian'}),1)

    def test_nonfinite_and_swapped_coordinates_rejected(self):
        for lon,lat in [(True,30),(float('nan'),30),(36,-100),(200,30)]:
            with self.assertRaises(ValueError):coordinates(lon,lat)

    def test_unsigned_sort_and_unknown_are_not_grass(self):
        d=summary(np.array([20,0,0,0,80,0,0,0],dtype='uint16'),[0,0,0],120,200,0,0,32767,-32768,0,0,0)
        self.assertEqual(d['dominant_cover'],'developed')
        self.assertEqual(d['scene_components'],['developed','forest_woodland'])
        self.assertAlmostEqual(sum(d['composition'].values()),1)
        self.assertEqual(d['coverage']['unknown_cover_area_m2'],18000)
        self.assertIsNone(d['terrain']['elevation_mean_m'])

    def test_empty_coverage_keeps_null(self):
        d=summary([0]*8,[0]*3,100,100,0,0,32767,-32768,0,0,0)
        self.assertTrue(all(v is None for v in d['composition'].values()))
        self.assertEqual(d['terrain']['descriptor'],'unknown')
        self.assertIsNone(d['dominant_cover'])

    def test_terrain_uses_relief_not_absolute_elevation(self):
        self.assertEqual(terrain_label(2,20),'flat')
        self.assertEqual(terrain_label(20,700),'rugged')
        self.assertEqual(terrain_label(2,800),'rugged')

    def test_aligned_sources_preserve_layout_and_nodata(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);x0,y0=-1000000,2000000
            base=from_origin(x0,y0,30,30)
            veg=np.full((12,12),100,dtype='int16');veg[:,6:]=200;veg[0,0]=32767
            dem=(np.arange(144).reshape(12,12)-60).astype('int16')
            dem[1,1]=32767
            slope=np.full((12,12),20,dtype='int16');slope[0,0]=32767
            paths={}
            for name,array in [('vegetation',veg),('elevation',dem),('slope',slope)]:
                t=base
                if name!='vegetation':
                    array=np.pad(array,((0,0),(1,0)),constant_values=32767);t=from_origin(x0-30,y0,30,30)
                p=root/(name+'.tif');paths[name]=str(p)
                with rasterio.open(p,'w',driver='GTiff',height=array.shape[0],width=array.shape[1],count=1,dtype='int16',crs='EPSG:5070',transform=t,nodata=32767) as f:f.write(array,1)
            lookup=root/'lookup.csv';paths['lookup']=str(lookup)
            with lookup.open('w') as f:
                w=csv.DictWriter(f,fieldnames=['VALUE','EVT_NAME','EVT_LF','EVT_PHYS','EVT_GP_N']);w.writeheader()
                w.writerow({'VALUE':100,'EVT_NAME':'Test forest','EVT_LF':'Tree','EVT_PHYS':'Riparian','EVT_GP_N':'Floodplain forest'})
                w.writerow({'VALUE':200,'EVT_NAME':'Open water','EVT_LF':'Water','EVT_PHYS':'Open Water','EVT_GP_N':'Open Water'})
            geom=transform(TO_LL.transform,box(x0-100,y0-500,x0+500,y0+100))
            boundary=root/'lower_48.geojson';paths['boundary']=str(boundary)
            boundary.write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':mapping(geom)}]}))
            r=SourceReader(paths)
            try:
                d=r.read(0,0,12,12)
                self.assertTrue(np.array_equal(d['elevation'],dem))
                self.assertEqual(d['cover'][0,0],0)
                self.assertEqual(d['cover'][0,7],6)
                a=aggregate(d,12);s=aggregate_summary(a,factor=12)
                self.assertEqual(a['counts'][0,0,0],71)
                self.assertEqual(a['counts'][5,0,0],72)
                self.assertEqual(a['tag_counts'][0,0,0],71)
                self.assertEqual(s['coverage']['mapped_cover_area_m2'],143*900)
                self.assertAlmostEqual(s['terrain']['elevation_mean_m'],round(float(dem[dem!=32767].mean()),2))
                lon,lat=TO_LL.transform(x0+165,y0-165)
                patch=local_context(r,lon,lat,300)
                self.assertEqual(patch['layout']['cell_size_m'],30)
                self.assertEqual(patch['layout']['dominant_cover'][0][0],0)
                self.assertEqual(patch['layout']['dominant_cover'][0][7],6)
                self.assertIsNone(patch['layout']['elevation_mean_m'][1][1])
                self.assertLess(patch['terrain']['elevation_min_m'],0)
                outside=local_context(r,0,0)
                self.assertEqual(outside['status'],'outside_conus');self.assertIsNone(outside['layout'])
            finally:r.close()


if __name__=='__main__':unittest.main()
