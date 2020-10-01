# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 08:08:09 2020

@author: mthom
"""


from bokeh.plotting import figure, curdoc
from bokeh.tile_providers import get_provider, Vendors
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import column
from bokeh.models import Button
from bokeh.io import export_png
from bokeh.models import Label
from bokeh.models.glyphs import Text


path = 'C:\\Users\\Name\\AnimatedGraph' #update with your working directory
df = pd.read_csv('https://raw.githubusercontent.com/mthomp12/Animated_Divvy_Graph/master/divvy_data.csv')

df['circle_sizes'] = df['avg_trip_count'] / df['avg_trip_count'].max() * 40
temps = df['temp'].unique().tolist()


df_all = df.copy()
#only load in data for first temperature
df = df[df['temp']==df['temp'].min()]

source = ColumnDataSource(data=dict(
                        x=list(df['coords_x']), 
                        y=list(df['coords_y']),
                        ridership=list(df['avg_trip_count']),
                        sizes=list(df['circle_sizes']),
                        stationname=list(df['station_name'])))

hover = HoverTool(tooltips=[
    ("station", "@stationname"),
    ("ridership","@ridership")
    
])


p = figure(x_range=(-9759380, -9749918), y_range=(5140778, 5150200),
           x_axis_type="mercator", y_axis_type="mercator", tools=['pan',hover, 'wheel_zoom', 'save'])


p.add_tile(get_provider(Vendors.CARTODBPOSITRON))


r = p.circle(x = 'x',
         y = 'y',
         source=source,
         size='sizes',
        line_color="#FF0000", 
         fill_color="#FF0000",
         fill_alpha=0.05
        )

ds = r.data_source

i=0
start = False
idx = 0
period = 20
refresh = 80


def start_graph():
    global start
    start = True
    return 0

def callback():
    if start:
        global i, temps, temp_button, idx, refresh, mytext, p
        new_data = dict()
        
        #stop updating once it hits 80
        if idx<len(temps)-1:
            
            #new data at end of period
            if i%period==0 and i>0:
                temp_button.label = str(int(temps[idx+1]))
                mytext.text = 'Temp: {}\N{DEGREE SIGN}F'.format(int(temps[idx+1]))
                new_data['sizes'] = list(df_all[df_all['temp']==temps[idx+1]]['circle_sizes'])
                new_data['ridership'] = list(df_all[df_all['temp']==temps[idx+1]]['avg_trip_count'])
                new_data['x'] = ds.data['x']
                new_data['y'] = ds.data['y']
                new_data['stationname'] = ds.data['stationname']
                ds.data = new_data
                idx+=1
            
            #interpolate data before end of period
            elif i>0:
                tick = i%period
                temp_button.label = str(int(temps[idx]*(period-tick)/period + temps[idx+1] * tick/period))
                mytext.text = 'Temp: {}\N{DEGREE SIGN}F'.format(int(temps[idx]*(period-tick)/period + temps[idx+1] * tick/period))
                size_1 = list(df_all[df_all['temp']==temps[idx]]['circle_sizes'])
                size_2 = list(df_all[df_all['temp']==temps[idx+1]]['circle_sizes'])
                size_interpolated = [x*(period-tick)/period+y*tick/period for x, y in zip(size_1,size_2)]
                new_data['sizes'] =size_interpolated
                            
                new_data['ridership'] = list(df_all[df_all['temp']==temps[idx]]['avg_trip_count'])
                
                
                new_data['x'] = ds.data['x']
                new_data['y'] = ds.data['y']
                new_data['stationname'] = ds.data['stationname']
                ds.data = new_data
            
            #save every iteration to .png file
            #export_png(p, filename = '{0}/gif/plot_{1}.png'.format(path, i))
        i+=1
    
button = Button(label="Start")
button.on_click(start_graph)  

temp_button = Button(label=str(int(temps[0])))

loc =  (-9756040, 5148472)
mytext = Label(x=loc[0], y=loc[1], text='Temp: 30\N{DEGREE SIGN}F', text_font_size='25pt')
p.add_layout(mytext)

beaches = ['Lake Shore Dr & North Blvd', 'Streeter Dr & Grand Ave', 'Lake Shore Dr & Monroe St', 'Theater on the Lake', 'Michigan Ave & Oak St']
beach_names = ['North Avenue Beach', 'Navy Pier', 'Monroe Harbor', 'Fullerton Beach', 'Oak Street Beach']
beach_dict  = dict(zip(beaches,beach_names))
beach = df.loc[[True if x in beaches else False for x in df['station_name']]].loc[df['station_name']!=df['station_name'].shift(1)]

text_source = ColumnDataSource(dict(x=beach['coords_x'].values, y=beach['coords_y'].values, text=[beach_dict[x] for x in beach['station_name'].values]))
glyph = Text(x="x", y="y", text="text", text_color='#6baed6')
p.add_glyph(text_source, glyph)

#Legend
rides = [50, 100, 200, 400]
circles = [x / df_all['avg_trip_count'].max() * 40 for x in rides]
x_coords = [-9752040] * 4
y_coords = [5149872, 5149524, 5149152, 5148533]
legend = p.circle(x = x_coords, y = y_coords, size=circles, line_color="#FF0000", fill_color="#FF0000", fill_alpha=0.05)
p.add_layout(Label(x = -9752100, y=5150072, text='Rides Per Day'))

for x,y,text in zip(x_coords, y_coords, rides):
    p.add_layout(Label(x = x+(500 if text!=50 else 595), y=y-200, text=str(text)))
#end legend

curdoc().add_root(column(p, button))
curdoc().add_periodic_callback(callback, refresh)

#Bash Code to Run 
#bokeh serve --show C:\Users\mthom\blog\AnimatedGraph\AnimatedGraph.py
