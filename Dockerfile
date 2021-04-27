FROM gcr.io/cmg-build-env/cmg-gcc-6.5.0-openmpi-4.0.2-x86_hdf5 as devel

ENV DEBIAN_FRONTEND=noninteractive

ADD ./ /tmp/hopr/

RUN apt-get update -y && \
    apt-get install -y wget git

# BLAS and Lapack
RUN . /etc/profile.d/z10_spack_environment.sh && \
    wget https://github.com/Reference-LAPACK/lapack/archive/v3.9.0.tar.gz --directory-prefix=/tmp/ &&\
    cd /tmp && tar -xvzf v3.9.0.tar.gz && mkdir -p /tmp/lapack-3.9.0/build && \
    cd /tmp/lapack-3.9.0/build && \
    cmake -DCMAKE_INSTALL_PREFIX=/opt/view /tmp/lapack-3.9.0 &&  \
    make && make install &&\
    rm -rf /tmp/lapack-3.9.0

# CGNS
RUN . /etc/profile.d/z10_spack_environment.sh && \
    wget https://github.com/Reference-LAPACK/lapack/archive/v3.9.0.tar.gz --directory-prefix=/tmp/ &&\
    cd /tmp && tar -xvzf v3.9.0.tar.gz && mkdir -p /tmp/lapack-3.9.0/build && \
    cd /tmp/lapack-3.9.0/build && \
    cmake -DCMAKE_INSTALL_PREFIX=/opt/hopr /tmp/lapack-3.9.0 &&  \
    make && make install &&\
    rm -rf /tmp/lapack-3.9.0


#HOPR
RUN . /etc/profile.d/z10_spack_environment.sh && \
    mkdir /tmp/hopr/build && \
    cd /tmp/hopr/build && \
    HDF5_ROOT=/opt/view CGNS_ROOT= cmake -DBUILD_HDF5= -DBUILD_CGNS= -DCMAKE_INSTALL_PREFIX=/opt/view /tmp/hopr &&\
    make && make install &&\
    rm -rf /tmp/hopr

FROM gcr.io/cmg-build-env/cmg-gcc-6.5.0-openmpi-4.0.2-x86_hdf5

COPY --from=devel /opt/ /opt/

