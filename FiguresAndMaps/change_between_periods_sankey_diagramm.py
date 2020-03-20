import plotly.graph_objects as go
import pandas as pd

df = pd.read_excel(r"Q:\FORLand\Clemens\data\tables\CropRotations\2005-2011_2012-2018_AreaOfChangeInMainTypes_v2_clean.xlsx", sheet_name="Tabelle1")

sources = list(df['Source'])
targets = list(df['Target'])
values = list(df['Area'])
labels = ['A-per1','B-per1','C-per1','D-per1','E-per1','F-per1','G-per1','H-per1','I-per1','A-per2','B-per2','C-per2','D-per2','E-per2','F-per2','G-per2','H-per2','I-per2']

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = dict(
      source = sources, # indices correspond to labels, eg A1, A2, A2, B1, ...
      target = targets,
      value = values
  ))])

fig.update_layout(title_text="Change", font_size=10)
fig.show()


## without stable areas
sources = list(df['Source'])[10:]
targets = list(df['Target'])[10:]
values = list(df['Area'])[10:]
labels = ['A-per1','B-per1','C-per1','D-per1','E-per1','F-per1','G-per1','H-per1','I-per1','A-per2','B-per2','C-per2','D-per2','E-per2','F-per2','G-per2','H-per2','I-per2']

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = dict(
      source = sources, # indices correspond to labels, eg A1, A2, A2, B1, ...
      target = targets,
      value = values
  ))])

fig.update_layout(title_text="Change", font_size=10)
fig.show()