FROM python:3.7

EXPOSE 8050

COPY requirements.txt ./
COPY dashboard.py ./
COPY games.csv ./

RUN pip install -r requirements.txt
RUN python -m pip install dash-bootstrap-components

CMD ["python", "./dashboard.py"]



