FROM python:3.12-slim

ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends wget tar \
    && rm -rf /var/lib/apt/lists/*

# Install MMseqs2 for current arch (amd64: AVX2→SSE4.1; arm64: ARM64)
RUN set -e; \
    if [ "$TARGETARCH" = "amd64" ]; then \
    wget -qO /tmp/mm.tgz https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz || \
    wget -qO /tmp/mm.tgz https://mmseqs.com/latest/mmseqs-linux-sse41.tar.gz; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
    wget -qO /tmp/mm.tgz https://mmseqs.com/latest/mmseqs-linux-arm64.tar.gz; \
    else \
    echo "Unsupported arch: $TARGETARCH" && exit 1; \
    fi; \
    tar -xzf /tmp/mm.tgz -C /opt && rm /tmp/mm.tgz && \
    ln -s /opt/mmseqs*/bin/mmseqs /usr/local/bin/mmseqs

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "consumer.py"]