# travel-times
Python code which determines the travel time from locations around a certain destination coordinate

### Python packages (tested version)
- GDAL					(v3.4.3)
- osrm					(v0.11.3)
- polyline 				(v1.4.0)
- basemap 				(v1.3.6)
- basemap-data-hires 	(v1.3.2)

### ImportError: cannot import name 'griddata' from 'matplotlib.mlab
In case this error is encountered go to extra.py (of the osrm package) and change line 14 to:
```python
from scipy.interpolate import griddata
```

Since griddata is deprecated in matplotlib. This issue is also mentioned here:
https://github.com/ustroetz/python-osrm/issues/40