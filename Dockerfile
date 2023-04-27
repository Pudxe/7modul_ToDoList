FROM python:3.10

WORKDIR /todolist/

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . .

ENTRYPOINT ["bash", "entrypoint.sh"]

EXPOSE 8000

CMD ["gunicorn", "todolist.wsgi", "-w", "4", "-b", "0.0.0.0:8000"]

