import subprocess

def stop_and_remove_all_containers():
    # Stop all running containers
    subprocess.run("docker stop $(docker ps -q)", shell=True)
    
    # Remove all stopped containers
    subprocess.run("docker rm $(docker ps -aq)", shell=True)

if __name__ == "__main__":
    stop_and_remove_all_containers()
