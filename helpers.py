from functools import wraps
from flask import session, redirect, request
from datetime import datetime
import io
import base64

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

'''def graph(rows):

    if not rows or len(rows) < 5:
        return "/static/error-no-data.jpeg"

    else:

        dates = []
        amounts = []
        for row in rows:
            dates.append(row["date"])
            amounts.append(row["amount"])
    
        date_objects = []
        for date in dates:
            date_objects.append(datetime.strptime(date, "%Y-%m-%d"))

        plt.plot(date_objects, amounts, 'b-')

        plt.xlabel('Time')
        plt.ylabel('Amount ($)')
        plt.title('Income Trend in the Past Year')

        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b"))
        plt.gcf().autofmt_xdate() 

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()

        return graph_url
        '''

    