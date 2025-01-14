import subprocess
import re

def get_docker_container_names():
    try:
        output = subprocess.check_output(["docker", "ps", "-a"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return []

    lines = output.strip().split('\n')
    
    if len(lines) < 2:
        print("No containers found")
        return []
    
    container_names = []
    for line in lines[1:]:
        parts = line.split()
        container_name = parts[-1]
        container_names.append(container_name)
    
    return container_names

def select_container(container_names):
    print("Select a container:")
    for idx, name in enumerate(container_names, start=1):
        print(f"{idx}. {name}")
    
    try:
        choice = int(input("Enter the number of the container: "))
        if 1 <= choice <= len(container_names):
            return container_names[choice - 1]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input.")
        return None

def start_service(container_name):
    command = f'docker exec -d {container_name} bash -c "cd /home/admin/mvs1_10.2_BACKUP_NO_PS && ./mvs"'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Service started in container {container_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start service: {e}")

def stop_service(container_name):
    try:
        hercules_pid = subprocess.check_output(["docker", "exec", "-it", container_name, "pidof", "hercules"], universal_newlines=True).strip()
        if hercules_pid:
            subprocess.run(["docker", "exec", "-it", container_name, "kill", "-TERM", hercules_pid], check=True)
            print("Hercules process stopped.")
        else:
            print("Hercules process not found.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop Hercules process: {e}")

    #try:
     #   mvs_pid = subprocess.check_output(["docker", "exec", "-it", container_name, "pidof", "mvs"], universal_newlines=True).strip()
      #  if mvs_pid:
       #     subprocess.run(["docker", "exec", "-it", container_name, "kill", "-TERM", mvs_pid], check=True)
         #   print("MVS process stopped.")
       # else:
       #     print("MVS process not found.")
   # except subprocess.CalledProcessError as e:
    #    print(f"Failed to stop MVS process: {e}")

def main_menu():
    print("1. Start Service")
    print("2. Stop Service")
    try:
        choice = int(input("Enter your choice: "))
        return choice
    except ValueError:
        print("Invalid input.")
        return None

if __name__ == "__main__":
    container_names = get_docker_container_names()
    if container_names:
        selected_container = select_container(container_names)
        if selected_container:
            choice = main_menu()
            if choice == 1:
                start_service(selected_container)
            elif choice == 2:
                stop_service(selected_container)
            else:
                print("Invalid choice.")
        else:
            print("No valid container selected.")
    else:
        print("No containers available.")

