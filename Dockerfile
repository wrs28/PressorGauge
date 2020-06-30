FROM python:3

EXPOSE 8501

ADD src /opt/streamlit-app
WORKDIR /opt/streamlit-app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir -p ~/.streamlit/

RUN bash -c echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
" > ~/.streamlit/config.toml

CMD streamlit run PressorGauge.py
