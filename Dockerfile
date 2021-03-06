# stage 1 - build APBS and PDB2PQR
FROM ubuntu:18.04 as apbs_pdb2pqr-build
WORKDIR /app
RUN apt update -y \
    && apt install -y python-pip swig cmake g++ make git \
    && git clone https://github.com/Electrostatics/apbs-pdb2pqr.git

COPY docker_materials/build_config.py /app/apbs-pdb2pqr/pdb2pqr/build_config.py

WORKDIR /app/apbs-pdb2pqr/apbs
RUN git submodule init \
    && git submodule update \
    && mkdir /app/apbs_build \
    && cd /app/apbs_build \
    && cmake /app/apbs-pdb2pqr/apbs -DENABLE_PYTHON=ON -DBUILD_SHARED_LIBS=ON \
    && make
# WORKDIR /app/apbs_build
# RUN cmake /app/apbs-pdb2pqr/apbs -DENABLE_PYTHON=ON -DBUILD_SHARED_LIBS=ON \
#     && make

WORKDIR /app/apbs-pdb2pqr/pdb2pqr
RUN python scons/scons.py install
# COPY build_config.py apbs-pdb2pqr/pdb2pqr/build_config.py

# stage 2 - config and deploy Flask app
FROM python:2.7-alpine
WORKDIR /app
COPY . ./
COPY --from=apbs_pdb2pqr-build /app/apbs_build ./apbs_build
COPY --from=apbs_pdb2pqr-build /app/pdb2pqr_build ./pdb2pqr_build
RUN cp  ./src/pdb2pqr_build_materials/main_cgi.py \
        ./src/pdb2pqr_build_materials/querystatus.py \
        ./src/pdb2pqr_build_materials/apbs_cgi.py ./pdb2pqr_build \
    && python -m pip install -r requirements.txt
# RUN export FLASK_APP=server.py
# RUN export FLASK_DEBUG=1
# ENV FLASK_APP=server.py
# ENV FLASK_DEBUG=1
ENV SERVER_HOST="0.0.0.0" \
    SERVER_PORT="5555"

EXPOSE 5555

ENTRYPOINT [ "python" ]
CMD [ "server.py" ]