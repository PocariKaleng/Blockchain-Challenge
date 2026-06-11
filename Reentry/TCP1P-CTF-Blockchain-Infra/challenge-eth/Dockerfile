FROM dimasmaualana/eth:latest

COPY deploy/ /home/ctf/

COPY contracts /tmp/contracts

RUN true \
    && cd /home/ctf \
    && pip install -r requirements.txt --break-system-packages \
    && cd /tmp \
    && forge build --root /tmp --contracts /tmp/contracts --out /home/ctf/compiled \
    && rm -rf /tmp/contracts \
    && true
