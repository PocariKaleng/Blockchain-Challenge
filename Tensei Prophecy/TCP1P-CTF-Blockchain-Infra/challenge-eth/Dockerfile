FROM dimasmaualana/eth:latest

COPY deploy/ /home/ctf/

COPY contracts /tmp/contracts
COPY foundry.toml /tmp/foundry.toml

RUN true \
    && cd /home/ctf \
    && pip install -r requirements.txt --break-system-packages \
    && cd /tmp \
    && forge build --out /home/ctf/compiled \
    && rm -rf /tmp/contracts /tmp/foundry.toml \
    && true
