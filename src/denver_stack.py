"""
denver_stack.py

plots inverse distance to primary and secondary roadways of a custom MapZen extraction
of OpenStreetMap data for metro Denver. 

Data Copyright:
Powered by MapZen (https://mapzen.com), Attribution: https://www.mapzen.com/rights
Data © OpenStreetMaps (OSM) contributors: https://openstreetmap.org/copyright

Code Copyright (C) 2016  Chris Havlin, <https://chrishavlin.wordpress.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import shapefile
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
from descartes.patch import PolygonPatch

"""
 IMPORT THE SHAPEFILE 
"""

shp_file_base='ex_QMDJXT8DzmqNh6eFiNkAuESyDNCX_osm_line'
dat_dir='../shapefiles/denver_maps/grouped_by_geometry_type/'
sf = shapefile.Reader(dat_dir+shp_file_base)
print 'number of shapes imported:',len(sf.shapes())

"""
       PLOTTING
"""
# get list of field names, pull out appropriate index
fld = sf.fields[1:]
field_names = [field[0] for field in fld]
print 'record field names:',field_names
map_geoms=['highway']#,'highway','bridge','tunnel']

plot_these_rec_vals=list()
plot_these_rec_vals.append('motorway')
plot_these_rec_vals.append('motorway_link')
plot_these_rec_vals.append('primary')
plot_these_rec_vals.append('secondary')

# grid for bg coloring
ymin=39.
ymax=40.2
xmin=-105.45
xmax=-104.4
nx = 200

x_o = np.linspace(xmin,xmax,nx)
dy = abs(x_o[1]-x_o[2])
y_o = np.linspace(ymin,ymax,int(abs(ymax-ymin)/dy))
ny = len(y_o)
Xg,Yg=np.meshgrid(x_o,y_o)

# distance to look for nearest neighbors
Dist = np.zeros((ny,nx))
dx = abs(x_o[1]-x_o[0])
Dismin = abs(xmax-xmin)/20#4*dx

""" PLOTS ALL SHAPES AND PARTS """
plt.figure()
ax = plt.axes() # add the axes
ax.set_aspect('equal')

shape_id = 0
nshapes=len(sf.shapes())
rec_vals=list()
previous=0
for shapeRec in sf.iterShapeRecords():
    # pull out shape geometry and records
    shape_id = shape_id+1
    pct_comp=float(int(float(shape_id)/float(nshapes)*10000))/100.
    print shape_id, 'of', nshapes, '(', pct_comp,'% )'
    shape=shapeRec.shape 
    rec = shapeRec.record 

    # select polygon facecolor RGB vals based on record value
    R = 0.81
    G = 0.81
    B = 0.81

    nparts = 0
    for mapg in map_geoms:
        if rec[field_names.index(mapg)] not in rec_vals:
           print rec[field_names.index(mapg)]
           rec_vals.append(rec[field_names.index(mapg)])

        if rec[field_names.index(mapg)] in plot_these_rec_vals:
            nparts = len(shape.parts) # total parts
            Pts = Point(shape.points)

            Lin=LineString(shape.points)
            Bounds=Lin.bounds #(minx, miny, maxx, maxy)
            minx=Bounds[0]
            miny=Bounds[1]
            maxx=Bounds[2]
            maxy=Bounds[3]
            
            Xsub = x_o[x_o>minx-Dismin]
            Xsub = Xsub[Xsub<maxx+Dismin]
            Ysub = y_o[y_o>miny-Dismin]
            Ysub = Ysub[Ysub<maxy+Dismin]
            Xg1,Yg1=np.meshgrid(Xsub,Ysub)
            GridPts = zip(Xg1.ravel(), Yg1.ravel())
            
            for Pt in GridPts:
                Dis = 1.0/(Lin.distance(Point(Pt))+.01)
                if Dis > Dist[y_o==Pt[1],x_o==Pt[0]]:
                   Dist[y_o==Pt[1],x_o==Pt[0]]=Dis#float(Dis<Dismin)

    if nparts == 1:
        Line = LineString(shape.points)
        x,y = Line.xy
        ax.plot(x, y, color=[R,G,B], zorder=2)

    elif nparts > 0 : # loop over parts of each shape, plot separately
        for ip in range(nparts): # loop over parts, plot separately
            i0=shape.parts[ip]
            if ip < nparts-1:
               i1 = shape.parts[ip+1]-1
            else:
               i1 = len(shape.points)

            # build the polygon and add it to plot   
            Line = LineString(shape.points[i0:i1+1])
            x,y = Line.xy
            ax.plot(x, y, color=[R,G,B],zorder=2)

print 'record field names:',field_names
print 'possible record values for ',map_geoms,':',rec_vals

plt.contourf(Xg,Yg,Dist,100,linewidths=None,zorder=1,cmap=plt.get_cmap('copper'))

plt.xlim(xmin,xmax)
plt.ylim(ymin,ymax)
plt.show()

