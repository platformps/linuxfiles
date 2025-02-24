FROM ubuntu
# Install SSH server and sudo
RUN apt update && apt install -y openssh-server sudo nano && apt-get clean
RUN mkdir /var/run/sshd
# Install sudo, man, ping, locate, vim, net-tools
RUN apt install sudo -y
RUN apt install man-db -y
RUN apt install iputils-ping -y
RUN apt install locate -y
RUN apt install vim -y
RUN apt install net-tools -y
RUN apt install python3 -y
RUN apt install python-is-python3 -y
RUN yes | unminimize
# Setup the admin user
RUN useradd -rm -d /home/admin -s /bin/bash -g root -G sudo admin && \
    echo 'admin:Learner2024' | chpasswd

# Set working directory
USER admin
WORKDIR /home/admin
# Generate SSH host keys
USER root
RUN mkdir -p /etc/ssh && ssh-keygen -A && \
    chown -R admin /etc/ssh && \
    chmod 700 /etc/ssh

# Update SSH configuration to disable public key authentication and enable password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/PubkeyAuthentication yes/PubkeyAuthentication no/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22
# Copy compute.py script to create cpu and RAM load
COPY compute.py /home/admin/compute.py
# Copy script to generate emails
COPY generate_emails.sh /home/admin/generate_emails.sh
# Start SSH service in foreground
CMD ["/usr/sbin/sshd", "-D"]
