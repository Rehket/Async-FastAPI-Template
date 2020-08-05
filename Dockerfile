FROM alpine:3.12 AS compile-image
ENV PIP_NO_CACHE_DIR=true
RUN apk info && \
    apk update && \
    apk upgrade && \
    apk del python3 && \
    apk add alpine-sdk py-pip python3-dev postgresql-dev libffi-dev libxslt-dev bash dos2unix llvm-dev
WORKDIR /app_dir/
RUN python3 -m pip install virtualenv --user && \
    python3 -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install --upgrade setuptools gunicorn wheel
COPY ./req.txt /app_dir/req.txt
RUN pip install -r req.txt --no-cache-dir


FROM alpine:3.12 AS build-image
COPY --from=compile-image /opt/venv /app_dir/venv
WORKDIR /app_dir/
ENV PYTHONPATH=/app_dir
ENV PATH="/app_dir/venv/bin/:$PATH"

#COPY ./config_files/inittab /etc/inittab
COPY . /app_dir
COPY ./config_files/inittab /etc/inittab
RUN dos2unix /app_dir/init.ash && \
    chmod +x /app_dir/init.ash && \
    apk update && \
    apk upgrade && \
    apk add --no-cache python3 postgresql-client  dumb-init && \
    cp /usr/bin/python3 /app_dir/venv/bin/python && \
    /app_dir/venv/bin/python /app_dir/venv/bin/mkdocs build

RUN apk info


EXPOSE 8000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["./init.ash"]