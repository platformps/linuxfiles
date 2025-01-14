import subprocess
import json
import os
import socket
import re

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_next_available_port(starting_port):
    port = starting_port
    while is_port_in_use(port):
        port += 1
    return port
def get_existing_container_indices(cohort_index, port_state_file):
    port_state = load_port_state(port_state_file)
    containers = port_state.get(str(cohort_index), {}).get('containers', {})
    return {int(index): count for index, count in containers.items()}


def update_output_file(output_file, container_info_list):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        container_info_dict = {}
        for line in lines:
            match = re.match(r"(Container 'cohort\d+_container\d+' created with ports: \d+:\d+, \d+:\d+, \d+:\d+, )(\d+) learners", line.strip())
            if match:
                base_info = match.group(1)
                learners = int(match.group(2))
                container_info_dict[base_info] = learners
        
        with open(output_file, 'w') as f:
            for info in container_info_list:
                match = re.match(r"(Container 'cohort\d+_container\d+' created with ports: \d+:\d+, \d+:\d+, \d+:\d+, )(\d+) learners", info)
                if match:
                    base_info = match.group(1)
                    learners = int(match.group(2))
                    if base_info in container_info_dict:
                        container_info_dict[base_info] = learners
                    else:
                        container_info_dict[base_info] = learners
            
            for base_info, learners in container_info_dict.items():
                f.write(f"{base_info}{learners} learners\n")
    else:
        with open(output_file, 'w') as f:
            for info in container_info_list:
                f.write(info + '\n')

def create_docker_containers(learners_per_cohort_list, output_file, port_state_file, cohort_index_start=1):
    last_ports = load_port_state(port_state_file)
    container_info_list = []

    for cohort_index, learners_per_cohort in enumerate(learners_per_cohort_list, start=cohort_index_start):
        if str(cohort_index) not in last_ports:
            last_ports[str(cohort_index)] = {
                'port_3270': 8000, 'port_22': 2200, 'port_8038': 9000, 'containers': {}
            }

        existing_indices = get_existing_container_indices(cohort_index, port_state_file)
        container_index = (max(existing_indices.keys(), default=0) + 1) if existing_indices else 1
        remaining_learners = learners_per_cohort

        # Fill existing containers first
        for index, current_learners in existing_indices.items():
            if current_learners < 7:
                available_slots = 7 - current_learners
                learners_to_add = min(available_slots, remaining_learners)
                existing_indices[index] += learners_to_add
                last_ports[str(cohort_index)]['containers'][str(index)] = existing_indices[index]
                remaining_learners -= learners_to_add
                container_info = f"Container 'cohort{cohort_index}_container{index}' created with ports: {last_ports[str(cohort_index)]['port_3270']}:3270, {last_ports[str(cohort_index)]['port_22']}:22, {last_ports[str(cohort_index)]['port_8038']}:8038, {existing_indices[index]} learners"
                print(container_info)
                container_info_list.append(container_info)
                if remaining_learners <= 0:
                    break

        # Create new containers if there are still remaining learners
        while remaining_learners > 0:
            num_learners = min(7, remaining_learners)
            container_name = f"cohort{cohort_index}_container{container_index}"
            port_3270 = find_next_available_port(last_ports[str(cohort_index)]['port_3270'] + 1)
            port_22 = find_next_available_port(last_ports[str(cohort_index)]['port_22'] + 1)
            port_8038 = find_next_available_port(last_ports[str(cohort_index)]['port_8038'] + 1)

            run_command = [
                "docker", "run", "--restart", "always", "--privileged", "-itd",
                "--name", container_name,
                "--log-driver", "local",
                "--log-opt", "max-size=30m",
                "--log-opt", "max-file=10",
                "--network", "ps-mainframe-network",
                "-p", f"{port_3270}:3270",
                "-p", f"{port_22}:22",
                "-p", f"{port_8038}:8038",
                "mainframe"
            ]
            subprocess.run(run_command)
            container_info = f"Container '{container_name}' created with ports: {port_3270}:3270, {port_22}:22, {port_8038}:8038, {num_learners} learners"
            print(container_info)
            container_info_list.append(container_info)

            remaining_learners -= num_learners
            last_ports[str(cohort_index)]['port_3270'] = port_3270
            last_ports[str(cohort_index)]['port_22'] = port_22
            last_ports[str(cohort_index)]['port_8038'] = port_8038

            existing_indices[container_index] = num_learners
            last_ports[str(cohort_index)]['containers'][str(container_index)] = num_learners
            container_index += 1

    update_output_file(output_file, container_info_list)
    save_port_state(port_state_file, last_ports)

# Rest of the code remains unchanged


def load_port_state(port_state_file):
    if os.path.exists(port_state_file):
        with open(port_state_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_port_state(port_state_file, port_state):
    with open(port_state_file, 'w') as f:
        json.dump(port_state, f, indent=4)


if __name__ == "__main__":
    output_file = "docker_containers_info.txt"
    port_state_file = "port_state.json"

    # ANSI escape codes for color and size
    RED_BOLD = "\033[1;31m"
    RESET = "\033[0m"

    print(f"""
    ***************************************
    *                                     *
    *    {RED_BOLD}Per Scholas - Mainframe{RESET}          *
    *                                     *
    ***************************************
    """)

    print("Menu:")
    print("1. Run the script for the first time")
    print("2. Add new learners to an existing cohort")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        num_cohorts = int(input("Enter the number of cohorts: "))
        learners_per_cohort_list = []

        for i in range(num_cohorts):
            learners = int(input(f"Enter the number of learners for cohort {i + 1}: "))
            learners_per_cohort_list.append(learners)

        create_docker_containers(learners_per_cohort_list, output_file, port_state_file)

    elif choice == '2':
        cohort_index = int(input("Enter the cohort number to add new learners: "))
        new_learners = int(input(f"Enter the number of new learners to add to cohort {cohort_index}: "))
        create_docker_containers([new_learners], output_file, port_state_file, cohort_index_start=cohort_index)

    else:
        print("Invalid choice. Please enter 1 or 2.")

