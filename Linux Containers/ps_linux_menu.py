import os
import subprocess
import re

def import_linux_files():
    os.makedirs("/repository", exist_ok=True)
    os.chdir("/repository")
    files = [
        "https://raw.githubusercontent.com/platformps/linuxfiles/main/Dockerfile",
        "https://raw.githubusercontent.com/platformps/linuxfiles/main/compute.py",
        "https://raw.githubusercontent.com/platformps/linuxfiles/main/generate_emails.sh"
    ]
    for file in files:
        subprocess.run(["wget", file])
    print("Files imported successfully.")

def build_docker_image():
    os.chdir("/repository")
    subprocess.run(["docker", "build", "-t", "ps-linux", "."])
    print("Docker image 'ps-linux' built successfully.")

def list_containers():
    output = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}"], capture_output=True, text=True)
    return output.stdout.strip().split("\n") if output.stdout.strip() else []

def get_running_containers():
    output = subprocess.run(["docker", "ps", "--format", "{{.ID}} {{.Names}} {{.Ports}}"], capture_output=True, text=True)
    return output.stdout.strip().split("\n") if output.stdout.strip() else []

def create_docker_containers():
    existing_containers = list_containers()
    
    core_containers = {
        "instructor": 2250,
        "IA": 2251,
        "Global": 2252,
        "SME": 2253
    }
    
    for name, port in core_containers.items():
        if name not in existing_containers:
            subprocess.run([
                "docker", "run", "-itd", "--restart", "always",
                "--name", name, "-h", name, "-m", "256m", "--memory-swap", "256m",
                "--log-driver", "local", "--log-opt", "max-size=30m", "--log-opt", "max-file=10",
                "--network", "ps-learner-network", "-p", f"{port}:22", "ps-linux"
            ])
            print(f"Container {name} created on port {port}.")
    
    learner_pattern = re.compile(r"learner_(\d+)")
    last_learner_num = 0
    last_port = 2200
    
    for container in existing_containers:
        match = learner_pattern.match(container)
        if match:
            num = int(match.group(1))
            last_learner_num = max(last_learner_num, num)
            last_port = max(last_port, 2200 + num)
    
    learners = int(input("Enter the number of learners in the cohort: "))
    
    for i in range(1, learners + 1):
        learner_num = last_learner_num + i
        port = last_port + i
        subprocess.run([
            "docker", "run", "-itd", "--restart", "always",
            "--name", f"learner_{learner_num}", "-h", f"learner_{learner_num}",
            "-m", "256m", "--memory-swap", "256m",
            "--log-driver", "local", "--log-opt", "max-size=30m", "--log-opt", "max-file=10",
            "--network", "ps-learner-network", "-p", f"{port}:22", "ps-linux"
        ])
        print(f"Container learner_{learner_num} created on port {port}.")

def add_more_containers():
    create_docker_containers()

def show_running_containers():
    running_containers = get_running_containers()
    if running_containers:
        print("CONTAINER ID   NAMES       PORTS")
        print("--------------------------------")
        for container in running_containers:
            parts = container.split()
            container_id = parts[0]
            name = parts[1]
            port = parts[2] if len(parts) > 2 else "N/A"
            print(f"{container_id:<15}{name:<12}{port}")
    else:
        print("No containers are currently running.")

def start_stop_container():
    containers = list_containers()
    if not containers:
        print("No containers available.")
        return
    
    print("Select containers:")
    for idx, name in enumerate(containers, start=1):
        print(f"{idx}. {name}")
    
    choices = input("Enter the container numbers (comma-separated for multiple): ").split(",")
    action = input("Start or Stop the containers? (start/stop): ").strip().lower()
    
    for choice in choices:
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(containers):
                container_name = containers[idx]
                if action == "start":
                    subprocess.run(["docker", "start", container_name])
                    print(f"Container {container_name} started.")
                elif action == "stop":
                    subprocess.run(["docker", "stop", container_name])
                    print(f"Container {container_name} stopped.")

def delete_container():
    containers = list_containers()
    if not containers:
        print("No containers to delete.")
        return
    
    print("Select containers to delete:")
    for idx, name in enumerate(containers, start=1):
        print(f"{idx}. {name}")
    
    choices = input("Enter the container numbers (comma-separated for multiple) : ").split(",")
    
    for choice in choices:
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(containers):
                container_name = containers[idx]
                subprocess.run(["docker", "rm", "-f", container_name])
                print(f"✅ Container {container_name} deleted.")

def main():
    while True:
        RED_BOLD = "\033[1;31m"
        RESET = "\033[0m"

        print(f"""
         ***************************************
         *                                     *
         *    {RED_BOLD}Per Scholas - Linux Containers{RESET}   *
         *                                     *
         ***************************************
         """)
        print("📌 **Menu:**")
        print("1️⃣  📥 Import Linux server files from GitHub")
        print("2️⃣  🏗️ Build PS LINUX Docker Image")
        print("3️⃣  🆕 Create Docker Containers")
        print("4️⃣  ➕ Add More Containers")
        print("5️⃣  📋 Show Running Containers")
        print("6️⃣  🔄 Start / Stop Containers")
        print("7️⃣  🗑️ Delete Containers")
        print("8️⃣  ❌ Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            import_linux_files()
        elif choice == "2":
            build_docker_image()
        elif choice == "3":
            create_docker_containers()
        elif choice == "4":
            add_more_containers()
        elif choice == "5":
            show_running_containers()
        elif choice == "6":
            start_stop_container()
        elif choice == "7":
            delete_container()
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
