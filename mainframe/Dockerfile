FROM ubuntu
# Install SSH server and sudo
RUN apt update && apt install -y openssh-server sudo nano && apt-get clean
RUN mkdir /var/run/sshd
# Install sudo, man, ping, locate, vim, net-tools
RUN apt install sudo -y
RUN apt install iputils-ping -y
RUN apt install vim -y
RUN apt install net-tools -y

# Setup the admin user
RUN useradd -m admin && echo "admin:Learner2024" | chpasswd && usermod -aG sudo admin
USER admin
WORKDIR /home/admin

USER root
RUN mkdir -p /etc/ssh && ssh-keygen -A && \
    chown -R admin /etc/ssh && \
    chmod 700 /etc/ssh

# Generate SSH host keys
USER root
RUN mkdir -p /etc/ssh && ssh-keygen -A && \
    chown -R admin /etc/ssh && \
    chmod 700 /etc/ssh


# Expose Ports port
EXPOSE 22
EXPOSE 3270
EXPOSE 3271
EXPOSE 3272
EXPOSE 3273
EXPOSE 8038
EXPOSE 80
EXPOSE 443
EXPOSE 10000
EXPOSE 20000

#copy tar file
COPY mainframe.tar.gz /home/admin/mainframe.tar.gz
RUN tar -xzvf mainframe.tar.gz
# Start SSH service in foreground
CMD ["/usr/sbin/sshd", "-D"]
