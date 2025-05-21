import subprocess
# Список модулей Ansible
# Тут указана часть модулей, расписанных выше
# Для экономии места
modules = [
    "ansible.posix.acl",
    "ansible.posix.at",
"ansible.posix.authorized_key",
"ansible.posix.firewalld",
"ansible.posix.firewalld_info",
"ansible.posix.mount",
"ansible.posix.patch",
"ansible.posix.rhel_facts",
"ansible.posix.rhel_rpm_ostree",
"ansible.posix.rpm_ostree_upgrade",
"ansible.posix.seboolean",
"ansible.posix.selinux",
"ansible.posix.synchronize",
"ansible.posix.sysctl" 
]
# Функция для выполнения команды ansible-doc и извлечения информации о REQUIREMENTS
def get_module_requirements(module_name):
    try:
        output = subprocess.check_output(f"ansible-doc {module_name}", shell=True, text=True)
        requirements = "NONE"
        for line in output.split('\n'):
            if line.startswith("REQUIREMENTS:"):
                requirements = line.split(":", 1)[1].strip()
                break
        return requirements
    except subprocess.CalledProcessError:
        return "Error: Module not found or other issue"
# Для каждого модуля выполняем команду ansible-doc и извлекаем информацию о REQUIREMENTS
for module in modules:
    requirements = get_module_requirements(module)
    print(f"{module}: {requirements}")
