FROM python:3

ADD hello_cadcad.py /

RUN pip3 install numpy
RUN pip3 install matplotlib

RUN pip3 install pandas
RUN pip3 install wheel
RUN pip3 install pathos
RUN pip3 install fn
RUN pip3 install tabulate
RUN pip3 install funcy
RUN pip3 install pytest
RUN pip3 install hypothesis

RUN pip3 install cadCAD

CMD [ "python", "./hello_cadcad.py" ]