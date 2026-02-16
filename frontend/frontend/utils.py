import matplotlib.pyplot
import base64
from io import BytesIO

def graph_to_img():
    buffer = BytesIO()
    matplotlib.pyplot.savefig(buffer, format='png')
    buffer.seek(0)
    png = buffer.getvalue()
    graph = base64.b64encode(png).decode('utf-8')
    buffer.close()
    return(graph)

def getplot(x, y):
    #GRAPH FORMATTING GOES HERE

    return graph_to_img()