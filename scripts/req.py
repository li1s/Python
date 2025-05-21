import subprocess

# Список модулей Ansible
modules = [
	"ansible.builtin.add_host",
	"ansible.builtin.apt",
	"ansible.builtin.apt_key",
	"ansible.builtin.apt_repository",
	"ansible.builtin.assemble",
	"ansible.builtin.assert",
	"ansible.builtin.async_status",
	"ansible.builtin.blockinfile",
	"ansible.builtin.command",
	"ansible.builtin.copy",
	"ansible.builtin.cron",
	"ansible.builtin.deb822_repository",
	"ansible.builtin.debconf",
	"ansible.builtin.debug",
	"ansible.builtin.dnf",
	"ansible.builtin.dnf5",
	"ansible.builtin.dpkg_selections",
	"ansible.builtin.expect",
	"ansible.builtin.fail",
	"ansible.builtin.fetch",
	"ansible.builtin.file",
	"ansible.builtin.find",
	"ansible.builtin.gather_facts",
	"ansible.builtin.get_url",
	"ansible.builtin.getent",
	"ansible.builtin.git",
	"ansible.builtin.group",
	"ansible.builtin.group_by",
	"ansible.builtin.hostname",
	"ansible.builtin.import_playbook",
	"ansible.builtin.import_role",
	"ansible.builtin.import_tasks",
	"ansible.builtin.include_role",
	"ansible.builtin.include_tasks",
	"ansible.builtin.include_vars",
	"ansible.builtin.iptables",
	"ansible.builtin.known_hosts",
	"ansible.builtin.lineinfile",
	"ansible.builtin.meta",
	"ansible.builtin.package",
	"ansible.builtin.package_facts",
	"ansible.builtin.pause",
	"ansible.builtin.ping",
	"ansible.builtin.pip",
	"ansible.builtin.raw",
	"ansible.builtin.reboot",
	"ansible.builtin.replace",
	"ansible.builtin.rpm_key",
	"ansible.builtin.script",
	"ansible.builtin.service",
	"ansible.builtin.service_facts",
	"ansible.builtin.set_fact",
	"ansible.builtin.set_stats",
	"ansible.builtin.setup",
	"ansible.builtin.shell",
	"ansible.builtin.slurp",
	"ansible.builtin.subversion",
	"ansible.builtin.systemd",
	"ansible.builtin.systemd_service",
	"ansible.builtin.sysvinit",
	"ansible.builtin.tempfile",
	"ansible.builtin.template",
	"ansible.builtin.unarchive",
	"ansible.builtin.uri",
	"ansible.builtin.user",
	"ansible.builtin.validate_argument_spec",
	"ansible.builtin.wait_for",
	"ansible.builtin.wait_for_connection",
	"ansible.builtin.yum",
	"ansible.builtin.yum_repository"
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

# Создаем и записываем результаты в файл в виде таблицы
with open('req_ans_builtin.txt', 'w') as file:
    file.write("module_name\trequirements\n")  # Заголовки столбцов
    for module in modules:
        requirements = get_module_requirements(module)
        file.write(f"{module}\t{requirements}\n")
