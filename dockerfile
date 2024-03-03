FROM python:3.12-slim

WORKDIR /usr/src/app

COPY . .

RUN apt-get update && apt-get install -y cron

CMD ["cron", "-f", "-", "--", "0 */12 * * * python /usr/src/app/dyndns.py lexcredendi.cfg"]

RUN echo "0 */12 * * * python /usr/src/app/dyndns.py lexcredendi.cfg" > /etc/cron.d/dyndns