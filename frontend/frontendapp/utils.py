import matplotlib.pyplot as pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import base64
from io import BytesIO
from django.db import connection

# def graph_to_img():
#     buffer = BytesIO()
#     pyplot.savefig(buffer, format='png')
#     buffer.seek(0)
#     png = buffer.getvalue()
#     graph = base64.b64encode(png).decode('utf-8')
#     buffer.close()
#     return(graph)

def getplot(name, uni):
    sql = "SELECT * FROM grade_results WHERE LOWER(program) LIKE %s"
    params = [f"%{name.lower()}%"]
    sql += " AND university_name = %s"
    params.append(uni)
    sql += " LIMIT 1000"

    avgs = []
    years = []
    try:
        with connection.cursor() as cursor:
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            for row in rows:
                if(row[0] not in years):
                    years.append(row[0])

            years.sort()

            for i in range(len(years)):
                avgs.append(0)
                count = 0
                for row in rows:
                    if(row[0] == years[i]):
                        avgs[i] += row[3]
                        count += 1
                    
                avgs[-1] /= count
            
    except Exception as e:
        print(e)

    if(len(years) == 0):
        return(None)
    #GRAPH FORMATTING GOES HERE
    # pyplot.switch_backend('AGG')
    fig = Figure(figsize = (10, 5))
    axis = fig.add_subplot(111)
    axis.set_xlabel("Year")
    axis.set_ylabel("Average")
    axis.set_title("Acceptance Averages By Year")
    axis.bar(years, avgs)
    axis.set_xticks(years)
    axis.set_yticks(range(50, 101, 5))
    for p in range(len(avgs)):
        axis.annotate(round(avgs[p], 2), xy=(years[p],avgs[p]),
                ha='center',
                va='center',
                xytext=(0, 10),
                textcoords='offset points')
    # pyplot.title("Acceptance Averages By Year")
    # pyplot.bar(years, avgs)
    # pyplot.xlabel("Year")
    # pyplot.ylabel("Average")
    # pyplot.xticks(years)
    # pyplot.ylim(50, 100)
    # pyplot.yticks(range(50,101, 5))
    # for p in range(len(avgs)):
    #     pyplot.annotate(round(avgs[p], 2), xy=(years[p],avgs[p]),
    #             ha='center',
    #             va='center',
    #             xytext=(0, 10),
    #             textcoords='offset points')
    # Convert figure to base64 string
    canvas = FigureCanvasAgg(fig)
    buffer = BytesIO()
    canvas.print_png(buffer)
    buffer.seek(0)
    png = buffer.getvalue()
    graph = base64.b64encode(png).decode('utf-8')
    buffer.close()
    return graph